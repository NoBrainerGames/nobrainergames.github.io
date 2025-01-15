---
layout: post
title: "A new engine for a new year!"
categories: engine
comments: true
---

* TOC
{:toc}

## What is Reboot Engine?
Reboot Engine is what will power No Brainer Games' upcoming indie game. It is a 3D game engine under development that strives to help indie developers (just me) deliver action role-playing games (my one game) to VR.

It is the result of four years and counting of learnings about compilers, editors, debuggers, API design, rendering, algorithms, optimization, and -- frankly speaking -- grit. This post outlines the journey of how I went from clueless to a demo of my own engine. Although this post is not a tutorial and the engine itself is nowhere near complete, sprinkled within are references to resources that other budding game engine programmers may find useful in their own journey.

As I continue through this journey, I plan to create more posts and open-source parts of the engine to contribute back to the communities that have guided me.

## Why another game engine?
Reboot Engine was conceived as an ambitious learning project in 2020 to up-skill in game engine development. As I gained knowledge and explored existing technologies, I began to see it as a conduit to innovate in aspects of my VR experiences that I found important:
- environment traversal with emphasis on reducing VR sickness
- 3D user interfaces for VR games
- context-aware 3D gestures and voice commands
- 3D audio queues paired with controller haptics

Eventhough the problem domains here can be tackled using existing game engines, I believe that the insight and confidence gained from implementing one myself will help in coming up with new and novel solutions.

Feature-wise, there is an emphasis on making the engine particulary good at simulating many objects simultaneously. I believe that keeping the engine singularly focused on this capability as opposed to mainstream features like realistic graphics will help me create the kind of games that I envision for VR.

