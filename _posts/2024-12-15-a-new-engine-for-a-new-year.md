---
layout: post
title: "A new engine for a new year!"
categories: engine
comments: true
---

* TOC
{:toc}

## What is Reboot Engine?
Reboot Engine is what will power No Brainer Games' first indie game. It is a 3D game engine under development that strives to help indie developers (just me) deliver action role-playing games (my games) to VR.

It is the result of four years and counting of learnings about compilers, editors, debuggers, API design, rendering, algorithms, optimization, and -- frankly speaking -- grit. This post outlines the journey of how I went from clueless to a demo with my own engine. Although this is not a tutorial and the engine itself is nowhere near complete, sprinkled within are references to resources that other budding game engine programmers may find useful in their own journey.

As I continue through this journey, I plan to create more posts and open-source parts of the engine to contribute back to the communities that have guided me.

## Why another game engine?
Reboot Engine was conceived as an ambitious learning project in 2020 to up-skill in game engine development. As I gained knowledge and explored existing technologies, the engine became a conduit to innovate in aspects of my VR experiences that I found important:
- environment traversal with emphasis on reducing VR sickness
- 3D user interfaces for VR games
- context-aware 3D gestures and voice commands
- 3D audio queues paired with controller haptics

Eventhough these problem domains can be tackled using existing game engines, I felt that the insight and confidence gained from implementing one myself would help in coming up with new and novel solutions.

