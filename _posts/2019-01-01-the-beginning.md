---
layout: post
title: "The beginning"
categories: engine
comments: true
---

The year 2019 was a year of learning for me.

Just before COVID-19 hit Australia, my interest in programming languages was rekindled. As an iOS developer, I loved the elegance of [Swift](https://www.swift.org/) and was interested in discovering more languages like it. Was there another programming language out there that was as elegant and expressive as Swift? That question kept me up late at night.

Prior to Australia, my background in programming went as far as writing tiny C and assembly programs as a student. I experimented with scripting languages like Perl and Python during my free time by implementing software robots that could play online games for me. Before graduating, I discovered Objective-C when I delved into iOS application programming for my first startup. I was amazed by the flexibility of that language; the run-time metaprogramming facilities of Objective-C combined with C macros seemed to provide me with endless ways to express logic and even more ways to shoot myself in the foot. In fact, I enjoyed writing horribly obfuscated metaprograms so much that I made a freelance developer cry from the agony of trying to understand my code.

A few years and two iOS app development jobs went by before Apple officially released Swift. I discovered how much easier code was to maintain when it was written in a clean and self-documenting manner. Swift -- powered by its shiny new protocol-oriented programming paradigm -- paved the way to my first clean codebase that other people could actually work on.

Still, I missed being able to write code that could create more code.

I began experimenting with the [D programming language](https://dlang.org/) after I moved to the land down under. I had previously encountered the language while researching obscure programming languages, but I had never really implemented anything with it. I was hooked as soon as I understood what it was capable of: D supported high-level programming constructs like a scripting language while still being able to drill down to the bit level. It accomplished this by leveraging its powerful metaprogramming facilities. It was like a better version of C, and could even interop with C++!


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

It turned out that just before I moved to Australia, I had worked as a contractor in a research project to build human interfaces for virtual reality games. This experience planted a seed that drove me to write a game engine that would put virtual reality at the forefront of the game development process.

And so I began to work towards implementing a prototype game engine. Looking back, I'm not sure I knew exactly how hard it was going to be.