Lastly, much importance is given to creating an ideal game development experience that I have not found in other engines. A result of this thought process is my implementation of the engine in the [Nim programming language](https://nim-lang.org/), which has allowed me the pleasure of writing everything from the build system to the [shader code](#shader-interface) in a single simple language. There are also ideas around VR-centric AI-powered development workflows that I am exploring and will make core to the engine.

## Which platforms does it work on?
It is regularly tested on Mac OS X Sonoma and Windows 11 version 24H2, with the intention of targetting Meta Quest 3S in the near future. In case you're curious, I have been using neovim exclusively to write the engine and it has been a pleasure. If you're a neovim fan you might find some (very) hidden gems in my [dotfiles](https://github.com/n0bra1n3r/dotfiles).

## How does it work?
The following diagram is an overview of the implemented and planned features of the engine, organised to show that each feature depends on the ones below it:

![Reboot diagram]({{ "assets/reboot-diagram.png" | relative_url }})

The engine is a collection of dynamic libraries that are loaded into the main application by the module loader. The [game loop](https://www.gafferongames.com/post/fix_your_timestep/) pumps events through these modules and the system interface, which exposes the five core features of the engine.

This organization has added complexity in comparison to a monolithic one, but I have already been enjoying some of its nice properties:
- enables hot reloading which facilitates rapid feedback when making code changes
- enforces modular design which in turn eases addition or removal of features
- easier debugging and testing since modules can be readily isolated
- easier parallelization as each module is a complete unit of functionality

The diagram also shows planned features that are still unimplemented. In the following sections I will discuss the already implemented core features.

### Render engine
The render engine is implemented using the [Diligent Engine core module](https://github.com/DiligentGraphics/DiligentCore), which treats OpenGL, DirectX, Vulkan, Metal, and WebGPU as rendering backends and provides a single low-level DirectX-based interface.

Figuring out how to get Diligent Engine to work with Nim was one of the first major milestones for the project. Diligent's straightforward API and excellent documentation was a massive help to easing the steep learning curve in graphics programming for me.

Currently my render engine uses the Vulkan backend exclusively, taking advantage of instancing, indirect rendering, and bindless resources to achieve consistent 120 FPS with 32k+ rendered objects on an Apple M2 Pro machine. I found [vkguide.dev](https://vkguide.dev/docs/gpudriven/draw_indirect), the [Vulkan docs](https://github.com/KhronosGroup/Vulkan-Samples/tree/main/samples/performance/multi_draw_indirect), and the [Diligent tutorials](https://github.com/DiligentGraphics/DiligentSamples/blob/master/Tutorials/Tutorial16_BindlessResources/readme.md) to be extremely helpful as references for these optimizations.

The render engine exposes a simple builder interface to describe graphics and compute pipelines with less verbosity than Diligent Engine itself, while still providing direct access to Diligent's API.

It is also closely tied to the shader interface which it uses to set up shader resources to use at run-time.

### Shader interface
Much of my apprehension with creating a game engine came from my inexperience in complex shaders and working with the GPU. The creation of the shader interface guided me through a path of learning that built up my confidence and allowed me to implement many of the engine's current features.

The shader interface converts my Nim shader dialect to HLSL at compile-time, which is later converted by Diligent to SPIRV at run-time. The initial implementation was a wrapper for the [ShaderWriter](https://github.com/DragonJoker/ShaderWriter) C++ library, but it was later rewritten as a pure Nim AST parser. This feature allows for some nifty capabilities:
- automated unit tests can be written and run on CPU
- some debugging can be done on CPU with breakpoints and logging
- HLSL constructs can be augmented with Nim's powerful metaprogramming
- strict type checking is done at compile-time instead of at run-time

Shader code structure and the naming of constructs closely follow that of HLSL, augmented with some functionality such as the following:
1. Type information of all macros, buffers, textures, and shader inputs can be accessed at compile-time. This information is used by the render engine to create resources for the shaders to use at run-time.
2. An additional buffer type called `GenericBuffer` can be used to store any type of shader data. The members of `struct` elements can be accessed and mutated similarly to `StructuredBuffer`, but it actually lowers to a `ByteAddressBuffer` or `RWByteAddressBuffer` depending on usage within the shader.

The following is an example of a shader module:
```nim
# shaders/pickercolors.nim

import ./types

type
  VSIn = object
    vertex: Vertex
    instanceID {.svInstanceID.}: UInt

  VSOut = object
    pos {.svPosition.}: Float4
    instanceColor: UInt

  PSIn = object
    pos {.svPosition.}: Float4
    instanceColor: UInt

  PSOut = object
    color {.svTarget.}: UInt

var worldState*: SingleBuffer[WorldState]
var instances*: GenericBuffer[Instance]

proc vtx*(vsIn: VSIn, vsOut: out VSOut) {.vertexShader.} =
  let transform = instances[vsIn.instanceID].transform.load()
  let position = float4(vsIn.vertex.pos, 1) ** transform

  vsOut = VSOut()
  vsOut.pos = position ** worldState.viewProjection.load()
  vsOut.instanceColor = instanceID

proc pix*(psIn: PSIn, psOut: out PSOut) {.pixelShader.} =
  psOut = PSOut()
  psOut.color = psIn.instanceColor
```

The following is the code for initializing a graphics pipeline:
```nim
import ./shaders/pickercolors

proc createPickerPipelines(self: Game) =
  # get Vulkan swap chain configuration
  let swapChainDesc = getSwapChainDesc()

  # load shader metadata from the `pickercolors` module
  let pickerColorsPix = getShader(pickercolors.pix)
  let pickerColorsVtx = getShader(pickercolors.vtx)

  # create a pipeline using the shader metadata
  self.pickerColors = makePipeline(pickerColorsVtx, pickerColorsPix)
  # customize render target and depth buffer configuration using Diligent Engine
  self.pickerColors.pushRenderTarget:
    it.Width = swapChainDesc.Width
    it.Height = swapChainDesc.Height
    it.Format = TEXTURE_FORMAT(TEX_FORMAT_R32_UINT)
  self.pickerColors.putDepthStencil:
    it.Format = TEXTURE_FORMAT(TEX_FORMAT_D32_FLOAT)
  # specify resource buffers that will be used by the shader
  self.pickerColors.setStaticVar(pickerColorsVtx.buffers.worldState, self.worldState)
  self.pickerColors.setStaticVar(pickerColorsVtx.buffers.instances, self.instances)
  # set buffer containing rendering commands
  self.pickerColors.setDrawCommandBuffer(self.pickerCommands)
```

And the following is the code for rendering:
```nim
proc renderPicker(self: Game) =
  self.pickerColors.prepareForRendering()
  self.pickerColors.clearRenderTarget()
  self.pickerColors.clearDepth()
  self.pickerColors.render()
```

#### Rendering and animation shaders
These form a graphics pipeline that renders static and animated skeletal meshes. Ideas on animated crowd rendering were taken from [GPU Gems 3 ch. 2](https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-2-animated-crowd-rendering).

Per-instance vertex transforms and textures are passed to the shaders via an SSBO and rendered using instanced rendering.

Skeletal animation is done by indexing into another SSBO containing pre-calculated transform matrices of all bones in all frames of all animations. This index is computed from a combination of the current game time, the instance ID, and the animation index. The calculation of the transform matrices is done CPU-side by the [scene builder](#scene-builder).

This pipeline is dispatched in 1 `vkCmdDrawIndexIndirect` call per frame.

#### Physics shaders
This is a set of graphics and compute pipelines implementing [GPU Gems 3 ch. 29](https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-29-real-time-rigid-body-simulation-gpus). This chapter of the book describes a method to efficiently simulate many rigid bodies by performing calculations on their particle representations. After many weeks of trying out different implementations I ended up with a very fast physics solver, but there are still many problems to solve around determinism and tunneling.

The particle representations are generated once per object prior to simulation with the following steps:
1. Render the front, back, right, left, bottom and top of the object onto a render target.
2. Group all filled pixels into cells of a 3D grid with positions relative to the center of mass and store these positions in an SSBO. These positions represent the particles that are used in collision detection and force calculations.
3. Store the information required to fetch the particle data computed in the current pipeline dispatch set in another SSBO. This represents the rigid body that is used in the linear and angular momentum calculations.

I used instancing and the `VkPhysicalDeviceFeatures::fragmentStoresAndAtomics` feature to perform this voxelization pass in 1 draw call and 2 compute shader dispatches.

Physics simulation is done in the following steps:
1. Perform collision detection using spatial hashing on each particle.
2. Compute gravitational and collision forces on each particle.
3. Transform the objects using the calculated linear and angular momentums.
4. Re-run the simulation a few more times to stabilize floating point values.

This averages 27 compute shader dispatches per frame and can handle 98k+ simultaneous collisions while maintaining 120 FPS on an Apple M2 Pro machine.

#### Picker shaders
These form a graphics pipeline used to detect objects under the mouse cursor for object picking.

This pipeline renders all objects to a render target with a `VK_FORMAT_R32_UINT` format, with the color channel set to the instance ID of each rendered object. The render target is later sampled at the texture coordinates corresponding to the clip space coordinates of the mouse to retrieve the currently selected instance ID.

This pipeline is dispatched once per frame.

#### Optimization shaders
These are an assortment of lightweight compute pipelines for initializing or modifying data in the various SSBOs used by the other pipelines.

They are either dispatched once per frame or only when user input causes a change to the rendered scene.

### ECS framework
The custom ECS framework was one of the first features I implemented, and I spent quite some time poring over optimization techniques in this area. The framework is based on skypjack's enlightening [ECS articles](https://skypjack.github.io/2019-03-07-ecs-baf-part-2) on sparse-set-based ECS, and powers the engine's event propagation mechanism.

The framework makes heavy use of arrays that serve as lookup tables for entities and components. Entities are simply indices into an array containing bit fields that represent a unique set of components. The component data is stored in different arrays corresponding to component types. This arrangement allows for fast iteration and comparison when querying for entities with a given combination of components.

Automatic memory management is done through a separate array holding function pointers that implement deletion and memory deallocation for each component type. These functions are invoked explicitly when deleting components and automatically by Nim's automatic reference counting system.

The ECS framework was designed to work across DLL boundaries in order to support the engine's modular layout. It does this by keeping its state and component identifiers in its own dynamically loaded modules. The component identifiers are generated at compile-time using Nim's metaprogramming features and are loaded through exported functions at run-time.

All functionality is exposed in a simple API grouped into the following operations:
1. entity insertion and deletion
2. component insertion and deletion
3. per-component change detection
4. per-entity component querying

The following is an example of an ECS query:
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

The scene builder currently loads the following GLTF data:
- albedo map textures and texture coordinates
- index and vertex data
- skeletal animations

 When loading skeletal animations, transforms of every bone are pre-computed for every frame. This eliminates the need to upload animation data every frame prior to rendering, allowing for animation of a large number of objects at the cost of increased loading times and memory.

 I found loading skeletal animations from GLTF quite challenging to understand and get right. There are certain GLTF files that do not load properly in the engine, so I obviously still have not understood everything about it. Fortunately the placeholder assets I use from [meshy.ai](https://www.meshy.ai/) are loaded properly, so I can put off fixing this until I need to.

### C/C++ interop interfaces
Many nights were spent searching for an efficient way to integrate C and C++ libraries into the Nim codebase. The interop interfaces have been key to speeding up development since PMunch's [futhark](https://github.com/PMunch/futhark) library was released. This library allows me to run a single command to generate the Nim interfaces of all the C libraries that are used by the engine. It works by using libclang to reliably convert C header ASTs to Nim types.

To integrate pure C++ libraries, I use my own [cinterop](https://github.com/n0bra1n3r/cinterop) library. This library allows me to write Nim code that interops with C++ at the source level using metaprogramming, and leans quite heavily on Nim's syntactical similarities to C++. This approach has some issues such as reliance on the underlying C++ compiler for debugging types when interacting with complex C++ features like templates.

## Upcoming work
There is still lots to do and learn before a playable game can be made, and even more before a game can be released. Priorities for the next year are:
1. [OpenXR](https://www.khronos.org/OpenXR/) integration
    - The next series of milestones revolve around VR and creating the development workflow for it.
2. UI framework using the [Nuklear](https://github.com/Immediate-Mode-UI/Nuklear) library
    - I am in urgent need of tools for debugging and a way to display text. I am leaning towards simple bring-your-own-graphics-backend libraries, and Nuklear seems to be one of the more popular ones.
3. sound engine using the [SoLoud](https://solhsa.com/soloud/) C++ library
    - I have not looked much into audio yet, but there is no game if there is no sound. I will need something that can support 3D sound for the type of game I am making.
4. lighting and shadows
    - Research and planning here is required to come up with something that fits the engine's goals. Since graphics fidelity is not the focus, fast and simple lighting and shadow mapping techniques are preferred.
5. particle system
    - The existing shader interface will be extended to support simple particle effects such as fire and smoke.
6. animation blending (stretch goal)
    - This may be a challenge given how animations are currently pre-computed and driven by the GPU. I think that fluid-looking animations are especially important in VR to avoid breaking immersion, so a lot of research will be poured into this.
7. constraint-based collision response similar to [Nvidia Flex](https://gameworksdocs.nvidia.com/FleX/1.2/lib_docs/manual.html) (stretch goal)
    - The current physics implementation has some limitations around stability and realism. Lots of experimentation and profiling needs to be done to balance performance and accuracy in this aspect.

I know that each item in this list is a difficult challenge, but I remain excited to find out if and how I can overcome them. Stay tuned for updates!

## External references
1. [Nim programming language](https://nim-lang.org/)
2. [my dotfiles](https://github.com/n0bra1n3r/dotfiles)
3. [Fix your timestep!](https://www.gafferongames.com/post/fix_your_timestep/)
4. [Diligent Engine core C++ library](https://github.com/DiligentGraphics/DiligentCore)
5. [draw indirect section in vkguide.dev](https://vkguide.dev/docs/gpudriven/draw_indirect)
6. [Vulkan docs on multi-draw indirect rendering](https://github.com/KhronosGroup/Vulkan-Samples/tree/main/samples/performance/multi_draw_indirect)
7. [Diligent tutorial on bindless resources](https://github.com/DiligentGraphics/DiligentSamples/blob/master/Tutorials/Tutorial16_BindlessResources/readme.md)
8. [ShaderWriter C++ library](https://github.com/DragonJoker/ShaderWriter)
9. [GPU Gems 3 - Animated Crowd Rendering](https://developer.nvidia.com/gpugems/gpugems3/part-i-geometry/chapter-2-animated-crowd-rendering)
10. [GPU Gems 3 - Real-Time Rigid Body Simulation and GPUs](https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-29-real-time-rigid-body-simulation-gpus)
11. [ECS Back and Forth - Where are my entities?](https://skypjack.github.io/2019-03-07-ecs-baf-part-2)
12. [cgltf C library](https://github.com/jkuhlmann/cgltf)
13. [futhark Nim library](https://github.com/PMunch/futhark)
14. [meshy.ai](https://www.meshy.ai/)
15. [cinterop Nim library](https://github.com/n0bra1n3r/cinterop)
16. [OpenXR C library](https://www.khronos.org/OpenXR/)
17. [Nuklear C library](https://github.com/Immediate-Mode-UI/Nuklear)
18. [SoLoud C++ library](https://solhsa.com/soloud/)
19. [Nvidia Flex](https://gameworksdocs.nvidia.com/FleX/1.2/lib_docs/manual.html)
