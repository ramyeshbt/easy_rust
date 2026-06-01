# Chapter 7 — Generics: Write Once, Use With Many Types

> "The best code is code you don't repeat. Generics are Rust's way of making that safe."

You've written functions that take `i32`, structs that hold `String`, and enums that wrap specific types. What if you need the same logic to work with *any* type? That's what **generics** solve — and in Rust, they do it with **zero runtime cost**.

---

## The Analogy: A Cookie Cutter

Imagine a cookie cutter in the shape of a star. You don't care what dough you use — shortbread, gingerbread, sugar dough. The *shape* (the logic) is the same; only the *material* (the type) changes.

```
Cookie Cutter (generic function)     Dough (concrete type)
┌────────────────────────────┐
│  fn largest<T>(list: &[T]) │  ◄── &[i32]     → largest integer
│                            │  ◄── &[f64]     → largest float
│                            │  ◄── &[char]    → largest character
└────────────────────────────┘
Same shape. Different dough. One definition.
```

Without generics you'd write `largest_i32`, `largest_f64`, `largest_char` — identical logic, three times. With generics, you write it once and the compiler stamps out the versions it needs.

---

## Part 1: Generic Functions

### The Problem Without Generics

```rust
// Without generics — duplicated for every type 😤
fn largest_i32(list: &[i32]) -> &i32 {
    let mut largest = &list[0];
    for item in list {
        if item > largest { largest = item; }
    }
    largest
}

fn largest_f64(list: &[f64]) -> &f64 {
    let mut largest = &list[0];
    for item in list {
        if item > largest { largest = item; }
    }
    largest
}
```

The bodies are *identical*. This is copy-paste programming — a maintenance trap.

### With Generics

```rust
// T is a placeholder — "some type we'll fill in later"
// T: PartialOrd means T must support > comparison (trait bound)
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest { largest = item; }
    }
    largest
}

fn main() {
    let numbers = vec![34, 50, 25, 100, 65];
    let chars   = vec!['y', 'm', 'a', 'q'];
    let floats  = vec![3.14, 2.71, 1.41];

    println!("Largest number: {}", largest(&numbers));  // 100
    println!("Largest char:   {}", largest(&chars));    // y
    println!("Largest float:  {}", largest(&floats));   // 3.14
}
```

`T` is a **type parameter** — a placeholder that gets replaced with a real type when the function is called. The `: PartialOrd` is a **trait bound** — a constraint saying "T must be comparable". You'll recognise that from Chapter 6.

---

## Part 2: Generic Structs and Enums

### Generic Structs

```rust
// A pair that can hold any two values of the same type
#[derive(Debug)]
struct Pair<T> {
    first:  T,
    second: T,
}

impl<T> Pair<T> {
    fn new(first: T, second: T) -> Self {
        Self { first, second }
    }
}

// A method only available when T can be compared and displayed
impl<T: PartialOrd + std::fmt::Display> Pair<T> {
    fn larger(&self) {
        if self.first >= self.second {
            println!("The larger value is: {}", self.first);
        } else {
            println!("The larger value is: {}", self.second);
        }
    }
}

fn main() {
    let pair_ints   = Pair::new(5, 10);
    let pair_strs   = Pair::new("hello", "world");
    let pair_floats = Pair::new(3.14, 2.71);

    pair_ints.larger();      // The larger value is: 10
    pair_strs.larger();      // The larger value is: world
    pair_floats.larger();    // The larger value is: 3.14

    println!("{:?}", pair_ints);   // Pair { first: 5, second: 10 }
}
```

Note the two `impl<T>` blocks:
- The first adds `new()` to **all** `Pair<T>` — no constraints needed.
- The second adds `larger()` only when `T: PartialOrd + std::fmt::Display` — a **conditional implementation**.

### Generic Enums — You Already Know These

`Option<T>` and `Result<T, E>` from the standard library are the most-used generic enums in all of Rust:

```rust
// How Option is actually defined in std:
enum Option<T> {
    Some(T),   // holds a value of any type T
    None,      // holds nothing
}

// How Result is actually defined in std:
enum Result<T, E> {
    Ok(T),     // success, holds a value of type T
    Err(E),    // failure, holds an error of type E
}
```

Every time you've written `Option<i32>` or `Result<String, io::Error>`, you've been using generics. Now you understand what those angle brackets mean.

---

## Part 3: Trait Bounds — The Safety Contract

Generics without bounds would let you write `T + T` without knowing if `T` supports addition. Rust requires you to declare what operations you need:

### Single Bound

