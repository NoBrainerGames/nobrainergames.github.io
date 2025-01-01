---
layout: post
title: "First steps"
categories: engine
comments: true
---

The first challenge was interfacing with C++.

Even though I had taken a liking to the D programming language, I continued my search for the best tools to use for developing the game engine. I realized that I simply did not have enough time to implement every aspect of the engine from scratch, so I needed to interface with existing libraries that I could glue together. It didn't take long for me to find out that [C++ is king when it comes to game engines](https://github.com/search?q=game+engine).

So I asked myself: why not just use C++ directly? I did have some experience with C++ when I worked on VR interfaces using [Unreal Engine](https://www.unrealengine.com/en-US/). I even learned the fundamentals of object-oriented programming by reading a book about [how to program in C++](https://www.goodreads.com/book/show/115703.C_) at least three times over. So why look for another language just to end up having to use C++ to a large capacity anyway?

The answer was that C++ was too complex for me to create a non-trivial system from scratch with. I simply did not have enough experience with it to implement a massive C++ codebase by myself; especially one that would eventually be worked on by other people. I was missing the intricacies of the language and knowledge of best practices that came with years of experience working in large game development teams.

It was fortunate that I stumbled upon communities and languages that sought to overcome similar challenges, the D community being one of them.

Other than D, I found that the [Haxe](https://haxe.org/) and [Rust](https://www.rust-lang.org/) communities exhibited rapid growth in the game programming space. Using Swift outside of the Apple ecosystem also occurred to me, having had experience implementing and releasing games to the App Store in earlier projects.

The following is the list of languages and frameworks I seriously investigated:

* D
* Swift via the [Silver](https://www.remobjects.com/elements/) compiler
* Haxe [targeting C++](https://haxe.org/manual/target-cpp-getting-started.html)
* Rust
* [Nim](https://nim-lang.org/)

I was overjoyed when I finished porting [this Vulkan tutorial](https://vulkan-tutorial.com/) to D early this year, which proved that the language was indeed one of the best languages to interface with existing C++ code. However, I soon found that it faced severe limitations when interfacing with metaprogramming-heavy C++ libraries like STL and boost. I eventually gave up on D after failing to port the [Diligent Engine](https://github.com/DiligentGraphics/DiligentEngine) library, which I had planned to use as the graphics backend for the engine. I still keep an eye on the language in the hopes that I would eventually be able to [include header files in D](https://github.com/atilaneves/dpp).

Swift with RemObject's Silver compiler was an exciting prospect for me after pivoting from D. Its compatibility with the JVM and .NET opened new doors in terms of the sheer number of [platforms](https://www.remobjects.com/elements/#platforms) I could tap into. Unfortunately I find it too difficult to set up and run on my systems without resorting to a paid version of the framework, so I moved on to other options.

Haxe was the next cab off the ranks. Its many backends boggled the mind, and I dreamt of making a game engine that could easily target every major platform in existence. In fact, the creator of the language has already made multiplatform [games with it](https://haxe.org/use-cases/games/)! After writing a few throw-away programs, however, I found the [warts in the language](https://news.ycombinator.com/item?id=9198406) too glaring for my tastes. It presented many ways to do things in a manner too similar to C++, probably due to the requirements imposed upon it by its numerous backends and maintainers. I was also spoiled by the power of metaprogramming in D, and Haxe seemed to be limited in comparison.

Rust stood out to me due to its syntactical similarities to Swift, but I ended up not liking it due to the challenges its [borrow checker](https://doc.rust-lang.org/1.8.0/book/references-and-borrowing.html) presented to my feeble brain. I had been searching for a language that struck a good balance between prototyping speed and type safety, but I found that Rust's approach leaned too heavily on the safety aspect for my purposes. It also has limited interop with C++, which greatly reduced the pool of tools and libraries I could access despite its rapidly growing community.

I first encountered Nim when I happened to read [a post in the D forums](https://forum.dlang.org/post/nofiznstdspaechomlnr@forum.dlang.org) mentioning its C++ interop capabilities. At the time I had a strong preference for curly-brace syntax owing to my history with C-based languages, so I put this language at the very bottom of the pile. But after 8 months of experimenting with other languages and getting nowhere, I finally decided to give it a fair shot.


```nim
import std/strformat

type
  Person = object
    name: string
    age: Natural # Ensures the age is positive

let people = [
  Person(name: "John", age: 45),
  Person(name: "Kate", age: 30)
]

for person in people:
  # Type-safe string interpolation,
  # evaluated at compile time.
  echo(fmt"{person.name} is {person.age} years old")


# Thanks to Nim's 'iterator' and 'yield' constructs,
# iterators are as easy to write as ordinary
# functions. They are compiled to inline loops.
iterator oddNumbers[Idx, T](a: array[Idx, T]): T =
  for x in a:
    if x mod 2 == 1:
      yield x

for odd in oddNumbers([3, 6, 9, 12, 15, 18]):
  echo odd


# Use Nim's macro system to transform a dense
# data-centric description of x86 instructions
# into lookup tables that are used by
# assemblers and JITs.
import macros, strutils

macro toLookupTable(data: static[string]): untyped =
  result = newTree(nnkBracket)
  for w in data.split(';'):
    result.add newLit(w)

const
  data = "mov;btc;cli;xor"
  opcodes = toLookupTable(data)

for o in opcodes:
  echo o
```
<sup>The above snippet is a peek into Nim's elegance.</sup>

I soon found a way to like Nim's syntax, and once that was out of mind, I began to delve deeper into the language. I figured out that Nim could compile into C++, which led to a theory: if Nim could interact with C++ at the source level instead of the ABI level like D did, maybe it could overcome the limitations of the other languages with the help of its epic metaprogramming chops.

3 months later, I have a working Nim wrapper for Diligent Engine.
