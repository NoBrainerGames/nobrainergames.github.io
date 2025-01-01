---
layout: post
title: "The firstborn"
categories: engine
comments: true
---

They say there is no prouder moment for a parent than when their child takes the first steps. Behold!

<iframe
    width="641"
    height="360"
    src="https://www.youtube.com/embed/IfNmUDC5Hu8"
    title="First avatar"
    frameborder="0"
    allow="picture-in-picture"
    allowfullscreen>
</iframe>

<sup>First 3D avatar in Nim.</sup>

This scene is the sum of two new modules: (1) the physics engine and (2) an entity component system (ECS). The first module establishes gravity in the scene, allowing the avatar to "fall" to the floor. The second module enables navigation using the mouse.

The physics module wraps AMD's [FEMFX](https://gpuopen.com/femfx/) library which is a newly opensourced project. I considered going with Nvidia's [PhysX](https://www.nvidia.com/en-us/drivers/physx/physx-9-19-0218-driver/) library initially, but after much research I have concluded that I should go with a smaller library that can be easily contributed to if I ever need to add a custom feature.

The ECS implementation -- dubbed [SECS](https://github.com/n0bra1n3r/secs) for Simple ECS -- was inspired by skypjack's amazing [series on ECS](https://skypjack.github.io/2019-02-14-ecs-baf-part-1/). I have made the decision to create a pure Nim implementation instead of wrapping his library to better take advantage of Nim's language features.

It was during the development of SECS that I conceptualized the engine's "implicit event system". The idea is that user-defined systems should be able to notify each other of mutations to components without explicitly invoking any callback functions.

To illustrate, take two systems defined in the files `inputs.nim` and `players.nim`. An "event" in this context is the mutation of a component handled by a system, e.g. a `Position` component handled by the `inputs` system. This event can be seen by another system that also handles the `Position` component -- e.g. the `players` system -- simply by defining a callback `onMutate` with a `Position` parameter.

```nim
# inputs.nim: system of inputs
proc onUpdate() =
  inputEntity.position = canvas.get3DMouseCoords() # get mouse coordinates
```

```nim
# players.nim: system of players
proc onMutate(position) = # automatically called from 'inputs.nim'
  playerEntity.position = position # move player to new location
```

The implementation of ECS in the engine will hopefully allow me to scale its functionality by enabling loose coupling between subsystems such as physics and rendering.

It seems that all that's needed from this point on is to implement the other core subsystems of the engine...
