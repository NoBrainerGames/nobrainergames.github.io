---
layout: page
title: projects
permalink: /projects/
---

## Macabre game (available on Steam)

<iframe
    width="641"
    height="360"
    src="https://www.youtube.com/embed/eqZroRAoVE4"
    title="Macabre launch trailer"
    frameborder="0"
    allow="picture-in-picture"
    allowfullscreen>
</iframe>

[Macabre](https://www.macabregame.com/) is a cooperative extraction horror game made with Unreal Engine 5 that I worked on with the team at WeForge. My main responsibilities were implementing voice-over-IP (VoIP) and player travel between maps, as well as assisting with the weather system, the cosmetics system, and inventory system.

To implement VoIP I used the P2P Steam API paired with a task-based multi-threaded design for sending and receiving voice packets and buffering to eliminate in-game stutters. I also implemented a worker thread to down-sample voice input to 16kHz and up-sample voice packets back to 44kHz using libsamplerate.

I used a combination of C++17 for the performance-intensive parts, and exposed data fields through Blueprint to serve as an easy configuration interface for the designers.

## Missile Madness!

<iframe
    width="641"
    height="360"
    src="https://www.youtube.com/embed/VPclgKAF8W0"
    title="Missile Madness!"
    frameborder="0"
    allow="picture-in-picture"
    allowfullscreen>
</iframe>

This mini-game was presented at the Western Sydney University Welcome Week. It is a VR game about using controllers to catch rockets flying at the player. The hectic gameplay and art was meant to highlight our event partner WSU LaunchPad's branding, and was designed together with No Brainer Games.

This was the first public game that was made with my [Reboot](https://nobrainergames.com/engine/2024/12/15/a-new-engine-for-a-new-year.html) game engine. The systems that made it possible were written from the ground up and powered by Vulkan, OpenXR, and OpenAL-Soft:

- Sparse-array-based entity component system (ECS) used for event propagation 
- API layer for zero-overhead interop with high-performance C and C++ libraries
- Custom shading, lighting and compute-shader-based outline rendering for a stylised look
- GPU-driven particle-based physics inspired by Nvidia's [GPU Gems article](https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-29-real-time-rigid-body-simulation-gpus) on rigid body simulation
- Spatial audio integrated with the GPU-driven pipeline for immersion

I made a [post](https://www.linkedin.com/posts/ryan-blonna_missile-madness-wsu-opening-week-activity-7434434469165580289-mJAM) on LinkedIn about it.

## Nobby the desktop assistant

<iframe
    width="641"
    height="360"
    src="https://www.youtube.com/embed/1wBL96f1-Vg"
    title="Nobby"
    frameborder="0"
    allow="picture-in-picture"
    allowfullscreen>
</iframe>

Nobby was demoed at the Western Sydney Innovation Festival and at a public pitching event, where it was presented to investors and other participants.

This is a prototype desktop assistant for MacOS created using C++17 and Vulkan. The assistant was rendered as an animated robot on a transparent background, and intelligently interacted with the user using a local Phi 4 multi-model LLM, Kokoro TTS model, Silero VAD model, Moonshine STT model, and the Voyage multi-modal embedding model. These models were run using Microsoft's [ONNX Runtime](https://github.com/microsoft/onnxruntime) C++ library.

The application interacted with the user by receiving voice, a desktop screenshot, and mouse position as inputs, running them through the multi-modal LLM, and rendering the LLM text output as voice, animated robot avatar actions, and tool invocations through my custom scripting system.

The application rendered smoothly with the help of my multi-threaded design, allowing models to behave as data sources sitting in their own background threads, with the main thread sending queries and routing outputs between models and the rendering backend.

## AI adventure RPG demo

<iframe
    width="641"
    height="360"
    src="https://www.youtube.com/embed/ekrgwUyaImI"
    title="AI adventure"
    frameborder="0"
    allow="picture-in-picture"
    allowfullscreen>
</iframe>

This demo was written in C++ and compiled to WebAssembly with Emscripten. The NPC was powered by Microsoft's Phi 4, Piper TTS, and Moonshine STT generative AI models, all dynamically loaded and run in the local browser using web workers.

The graphics was powered by WebGPU and WGSL, rendering at 120FPS on a MacBook Pro, with near-instant response time from the AI models. This was thanks to GPU-driven rendering and animations, allowing full use of both CPU and GPU for AI and rendering.

## Eldervine VR experience

<iframe
    width="641"
    height="360"
    src="https://www.youtube.com/embed/a_iAy9kTZcU"
    title="Eldervine"
    frameborder="0"
    allow="picture-in-picture"
    allowfullscreen>
</iframe>

This is a VR experience created with the Ubiquitous Computing VR Lab, with the goal of researching novel input modes in VR using human hands.

For this project we used C++ with Unreal Engine 4, and the Leap Motion device mounted on the Oculus Quest 1 for detecting hand and finger motion inside the game.