```rust
use std::fmt::Display;

fn print_value<T: Display>(value: T) {
    println!("Value: {}", value);
}
```

### Multiple Bounds with `+`

```rust
use std::fmt::{Debug, Display};

fn show<T: Display + Debug>(value: T) {
    println!("Display: {}", value);
    println!("Debug:   {:?}", value);
}
```

### `where` Clauses — Cleaner for Complex Bounds

```rust
// Gets messy inline:
fn compare_and_show<T: Display + PartialOrd, U: Display + Debug>(t: T, u: U) {
    // ...
}

// Clean with where:
fn compare_and_show<T, U>(t: T, u: U)
where
    T: Display + PartialOrd,
    U: Display + Debug,
{
    println!("t = {}, u = {:?}", t, u);
}
```

### Conditional Methods — `impl<T: Bound>`

You can add methods to a generic struct only when T meets certain requirements:

```rust
use std::fmt::Display;

#[derive(Debug)]
struct Wrapper<T> {
    value: T,
}

impl<T> Wrapper<T> {
    fn new(value: T) -> Self {
        Self { value }
    }
}

// This method only exists when T implements Display
impl<T: Display> Wrapper<T> {
    fn show(&self) {
        println!("Wrapper holds: {}", self.value);
    }
}

fn main() {
    let w1 = Wrapper::new(42);
    w1.show();          // ✅ i32 implements Display

    let w2 = Wrapper::new(vec![1, 2, 3]);
    // w2.show();       // ❌ Vec<i32> doesn't implement Display
    println!("{:?}", w2); // ✅ Debug works because #[derive(Debug)]
}
```

---

## Part 4: Generic Structs in Practice — A Typed Stack

Let's build something real: a generic stack (last-in-first-out collection).

```rust
#[derive(Debug)]
struct Stack<T> {
    elements: Vec<T>,
}

impl<T> Stack<T> {
    fn new() -> Self {
        Stack { elements: Vec::new() }
    }

    fn push(&mut self, item: T) {
        self.elements.push(item);
    }

    fn pop(&mut self) -> Option<T> {
        self.elements.pop()
    }

    fn peek(&self) -> Option<&T> {
        self.elements.last()
    }

    fn is_empty(&self) -> bool {
        self.elements.is_empty()
    }

    fn size(&self) -> usize {
        self.elements.len()
    }
}

// Extra method only when T can be displayed
impl<T: std::fmt::Display> Stack<T> {
    fn print_top(&self) {
        match self.peek() {
            Some(top) => println!("Top: {}", top),
            None      => println!("Stack is empty"),
        }
    }
}

fn main() {
    // Integer stack
    let mut int_stack: Stack<i32> = Stack::new();
    int_stack.push(1);
    int_stack.push(2);
    int_stack.push(3);
    int_stack.print_top();                        // Top: 3
    println!("Popped: {:?}", int_stack.pop());    // Popped: Some(3)
    println!("Size: {}", int_stack.size());       // Size: 2

    // String stack — exactly the same code, different type
    let mut str_stack: Stack<String> = Stack::new();
    str_stack.push(String::from("Rust"));
    str_stack.push(String::from("Rocks"));
    str_stack.print_top();                        // Top: Rocks
    println!("{:?}", str_stack);
}
```

```
Top: 3
Popped: Some(3)
Size: 2
Top: Rocks
Stack { elements: ["Rust", "Rocks"] }
```

One `Stack<T>` definition. Works for any type. No code duplication.

---

## Part 5: Generics and the Standard Library

Once you understand generics, the standard library's type signatures stop being cryptic:

```rust
// Vec<T> — a growable list of any type T
let v: Vec<i32> = vec![1, 2, 3];

// HashMap<K, V> — maps keys of type K to values of type V
use std::collections::HashMap;
let mut scores: HashMap<String, u32> = HashMap::new();

// Option<T> — Some(T) or None
let maybe: Option<f64> = Some(3.14);

// Result<T, E> — Ok(T) or Err(E)
let parsed: Result<i32, _> = "42".parse();

// Iterator trait (simplified) — yields items of type Item
// fn map<B, F: FnMut(Self::Item) -> B>(self, f: F) -> Map<Self, F>
// That's just: "map takes a function from T to B, returns an iterator of B"
```

Generics are everywhere in Rust. Understanding them demystifies the standard library.

---

## 🔍 Deep Dive — Monomorphization: Zero Runtime Cost

This is the magic behind Rust's promise that "abstractions are free."

When the compiler sees this:

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest { largest = item; }
    }
    largest
}

