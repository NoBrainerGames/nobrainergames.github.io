---
layout: post
title: "Milestone post for 2024"
categories: engine
---

The year 2020 put a nagging question in my head: *what is a difficult problem that I can enjoy working on and become my life's work?* 6 months later I had come up with a problem statement: *make a game engine uniquely suited for creating VR action RPG games.*

I had some experience creating VR games using Unity3D and Unreal Engine 4 in past jobs, and really enjoyed the creative and technical aspects of it, but I was never exposed to the systems running behind the scenes.

So I embarked on a journey of coffee-fuelled nights and socially-deprived weekends towards what seemed like an impossible goal. 4 years and 3 rewrites later, I am proud to announce the demo of my upcoming indie game made with my own game engine!

I laid out the following requirements for the MVP:
1. Must be written in a small programming language that I can contribute to.
2. Said programming language must be able to interface with both C and C++.
3. 3D rendering system must be portable to all major desktop and mobile platforms without too much extra work.
4. Physics, rendering and animation systems must be fast with many rendered objects.
5. Architecture must be modular and components easily testable.

I'm happy to say that I have (mostly) hit these requirements, having the following notable features:
1. Written in [Nim](https://nim-lang.org/) with some C and C++ glue for third party libraries.
2. Uses [Diligent](https://diligentgraphics.github.io/) with the Vulkan API, taking advantage of cutting-edge features to render scenes in 1 draw call.
3. GPU-driven animation of skeletal meshes loaded from gltf2 assets for efficient crowd animation.
4. Rigid body physics implemented with compute shaders, supporting >98k simultaneous collisions at 120+ FPS on an Apple M2 Pro machine.
5. Custom ECS that supports usage across DLL boundaries, used for hot code reloading and plug-in functionality.
6. Nim to HLSL transpiler with shader reflection, enabling rapid prototyping and unit tests that are run on CPU. Try out the (very) WIP [playground](https://nobrainergames.com/playground.html) to see the transpiler working!

 There are still a few things needed to get to an actual game. For instance there is no sound subsystem yet (my partner [Anna del Rosario](https://www.linkedin.com/in/annadelro) who is a talented music producer added sound post-recording).

While there is still lots of R&D to be done, I would love to get in touch with Nim/XR/game devs and founders to learn and share ideas. Check out my [blog](https://nobrainergames.com/) for more details and contact info. I am in the process of opensourcing parts of the code @ [github](https://github.com/n0bra1n3r) and will be looking forward to feedback on it, so feel free to follow/watch!

P.S. I used [meshy.ai](https://www.meshy.ai/) to create the demo assets which saved an unimaginable amount time.

#vr #game #graphics #shaders #engine #ai #nim #cpp #diligentgraphics #meshyai

<iframe
    width="641"
    height="360"
    src="https://www.youtube.com/embed/BiptB-zqJpc?si=3f4Z9ofTxVN3VMDe"
    title="Reboot Engine demo"
    frameborder="0"
    allow="picture-in-picture"
    allowfullscreen>
</iframe>

<sup>Reboot Engine demo</sup>
