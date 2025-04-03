---
layout: post
title: "Shady physics"
categories: engine
comments: true
---

I'm running late on these posts. I've been quite busy trying to catch up on tech debt while implementing demos at 1 kLoC per second.

That's not an excuse though. I know I said the next post would be about threads, but I decided to dive back a bit into the GPU stuff. I got burnt out by the flurry of AI features I had to implement for expos and such.

So today I'll be talking a bit about an issue I faced with [physics on the GPU](./2024-12-15-a-new-engine-for-a-new-year.md#physics-shaders). A [previous post](./2024-01-01-moving-forward) was about the voxelization shaders, which is a set of shaders executed once per instantiation of a rigid body. The physics shaders on the other hand use the output of those shaders to compute object collisions about 30 times per frame. These are fast enough to compute almost 100k simultaneous collision reactions at 120 FPS on my outdated Macbook.

Impressive right? Not really. Technically speaking, this is crappy performance compared to what some [other physics systems](https://www.perplexity.ai/page/genesis-world-s-fastest-physic-2_AOTm8gQZ2edfo0ywBX4A) can achieve. Hopefully we can get to their level someday. Like, the day when No Brainer Games has 20 research labs.

But for now, let's focus on what we have. And what we have is a massive pile of issues 😅.

The physics system runs in three stages in sequence:
1. Mark the grid cells of a spatial grid that contain rigid body voxels. 1 GPU thread is assigned to 1 rigid body voxel.
2. Test for collisions and apply repulsive forces to colliding rigid body voxels. 1 GPU thread is assigned to 1 rigid body voxel.
3. Compute momenta from repulsive forces and update body orientations. 1 GPU thread is assigned to 1 rigid body.

The issue was that when the spatial grid became large (over 32x32x32 or ~32k grid cells) the frame rate would drop to about 10 FPS if every grid cell detected a collision. Fortunately, after several Xcode crashes and a lengthy period of swearing from yours trully, the Xcode shader debugger finally revealed the cause.

It turned out that someone 😐 was clearing all grid cells occupied by a rigid body in stage 3 using a loop.

```nim
# Nim shader module

# stage 3
proc applyMomenta*(cIn: CIn) {.computeShader.} =
  # 1. Compute rigid body momenta based on forces applied.
  # 2. Update rigid body transform based on computed momenta.
  # 3. Get indices for grid cells occupied by rigid body.
  # 4. Clear grid cell collision flag at each index. ❌
```

In the current implementation, a rigid body occupies at least 8 grid cells: 1 for each corner of the smallest cubic volume that can contain the rigid body. This meant that (1) at least 7 cells were being cleared even if only 1 of the cells detected a collision, and (2) the cells were being cleared sequentially instead of in parallel!

To fix the issue, the loop was removed and replaced with an equivalent algorithm spread across stages 1 and 2:
1. Added a new `uint32` field to each grid cell:
    - lower 31 bits as a counter for the number of collisions that occurred within the cell
    - upper 1 bit as a 'dirty' flag to indicate that the cell was used in a previous simulation run
2. In stage 1:
    - if the dirty flag is set in the grid cell being occupied by the current rigid body voxel, clear the flag and set the counter to 1
    - else increment the counter
3. In stage 2:
    - use the counter to determine the number of rigid body voxel collisions to test for

This way of doing things actually added 2 optimizations:
1. Grid cells are cleared in parallel in stage 1.
2. In the case where there are multiple rigid body voxels detected within a single grid cell, we can use the counter to determine the exact number of collision tests to run.

The only price is an extra 32 bits to the data structure representing a grid cell. For a 32x32x32 grid, that's an extra 132kb. Yikes! We can probably optimize that too...🤔
