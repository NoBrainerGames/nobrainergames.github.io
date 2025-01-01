---
layout: post
title: "Moving forward"
categories: engine
comments: true
---

In my [previous post](./2024-12-15-a-new-engine-for-a-new-year.md#physics-shaders), I talked a little about the physics shaders in Reboot Engine. In this post I talk about a related problem I worked on recently and how I solved it.

I mentioned that the physics solver still has issues around stability and tunneling. But there is another problem that manifests consistently and is quite obvious: the voxelization shader induces noticeable lag each time it is dispatched. Based on my profiling using the [Xcode metal debugger](https://developer.apple.com/documentation/xcode/metal-debugger/), dispatching this shader causes a drop of up to 20 FPS! 😱

This is very bad news for a VR-focused engine.

The voxelization shader is responsible for generating the particles that make up a rigid body, and is invoked once for every object that is instantiated. Conceptually, it works in two phases by (1) projecting the surface of the object onto the smallest cube that encloses the object, and then (2) taking the cells of that cube that intersect with the surface of the object as the particles. Pseudocode for a non-parallelized version of this could be something like:

```
given instance I with origin at <X, Y, Z>
given a 2D texture T with dimensions SxS
given a 3D array G with dimensions SxSxS containing boolean flags
given a 2D array P with dimensions MxN containing particle locations

for each vector in <-1, 0, 0>, <+1, 0, 0>, <0, -1, 0>, <0, +1, 0>, <0, 0, -1>, <0, 0, +1>:
  render vertices of I whose normals have components parallel to vector onto T
  for each pixel in T at index <u, v> with depth d:
    if pixel is not black:
      toggle flag in G at index <u, v, d> to true

for each flag in G at index <u, v, d>:
  if flag is true:
    set i to count of values in first dimension of P where i < M
    set j to count of values in second dimension of P where j < N
    set value in P at <i, j> to <<u, v, d> + (1 - S) * 0.5>
```

When I dug in to improve the performance of this shader, I tried using a humanoid model instead of the usual default cube. I quickly noticed that in a free-fall the rigid body was consistently rotating to an upside-down position before hitting the ground... 😱😱

Forget the 20 FPS drop, this new issue took the cake as the most glaring bug.

It's glaring because the center of mass (CoM) of real humanoid shapes with uniform density is usually around the torso. Since torques in the engine act on the particles of rigid bodies, this implied that the particle locations were incorrectly offset.

It turned out that in the first phase of the algorithm, models are rendered relative to the *origin* which may be different from the CoM. In this case the origin was at the foot of the model, and the particle locations were relative to this point.

My first thought was to simply apply the difference between the origin and the CoM to particle positions in the physics solvers. Easy right? Well, the next link in this chain of problems was how to get the CoM in the first place.

The obvious way is to (1) accumulate the sum of all particle grid coordinates and (2) divide the sum by the number of particles. Since the grid coordinates are computed on GPU, this means that the CoM calculation should also be done there:

```nim
# Nim shader module

type CIn = object
  dispatchThreadID {.svDispatchThreadID.}: UInt3

# buffers populated by implementation of pseudocode above
var particleGridCoords*: GenericBuffer[Float3]
var particleCount*: SingleBuffer[UInt]

# buffer to store CoM and use in physics solver
var centerOfMass*: SingleBuffer[Float3]

# runs in `particleCount` parallel threads
proc accumulatePositionSum(cIn: CIn) {.computeShader.} = # (1)
  let particleIndex = cIn.dispatchThreadID.x
  if particleIndex < particleCount.load():
    discard # implement equivalent of centerOfMass += particleGridCoords[particleIndex]

proc divideByParticleCount(cIn: CIn) {.computeShader.} = # (2)
  centerOfMass.store(centerOfMass.load() / Float(particleCount))
```

But the issue here is that the accumulation operation in `accumulatePositionSum` must be done atomically as opposed to separate `load`, `increment`, and `store` operations. This is because the shader is executed in parallel threads, which means that the order of operations on `centerOfMass` is indeterminate. Fortunately the [`interlockedAdd`](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/interlockedadd) intrinsic can be used for this purpose, so the implementation would be:

```nim
# ...
    let particleGridCoord = particleGridCoords[particleIndex].load()
    # `interlockedAdd` on supports incrementing `uint` scalars
    centerOfMass[0].interlockedAdd(particleGridCoord.x)
    centerOfMass[1].interlockedAdd(particleGridCoord.y)
    centerOfMass[2].interlockedAdd(particleGridCoord.z)
```

And then offset particle locations in the physics solvers by `conterOfMass`. Problem solved! Stay tuned for my solution to the original performance problem... 😅
