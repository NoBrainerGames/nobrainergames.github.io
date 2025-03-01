---
layout: post
title: "AI this, AI that"
categories: engine
comments: true
---

I realized that noboby ever stops talking about AI. I heard about it so much on the various channels I lurk in that it became a problem.

So I decided to do something about it.

The Reboot Engine now has a local LLM running inside it. That's right. It doesn't just call out to OpenAI, Claude, or whatever other service. Well it does, but I'll talk about that later.

First I'll just mention what the actual point of it is. Remember the [demo video](https://youtu.be/ONRqG3Oo6sM) I posted in January? There was a nice troll standing at the gate, smashing up goblins. I just wanted to be able to talk to that troll. As in have a deep, meaningful conversation about how I want to get to the other side of the gate so I can get on with my quest.

In my [other post](./2024-12-15-a-new-engine-for-a-new-year.md#ecs-framework), I describe my custom ECS a bit. At a high level, all the engine really is is a bunch of systems communicating with the main program and each other. To get the troll to talk to me, I ended up adding 5 new systems:
1. speech-to-text
2. AI language model
3. text-to-speech
4. audio output
5. file downloader

The first 3 actually run AI models. Speech-to-text runs 2 models locally, one for [voice activity detection](https://github.com/snakers4/silero-vad) (VAD) and another for [automatic speech recognition](https://github.com/usefulsensors/moonshine) (ASR). I use [Hermes 3 3B](https://huggingface.co/NousResearch/Hermes-3-Llama-3.2-3B) as the language model. I call out to the [ElevenLabs API](https://elevenlabs.io/) for text-to-speech because I'm still experimenting with local TTS, and their speech generation model is unbelievably fast. This is the only system that uses a remote API.

For sound input and output, I use [OpenAL Soft](https://github.com/kcat/openal-soft). They have a nice C API, and I want to try taking advantage of their 3D sound features at some point.

The file downloader system is actually the first one I implemented. I needed it to download all those models in advance (about 2GB worth) before booting up the rest of the engine. It was also the most hair-pullingly frustrating system I've implemented in the engine. "But what's the problem?" you say. "It's just a file downloader right?" you say. WRONG. Well you're right, but it's not that simple apparently.

So I'm currently [targeting WASM](./2025-02-01-wasm.md) for my demos. I'm doing this because it's super easy to show people things on a browser. But you apparently can't access the network from WASM willy-nilly. Trying to compile something like [libcurl](https://curl.se/libcurl/) won't work.

Fortunately Emscripten has a [fetch API](https://emscripten.org/docs/api_reference/fetch.html), so I just did the typical `#ifdef emscripten` (or `when defined(emscripten)` in Nim) and used the Emscripten API for web builds. Done? Nope. The next issue is storing the downloaded files. The model files are massive, so you have to write them to disk and not just keep them hanging around in RAM. But you can't write to disk willy-nilly from WASM 🤦.

If you take a closer look at the fetch API docs, you'll notice a mention of IndexedDB. This is a new in-browser database that's similar to things like CoreData in iOS. It stores massive files like we need to it to, but there is a magic incantation you need to perform to make it work with your `fopen` and `fwrite` calls:

```c
EM_ASM({
  FS.mkdir('models');
  FS.mount(IDBFS, { autoPersist: true }, 'models');
  FS.syncfs(true, (err) => {
    if (err) {
      console.error('emscripten: ', err);
    }
  });
});
```

Make sure you add that `autoPersist` flag. Call this in your main thread and you're set. Maybe. Speaking of threads...I'll talk about that in my next post. 😅
