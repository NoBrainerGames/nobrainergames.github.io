---
layout: post
title: "The beginning"
categories: engine
comments: true
---

This year was a year of learning for me.

The year my interest in programming languages was rekindled. As an iOS developer, I love the elegance of [Swift](https://www.swift.org/) and I am interested in discovering more languages like it. Is there another programming language out there that is as elegant and expressive as Swift? That question keeps me up late at night.

As a college student, I loved writing tiny C and assembly programs. I experimented with scripting languages like Perl and Python during my free time by implementing software robots that could play online games for me. Before graduating, I discovered Objective-C when I delved into iOS application programming for my first startup. I was amazed by the flexibility of that language; the run-time metaprogramming facilities of Objective-C combined with C macros seemed to provide me with endless ways to express logic and even more ways to shoot myself in the foot. In fact, I enjoyed writing horribly obfuscated metaprograms so much that I once made a freelance developer cry from the agony of trying to understand my code.

A few years and two iOS app development jobs went by before Apple officially released Swift. I discovered how much easier code was to maintain when it was written in a clean and self-documenting manner. Swift -- powered by its shiny protocol-oriented programming paradigm -- paved the way to my first codebase that other people could actually work on.

Still, I missed the expressivity of metaprogramming.

I began experimenting with the [D programming language](https://dlang.org/) after I moved to the land down under. I had previously encountered the language while researching obscure programming languages to sink my teeth into, but I had never really implemented anything with it. I was hooked as soon as I understood what it was capable of: D supported high-level programming constructs like a scripting language while still being able to drill down to the bit level. It accomplished this by leveraging its powerful metaprogramming facilities. It was like a better version of C, and could even interop with C++!


```d
void main()
{
    import std.range, std.stdio;

    auto sum = 0.0;
    auto count = stdin
        //Get an input range set up to read one line at a time
        .byLine
        //Perform a transparent operation (as in the shell command tee)
        .tee!(l => sum += l.length)
        .walkLength;

    writeln("Average line length: ",
        count ? sum / count : 0);
}
```
<sup>The snippet above is a taste of the powerful simplicity of D.</sup>

I quickly developed a hunger to find a project to implement with it.

It turns out that just before I moved to Australia, I had worked as a contractor in a research project to build interfaces for virtual reality games. This experience planted a seed that drove me to start writing a game engine, one that will put virtual reality at the forefront of the game development process if I am successful.

And so I begin to work towards implementing a prototype game engine.
