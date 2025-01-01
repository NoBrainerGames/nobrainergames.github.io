---
layout: post
title: "A quiet few months"
categories: engine
comments: true
---

By this time not much visible progress has been made -- other than rendering another colorful triangle on my laptop.


![A triangle in Nim](https://github.com/DiligentGraphics/DiligentSamples/blob/1b40c774ae9b0735382614e8d505278765a5d870/Tutorials/Tutorial01_HelloTriangle/Screenshot.png?raw=true)

<sup>A triangle in Nim.</sup>

On the surface it's just a repeat of the work that I had done with the D programming language, but translated to Nim. However there is a subtle but important difference: this time I used Diligent Engine to render the triangle.

The simple triangle was the result of my many months of learning around the Nim programming language. Recently I figured out that I could easily call C++ code from Nim without strictly modelling every concept the C++ code presented. This is due to the fact that Nim compiles to C++, and can therefore interact with C++ at the source level. This means that all I have to do is match C++ type names when using them in Nim, as opposed to having to describe their contents.

To illustrate, take this C++ code snippet:

```cpp
class CppClass
{
public:
  int field1;
  float field2;
};

CppClass value;
```

A language like D -- which interfaces with C++ through the ABI -- requires the programmer to define all fields of the value type:

```d
extern(C++) class CppClass
{
  int field1;
  float field2;
}

CppClass value;
```

...whereas in Nim, the type would simply be expressed as:

```nim
type CppClass {.importcpp.} = object

var value: CppClass
```

It may not be obvious in this contrived example, but this detail makes a world of difference when interfacing with large codebases. Most non-trivial C++ data structures would contain fields that are themselves C++ data structures, typically requiring massive swaths of boilerplate code for interop. With Nim, simply declaring a type's name allows that type to be used immediately, its innards needing to be fleshed out only when needed.

This breakthrough drove the creation of the first version of my C++ interop library, lovingly dubbed [cinterop](https://github.com/n0bra1n3r/cinterop). It is the library that has finally allowed me to interface with a beast of a rendering framework that is Diligent Engine.