fn main() {
    largest(&[1, 2, 3]);          // called with i32
    largest(&[3.14, 2.71]);       // called with f64
    largest(&['a', 'z', 'm']);    // called with char
}
```

It generates three **concrete** functions — as if you'd written them by hand:

```
Generic source code          What the compiler actually generates
────────────────────────     ──────────────────────────────────────
                             fn largest_i32(list: &[i32]) -> &i32 {
fn largest<T>(list: &[T])        let mut largest = &list[0];
──────────►  fn largest_f64(list: &[f64]) -> &f64 {
                             fn largest_char(list: &[char]) -> &char {
```

At **runtime**, there is no generic. There is no type dispatch. There is no overhead. The CPU executes the same tight, optimised machine code it would if you'd hand-written each version.

```
Language        Generics cost
──────────────────────────────
Java / C#       Virtual dispatch or boxing → runtime overhead
Python          Everything is a pointer → overhead on every op
C++ templates   Monomorphization → zero overhead ✅ (same as Rust)
Rust generics   Monomorphization → zero overhead ✅
```

The tradeoff: **compile time and binary size increase** slightly (more code to generate), but runtime performance never suffers. For most programs this is an excellent deal.

### Contrast: `dyn Trait` (from Chapter 6)

`Box<dyn Trait>` uses **dynamic dispatch** — a vtable lookup at runtime (a pointer indirection). It's the right tool when you need runtime flexibility (mixed types in a Vec). For everything else, prefer generics.

```
impl Trait / generics → compile-time, monomorphized, fastest, one type per call site
dyn Trait             → runtime vtable, flexible, small overhead, mixed types ok
```

---

## Break It On Purpose

### Mistake 1: Missing trait bound

```rust
fn show_largest<T>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest { largest = item; } // ❌ T might not support >
    }
    largest
}
```

> **Error:** `error[E0369]: binary operation '>' cannot be applied to type 'T'`
>
> The compiler doesn't know if `T` supports comparison. It *can't* assume it.
>
> **Fix:** Add the bound: `fn show_largest<T: PartialOrd>`

### Mistake 2: Using a method that needs a bound you didn't declare

```rust
fn print_all<T>(items: &[T]) {
    for item in items {
        println!("{}", item); // ❌ T might not implement Display
    }
}
```

> **Error:** `error[E0277]: 'T' doesn't implement 'std::fmt::Display'`
>
> **Fix:** `fn print_all<T: std::fmt::Display>(items: &[T])`
>
> The compiler's error message will usually tell you exactly which bound to add.

### Mistake 3: Trying to use a concrete method on a generic

```rust
fn get_len<T>(item: T) -> usize {
    item.len() // ❌ only works for String, &str, Vec — not all T
}
```

> **Error:** `error[E0599]: no method named 'len' found for type parameter 'T'`
>
> **Fix:** Either constrain `T` to a trait that provides `len()`, or accept a concrete type, or define your own trait with a `len()` method and bound `T` to it.

---

## Try Yourself 🦀

1. **Generic min:** Write a `fn smallest<T: PartialOrd>(list: &[T]) -> &T` that returns the smallest item in a slice. Test with `&[i32]`, `&[f64]`, and `&[char]`.

2. **Generic struct:** Create a `#[derive(Debug)] struct MinMax<T>` with fields `min: T` and `max: T`. Add a `new(list: &[T]) -> Self` constructor that finds both in one pass. Add a `range(&self) -> T` method when `T: Copy + std::ops::Sub<Output = T>`.

3. **Multiple bounds:** Write `fn debug_and_display<T: std::fmt::Debug + std::fmt::Display>(val: T)` that prints both `{}` and `{:?}` representations. Test with `42i32` and `"hello"`.

4. **`where` clause:** Rewrite the signature from exercise 3 using a `where` clause instead of inline bounds.

5. **Conditional impl:** Create a `struct Cached<T> { value: T, label: String }`. Add a `show()` method only when `T: std::fmt::Display`. Add a `debug_show()` method only when `T: std::fmt::Debug`. Test that you can only call the appropriate method.

6. **Generic Stack:** Extend the `Stack<T>` from Part 4 — add a `fn contains(&self, item: &T) -> bool` method that works only when `T: PartialEq`. Test it.

7. **Demystify std:** Look at the signature for `Vec::sort_by_key` in the [Rust docs](https://doc.rust-lang.org/std/vec/struct.Vec.html). Break down each type parameter and bound. What does `K: Ord` mean? Why is `F: FnMut(&T) -> K` needed?

---

## 🧠 Memory Technique

> **GENERICS = COOKIE CUTTER 🍪**
>
> The cutter (function/struct definition) stays the same.
> The dough (concrete type) changes each time.
> Trait bounds = "this cutter only works on dough that can be cut" (i.e., meets a requirement).
>
> At compile time, Rust stamps out one cutter-shape per dough type used.
> At runtime, there are only concrete cookies — no generic ones.
>
> **If the compiler complains about T:** ask "what does T need to be able to do?" and add that trait bound.

---

## FAQ

**Q: When should I use generics vs trait objects (`dyn Trait`)?**
Default to generics (`impl Trait` / `T: Trait`). They're faster (monomorphized, zero runtime cost) and simpler to reason about. Use `dyn Trait` when you need to store *different* concrete types in the same collection, or return different types from a function at runtime.

**Q: Can a generic have multiple type parameters?**
Yes: `fn zip<A, B>(a: A, b: B) -> (A, B)`. Each gets its own bounds if needed. Standard library types like `HashMap<K, V>` and `Result<T, E>` use two.

**Q: What does `<T: 'static>` mean? I see it sometimes.**
The `'static` lifetime bound means "T contains no borrowed references that could expire" — T is either owned data or a reference that lives for the whole program. It comes up when spawning threads (which need data that outlives the current scope).

**Q: Why does Rust binary size grow with generics?**
Monomorphization stamps out a separate copy of the function for each concrete type. If you call `largest` with `i32`, `f64`, `char`, and `u8`, you get four copies in the binary. This is usually fine — the copies are small and the performance gain is worth it. If binary size is critical, `dyn Trait` produces a single copy.

**Q: What is a "blanket implementation"?**
A trait implementation over *all* types matching a bound. The standard library does this for `Display`:
```rust
// Implement ToString for any type that implements Display
impl<T: Display> ToString for T {
    fn to_string(&self) -> String { ... }
}
```
That's why calling `.to_string()` works on `42i32`, `3.14f64`, `true`, and anything else implementing `Display` — one blanket impl covers them all.

**Q: `T: Trait` vs `impl Trait` — which should I use?**
They're equivalent for simple cases. Use `impl Trait` for cleaner signatures when the generic is only used once. Use `T: Trait` (explicit type parameter) when: you need `T` in more than one position, you need to name the type in a `where` clause, or you're building a generic struct/enum.

---

## Cheat Card — Generics

```
┌───────────────────────────────────────────────────────────────┐
│  CARD 14: GENERICS                                            │
│  "One definition. Many types. Zero runtime cost."            │
├──────────────────────────────┬────────────────────────────────┤
│  fn f<T>(x: T)               │  Generic function              │
│  fn f<T: Bound>(x: T)        │  With trait bound              │
│  fn f<T>(x: T) where T: Bound│  With where clause             │
│  struct S<T> { val: T }      │  Generic struct                │
│  impl<T> S<T> { ... }        │  Methods for all T             │
│  impl<T: Bound> S<T> { ... } │  Methods for T meeting Bound   │
│  fn f(x: &impl Trait)        │  Sugar for &T where T: Trait   │
├──────────────────────────────┴────────────────────────────────┤
│  MULTIPLE BOUNDS                                              │
│  T: Display + Debug + Clone   (inline, simple)                │
│  where T: Display, U: Debug   (where clause, complex)         │
├───────────────────────────────────────────────────────────────┤
│  MONOMORPHIZATION (zero runtime cost)                         │
│  largest<i32>  ─────────────►  fn largest_i32() { ... }      │
│  largest<f64>  ─────────────►  fn largest_f64() { ... }      │
│  Compiler generates one function per concrete type used.      │
│  At runtime: no generics exist. Only concrete code.           │
├───────────────────────────────────────────────────────────────┤
│  GENERICS vs DYN TRAIT                                        │
│  Generics → fast, compile-time, one type per site             │
│  dyn Trait → flexible, runtime, mixes types in Vec            │
├───────────────────────────────────────────────────────────────┤
│  🧠 COOKIE CUTTER — same shape, different dough               │
│  ⚠️  Compiler error about T? Ask: "what does T need to do?"   │
│     Then add that trait as a bound: T: WhatItNeedsToDo        │
└───────────────────────────────────────────────────────────────┘
```

---

*Next: [Chapter 8 — Closures & Iterators: Rust's Functional Side](08_closures_iterators.md)*
*Previous: [Chapter 6 — Traits](06_traits.md)*
