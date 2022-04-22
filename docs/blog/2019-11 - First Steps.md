---
title: First Steps
template: comments.html
publish: blog/
---

The first challenge was interfacing with C++.

Even though I had taken a liking to the D programming language, I continued my search for the best tools to use for developing the game engine. I realized that I simply did not have enough time to implement every aspect of the engine from scratch, so I needed to interface with existing libraries that I could glue together. It didn't take long for me to find out that C++ was king when it came to game engines.

So I asked myself: why not just use C++? I did have some experience with C++ due my work on VR interfaces in [Unreal Engine](https://www.unrealengine.com/en-US/). I even learned the fundamentals of object-oriented programming by reading a book about [how to program in C++](https://www.goodreads.com/book/show/115703.C_). So why look for another language just to end up having to use C++ to a large capacity anyway?

The answer was that C++ was too complex for me to create a non-trivial system from scratch with. I simply did not have enough experience with it to implement a massive C++ codebase by myself; especially one that would eventually be worked on by other people. I was missing the intricacies of the language and knowledge of best practices that came with years of experience working in large game development teams.

Fortunately I stumbled on communities and languages that sought to overcome similar challenges, the D community being one of them.

Other than D, I found that the [Haxe](https://haxe.org/) and [Rust](https://www.rust-lang.org/) communities were exhibiting rapid growth in the game programming space. I also considered using Swift outside of the Apple ecosystem, which presented some interesting possibilities given its compatibility with Objective-C. The following is the list of languages and frameworks I seriously investigated:

* D
* Swift via the [Elements](https://www.remobjects.com/elements/) framework
* Haxe [targeting C++](https://haxe.org/manual/target-cpp-getting-started.html)
* Rust
* [Nim](https://nim-lang.org/)

I was overjoyed when I finished porting [this Vulkan tutorial](https://vulkan-tutorial.com/) to D, which proved that the language was indeed one of the best languages to interface with existing C++ code. However, I soon found that it had severe limitations when interfacing with metaprogramming-heavy C++ libraries like STL and boost. I eventually gave up on D after failing to port the [Diligent Engine](https://github.com/DiligentGraphics/DiligentEngine) library, which I had planned to use as the graphics backend for the engine.

Swift with the Elements framework was an exciting prospect for me after pivoting from D. Its compatibility with the JVM and .NET opened new doors in terms of the sheer number of resources and code I could tap into. Unfortunately I found it too difficult to set up on my systems without resorting to a paid version of the framework, so I moved on to other options.

Haxe was the next cab off the ranks. Its many backends boggled the mind, and I dreamt of making a game engine that could easily target every major platform in existence with it. After writing a few throw-away programs with it, however, I found the inconsistencies in the language too glaring to ignore. It presented many ways to do things in a manner too similar to C++, probably due the requirements imposed upon it by its backends. I was also spoiled by the power of metaprogramming in D, and Haxe seemed to have some limitations in comparison.

Rust stood out to me due to its syntactical similarities to Swift, but I ended up not liking it due to its borrow checker. I had been searching for a language that struck a good balance between cognitive simplicity and type safety, but I found that Rust's approach leaned too heavily on the safety aspect for my purposes. It also had limited interop with C++, which greatly reduced the pool of tools and libraries I could access.

I first encountered Nim when I happened to read a post in the D forums comparing their C++ interop capabilities. At the time I had a strong preference for curly-brace syntax owing to my history with C-based languages, so I put this language at the bottom of the pile. But after 8 months of experimenting with other languages and getting nowhere, I decided to give it a fair shot.

I soon found a way to like Nim's syntax, and once that was out of mind, I began to delve deeper into the language. I figured out that Nim could compile into C++, which lead to a theory: if Nim could interact with C++ at the source level instead of the ABI level like D did, maybe I could overcome the limitations of the other languages.

6 months later, I had a working Nim wrapper for Diligent Engine.