Apart from this, much work was put into making my customized game development experience simple and enjoyable. For example, implementing the engine in the [Nim programming language](https://nim-lang.org/) has allowed me to write everything from the build system to the shader code in one language. An effect of this is that context switching during prototyping is significantly reduced, speeding up my research-ideation-development pipeline.

## Which platforms does it work on?
Currently Meta Quest 3S is the primary platform, and is regularly tested on Mac OS X Sonoma and Windows 11 version 24H2.

## How does it work?
The following diagram is an overview of the implemented features of the engine, organised to show that each feature depends on the ones below it:

![Reboot diagram]({{ "assets/reboot-diagram.png" | relative_url }})

The engine is a collection of dynamic libraries that are loaded into the main application by the module loader. The [game loop](https://www.gafferongames.com/post/fix_your_timestep/) pumps events through these modules and the system interface, which exposes the five core features of the engine.

This type of organization has added some complexity in comparison to a monolithic one, but I have enjoyed some of its nice properties:
- enables hot reloading which allows rapid feedback when making code changes
- enforces modular design which in turn eases addition or removal of features
- easier debugging and testing since modules can be readily isolated
- easier parallelization as each module is a complete unit of functionality

The diagram also shows planned features that are still unimplemented. In the following sections I will discuss the already implemented core features.

### Render engine
The render engine is implemented using the [Diligent Engine core module](https://github.com/DiligentGraphics/DiligentCore), which treats OpenGL, DirectX, Vulkan, Metal, and WebGPU as rendering backends and provides a single low-level DirectX-based interface.

Currently my render engine uses the Vulkan backend exclusively, taking advantage of instancing, indirect rendering, and bindless resources to achieve consistent 120 FPS with 32k+ rendered objects on an Apple M2 Pro machine. I found [vkguide.dev](https://vkguide.dev/docs/gpudriven/draw_indirect), the [Vulkan docs](https://github.com/KhronosGroup/Vulkan-Samples/tree/main/samples/performance/multi_draw_indirect), and the [Diligent tutorials](https://github.com/DiligentGraphics/DiligentSamples/blob/master/Tutorials/Tutorial16_BindlessResources/readme.md) to be extremely helpful as references for these optimizations.

The render engine exposes a simple builder interface to describe graphics and compute pipelines with less verbosity than Diligent Engine itself, while still providing direct access to Diligent's API.

It is also closely tied to the shader interface which it uses to set up shader resources to use at run-time.

### Shader interface
The shader interface converts my Nim shader dialect to HLSL at compile-time, which is later converted by Diligent to SPIRV at run-time. The initial implementation was a wrapper for the [ShaderWriter](https://github.com/DragonJoker/ShaderWriter) C++ library, but it was later rewritten to a pure Nim parser. This feature allows for some nifty capabilities:
- automated unit tests can be written and run on CPU
- some debugging can be done on CPU with breakpoints and logging
- HLSL constructs can be augmented with Nim's powerful metaprogramming
- strict type checking is done at design-time instead of run-time

Shader code structure and the naming of constructs closely follow that of HLSL, augmented with some functionality such as the following:
1. Type information of all macros, buffers, textures, and shader inputs can be accessed at compile-time. This information is used by the render engine to create resources for the shaders to use at run-time.
2. A single buffer type called `GenericBuffer` can be used to store any type of shader data. The members of `struct` elements can be accessed and mutated similarly to `StructuredBuffer`, but it actually lowers to a `ByteAddressBuffer` or `RWByteAddressBuffer` depending on usage within the shader.

#### Rendering and animation shaders
These form a graphics pipeline that renders static and animated skeletal meshes. Ideas on animated crowd rendering were taken from [GPU Gems 3 ch. 2](https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-2-animated-crowd-rendering).

Per-instance mesh transforms and textures are passed to the shaders via an SSBO and rendered using instanced rendering.

Skeletal animation is done by indexing into another SSBO containing pre-calculated transform matrices of all bones in all frames of all animations. This index is computed from a combination of the current game time, the instance ID, and the animation index. The calculation of the transform matrices is done CPU-side by the [scene builder](#scene-builder).

This pipeline is dispatched with 1 `vkCmdDrawIndexIndirect` call per frame.

#### Physics shaders
This is a set of graphics and compute pipelines implementing [GPU Gems 3 ch. 29](https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-29-real-time-rigid-body-simulation-gpus). This chapter of the book describes a method to efficiently simulate many rigid bodies by performing calculations on their particle representations.

The particle representations are generated once per object prior to simulation with the following steps:
1. Render the front, back, right, left, bottom and top of the object onto a render target.
2. Group all filled pixels into cells of a 3D grid with positions relative to the center of mass and store them in an SSBO. These cells represent the particles that are used in collision detection and force calculations.
3. Store the offset and count of the particle data computed in the current pipeline dispatch set in another SSBO. This represents the rigid body that is used in the linear and angular momentum calculations.

I used instancing and the `VkPhysicalDeviceFeatures::fragmentStoresAndAtomics` feature to perform this voxelization pass in 1 draw call and 1 compute shader dispatch.

Per-frame physics simulation is done in the following steps:
1. Perform collision detection using spatial hashing on each particle.
2. Compute gravitational and collision forces on each particle.
3. Transform the objects using the calculated linear and angular momentums.
4. Re-run the simulation a few more times to stabilize floating point values.

Physics simulations average 27 compute shader dispatches per frame on my machine.

#### Picker shaders
These form a graphics pipeline used to detect objects under the mouse cursor for object picking.

This pipeline renders all objects to a render target with a `VK_FORMAT_R32_UINT` format, with the color channel set to the instance ID of each rendered object. The render target is later sampled at the texture coordinates corresponding to the clip space coordinates of the mouse to retrieve the currently selected instance ID.

This pipeline is dispatched once per frame.

#### Optimization shaders
These are an assortment of lightweight compute pipelines for initializing or modifying data in the various SSBOs used by the other pipelines.

They are either dispatched once per frame or only when user input causes a change to the rendered scene.

### ECS framework
The custom ECS framework was one of the first features I implemented. The framework is based on [skypjack's ECS articles](https://skypjack.github.io/2019-03-07-ecs-baf-part-2) on sparse-set-based ECS, and powers the engine's event propagation mechanism.

The framework makes heavy use of arrays that serve as lookup tables for entities and components. Entities are simply indices into an array containing bit fields that represent a unique set of components. The component data is stored in different arrays corresponding to component types. This arrangement allows for fast iteration and comparison when querying for entities with a given combination of components.

Automatic memory management is done through a separate array holding function pointers that implement deletion and memory deallocation for each component type. These functions are invoked explicitly when deleting components and automatically by Nim's automatic reference counting system.

The ECS framework was designed to work across DLL boundaries in order to support the engine's modular layout. It does this by keeping its state and component identifiers in its own dynamically loaded modules. The component identifiers are generated at compile-time using Nim's metaprogramming features and are loaded through exported functions at run-time.

All functionality is exposed in a simple API grouped into the following operations:
1. entity insertion and deletion
2. component insertion and deletion
3. per-component change detection
4. per-entity component querying

The following is an example of a component query:
```nim
# iterate through all entities containing viewport, button input, and cursor input components
for entity, (viewport, buttonInput, cursorInput) in query(Viewport, ButtonInput, CursorInput):
  if entity.hasChanged(Viewport):
    # the viewport component has changed since the last frame
    resizeViewport(viewport.width, viewport.height)

  if entity.isChanged:
    # one of the components has changed since the last frame
    updateCamera(buttonInput.keys, cursorInput.xy)
```

### Scene builder
The scene builder loads mesh, texture, and animation data into arrays that are later directly uploaded to the GPU as buffer data. This module implements APIs to load default shapes, as well as GLTF assets using the [cgltf](https://github.com/jkuhlmann/cgltf) library.

The scene builder loads the following GLTF asset types:
- albedo map textures and texture coordinates
- index and vertex data
- skeletal animations

 When loading skeletal animations, transforms of every bone are pre-computed for every frame. This eliminates the need to upload animation data every frame during rendering, allowing for animation of a large number of objects at the cost of increased loading times and memory.

## Upcoming work
There is still lots to do before a playable game can be made, and even more before a game can be released. Priorities for the medium term are:
1. UI framework using the [Nuklear](https://github.com/Immediate-Mode-UI/Nuklear) library
2. sound engine using the [SoLoud](https://solhsa.com/soloud/) C++ library
3. lighting and shadows
4. trigger volumes
5. constraint-based collision response similar to [Nvidia Flex](https://gameworksdocs.nvidia.com/FleX/1.2/lib_docs/manual.html)

Stay tuned for updates!

## External references
1. [Nim programming language](https://nim-lang.org/)
2. [Fix your timestep!](https://www.gafferongames.com/post/fix_your_timestep/)
3. [Diligent Engine core module repository](https://github.com/DiligentGraphics/DiligentCore)
4. [draw indirect section in vkguide.dev](https://vkguide.dev/docs/gpudriven/draw_indirect)
5. [Vulkan docs on multi-draw indirect rendering](https://github.com/KhronosGroup/Vulkan-Samples/tree/main/samples/performance/multi_draw_indirect)
6. [Diligent tutorial on bindless resources](https://github.com/DiligentGraphics/DiligentSamples/blob/master/Tutorials/Tutorial16_BindlessResources/readme.md)
7. [ShaderWriter C++ library](https://github.com/DragonJoker/ShaderWriter)
8. [GPU Gems 3 - Animated Crowd Rendering](https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-2-animated-crowd-rendering)
9. [GPU Gems 3 - Real-Time Rigid Body Simulation and GPUs](https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-29-real-time-rigid-body-simulation-gpus)
10. [ECS Back and Forth - Where are my entities?](https://skypjack.github.io/2019-03-07-ecs-baf-part-2)
11. [cgltf library](https://github.com/jkuhlmann/cgltf)
12. [Nuklear library](https://github.com/Immediate-Mode-UI/Nuklear)
13. [SoLoud library](https://solhsa.com/soloud/)
14. [Nvidia Flex](https://gameworksdocs.nvidia.com/FleX/1.2/lib_docs/manual.html)
