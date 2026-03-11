---
layout: post
title: "Smooooth visual"
categories: engine
comments: true
---

BAM! Just like that, an entire year has passed.

Time moves fast when you're banging your head against the wall...er, figuring out how to render VR graphics fast enough so players don't vomit.

So yeah, first of all, I finally got VR working! I hit up to #4 of my [goals](./2024-12-15-a-new-engine-for-a-new-year.md#upcoming-work) last year, and it was hectic.

OpenXR's verbosity is something else. In order to integrate VR, I had to rewrite my display system to accept normal window swap chains and VR swap chains, which are what renderers render to in a Vulkan app. Extracting the swap chain from OpenXR was a whole dance.

In summary, OpenXR provides a set of revolving textures for the application to render to, which are swapped every frame so the last frame can be presented to the screen while the next frame is being rendered. By default, separate textures are provided for each eye, since VR headsets present two separate images for each eye simultaneously.

What I wanted to do though was to keep my single-draw call rendering and do the image multi-plexing for each eye on the GPU. Fortunately after some digging, I found that OpenXR allows specifying two layers for its swap chain textures and the application can render the image for each eye on separate layers of the textures.

All good so far...until I saw the jaggies in the scene! In VR, aliasing is extremely noticeable and jarring, so I decided to try and enable [Vulkan's MSAA](https://docs.vulkan.org/samples/latest/samples/performance/msaa/README.html) feature. The idea is that the application renders to an MSAA texture, and in Vulkan you get that by intialising the texture to contain more than 1 sample. When the application has finished rendering, it must then instruct Vulkan to "resolve" those samples into a swap chain texture before presenting the swap chain.

This resolve step can be done in two ways, by calling `VkCmdResolveImage` from the CPU before presenting, or by using resolve attachments which allows Vulkan to do the resolving automatically in the fixed function pipeline. [This article](https://arm-software.github.io/vulkan-sdk/multisampling.html) explains why the former is slow and bad, while the latter is fast and amazing, especially for tile-based GPUs like the ones used for Meta Quest.

This sent me down a rabbit hole of refactoring the core renderer so these MSAA textures are created automatically as long as you specify a render target sample count of >1. I also decided to convert my renderer to use render passes instead of the dynamic rendering feature. This is because render passes are still the most performant method of rendering for tile-based GPUs because they allow passing data between render passes (fast) without commiting anything to shared memory (slow). Render passes also conveniently allow me to provide resolve texture references in the initialisation functions.

The result? Smooth edges. Maybe I'll post a VR image at some point, but here is a flat screen render:

![MSAA demo]({{ "assets/msaa.png" | relative_url }})
