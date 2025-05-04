---
layout: post
title: "Anatomy of coroutines"
categories: engine
comments: true
---

Last month, I cleaned up some of the game code I had been writing. One of my simple game demos had just reached 1k lines, and I thought maybe it was time to address the growing complexity.

Apart from game logic, a lot of the code in each of the game files was some variation of common rendering code. Loading 3D assets, loading shaders, allocating resources for shaders...the usual. The rest of the code like windowing and input had already been extracted into separate modules called "systems". I had been putting off doing the same for the rendering stuff because I hadn't actually sat down and thought through how it should be split into independent modules. Last month I finally found an acceptable strategy to implement this, so I went about creating an API for accessing the functionality of these new systems more easily.

A game folder looks something like this:

```
reboot/
  |- core/
  |    |- ecs.nim
  |    |- gltf.nim
  |    |- gpu.nim
  |    |- math.nim
  |
  |- components/
  |    |- camera.nim
  |    |- viewport.nim
  |
  |- systems/
  |    |- scene.nim
  |    |- window.nim
  |
  |- shaders/
       |- physics.nim
       |- instancecolors.nim

assets/
  |- model.gltf
  |- skybox.ktx

game.nim
```

The idea is that the game loop inside `game.nim` calls the `update` procedure inside each file in `systems/` once every frame. Those `update` procedures in turn query for combinations of the component types declared in `components/` and invoke the APIs implemented in `core/` depending on the results.

Something similar needed to be done in the game logic. For example, if the system handling the camera changed the rotation of the `Camera` component, the game logic could respond by making an NPC on screen look at the player. To implement this, I could create a new system with an `update` function that queried for `Camera` components. However, I found the context switching required to do this quite taxing and wanted to be able to mock out behaviour quickly inside the game file itself.

For inspiration, I thought of how existing asynchronous systems worked. For example, Javascript implements an [event loop](https://www.geeksforgeeks.org/what-is-an-event-loop-in-javascript/) which is essentially a game loop that queries a queue for callbacks submitted from elsewhere in the code. Since this is very similar to how my own engine implements component querying, it occurred to me that I could implement the same thing using a component type with a function pointer field. All I had to do was create a new system that queried for this new component every frame and call the referenced function.

Using the ECS API in the engine, this could be written in `game.nim` like:

```nim
# game.nim

let entity = ...
entity.attach Lambda(callback: proc() = echo "do something")
```

and the new system could be implemented like:

```nim
# dispatch.nim

proc update() =
  for lambda in query(Lambda):
    lambda.callback()
```

I couldn't believe how conceptually simple this was. All kinds of other things could be implemented with this, like timers, coroutines...

So, coroutines. Unity3D [implements them](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Coroutine.html) as a convenient way to express state changes in a game object. I particularly like how timers, delays, and state machines can be written inside what appeared to be a simple function. Using Nim's metaprogramming, I made an interface for the new `Lambda` component that looks very similar to Unity's API:

```nim
# game.nim

var isGameStart = false

# count down before game start
coroutine:
  yield State(kind: delay, seconds: 1)
  echo "3"
  yield State(kind: delay, seconds: 1)
  echo "2"
  yield State(kind: delay, seconds: 1)
  echo "1"
  yield State(kind: delay, seconds: 1)
  echo "START"
  isGameStart = true
  break

var npcEntity = ...

# perform an action if the camera is facing an NPC
coroutine do(camera: Camera):
  if not isGameStart:
    continue

  if camera.isLookingAt(npcEntity):
    echo "look back"
```

This new API was implemented in less than 20 lines of Nim code (simplified for readability):

```nim
template coroutine(code) =
  block:
    iterator iter(): auto =
      code

    let entity = newEntity()
    entity.attach Lambda(
      callback: proc(handle: Entity) =
        if finished(iter):
          # remove this Lambda component from the ECS if the iterator has finished
          delete(handle)
          return

        discard iter()
    )
```

Pretty cool, right?
