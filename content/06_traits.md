# Chapter 6 — Traits: Job Descriptions for Types

> "The strength of Rust's type system isn't just what types *are* — it's what they can *do*."

You've built structs and enums. Now it's time to make them talk to each other — and to the rest of Rust — through a shared language called **traits**.

This chapter is the gateway to idiomatic Rust. After this, generics, iterators, smart pointers, and even error handling will start making much deeper sense.

---

## The Analogy: A Job Description

Imagine you're hiring for a role. You don't care who the person is (their name, age, background) — you care what they can **do**: speak English, drive a truck, debug code.

A **trait** is exactly that: a formal job description. It says:

> "Any type that wants to be a `Printable` must be able to `print_info`. I don't care what *kind* of type you are — as long as you can do that job."

```
TRAIT: Describable          IMPLEMENTORS
┌──────────────────┐        ┌────────────────────┐
│  + describe()    │ ◄──────│  Book              │
│  + word_count()  │ ◄──────│  Podcast           │
└──────────────────┘ ◄──────│  Article           │
                            └────────────────────┘
Different types. Same interface. Code that needs a Describable
doesn't care which one it gets.
```

---

## Part 1: Defining and Implementing Traits

### Defining a Trait

```rust
// Define the "job description"
trait Greet {
    fn hello(&self) -> String;          // required — every implementor must define this
    fn goodbye(&self) -> String {       // default — implementors can override or keep it
        String::from("Goodbye!")
    }
}
```

`hello` is **required** — no default, every type must provide its own version.
`goodbye` has a **default implementation** — types can use it as-is or override it.

### Implementing a Trait

```rust
struct Person {
    name: String,
}

struct Robot {
    model: String,
}

impl Greet for Person {
    fn hello(&self) -> String {
        format!("Hi, I'm {}!", self.name)
    }
    // uses default goodbye()
}

impl Greet for Robot {
    fn hello(&self) -> String {
        format!("HELLO. I AM MODEL {}.", self.model)
    }
    fn goodbye(&self) -> String {           // overrides the default
        String::from("SHUTTING DOWN.")
    }
}

fn main() {
    let alice = Person { name: String::from("Alice") };
    let r2d2  = Robot  { model: String::from("R2-D2") };

    println!("{}", alice.hello());      // Hi, I'm Alice!
    println!("{}", alice.goodbye());    // Goodbye!  ← default
    println!("{}", r2d2.hello());       // HELLO. I AM MODEL R2-D2.
    println!("{}", r2d2.goodbye());     // SHUTTING DOWN.  ← overridden
}
```

---

## Part 2: Traits as Function Parameters

This is where traits become genuinely powerful. Instead of writing one function for `Person` and another for `Robot`, you write one function that accepts **any type implementing `Greet`**:

### Syntax 1: `impl Trait` (clean, preferred for simple cases)

```rust
fn print_greeting(entity: &impl Greet) {
    println!("{}", entity.hello());
}

fn main() {
    let alice = Person { name: String::from("Alice") };
    let r2d2  = Robot  { model: String::from("R2-D2") };

    print_greeting(&alice);   // works ✅
    print_greeting(&r2d2);    // works ✅ — same function, different type
}
```

### Syntax 2: Trait Bound (needed for generics — previewing Chapter 7)

```rust
fn print_greeting<T: Greet>(entity: &T) {
    println!("{}", entity.hello());
}
```

These two are **equivalent** in simple cases. `impl Trait` is terser; `T: Greet` is needed when you use `T` more than once or in return position. You'll use both regularly.

### Returning `impl Trait`

```rust
// "I'll return something that can Greet — you don't need to know exactly what"
fn make_greeter(formal: bool) -> impl Greet {
    if formal {
        Person { name: String::from("Butler") }
    } else {
        Person { name: String::from("Buddy") }
    }
}
```

> ⚠️ **Limitation: both branches must return the same concrete type.** The `impl Trait` return position is resolved at compile time — Rust needs to know one concrete type for the whole function.

**See the limit in action — what if you try to return two different types?**

```rust
// ❌ This does NOT compile — each branch returns a different concrete type
trait Greet { fn hello(&self) -> String; }
struct Person { name: String }
struct Robot  { model: String }
impl Greet for Person { fn hello(&self) -> String { format!("Hi, I'm {}!", self.name) } }
impl Greet for Robot  { fn hello(&self) -> String { format!("HELLO. {}.", self.model) } }

fn make_greeter_broken(formal: bool) -> impl Greet {
    if formal {
        Person { name: String::from("Butler") }      // type: Person
    } else {
        Robot { model: String::from("RX-7") }        // ❌ type: Robot — E0308 mismatch
    }
}
fn main() { let _ = make_greeter_broken(true); }
```

> **Error:** `error[E0308]: 'if' and 'else' have incompatible types`
>
> The `if` arm is `Person`, the `else` arm is `Robot`. Rust can't pick one concrete type for the return — it would need to know at compile time, and here it depends on a runtime condition.

**Fix: use `Box<dyn Greet>` to let the concrete type be resolved at runtime:**

```rust
// ✅ Box<dyn Greet> allows returning different concrete types
trait Greet { fn hello(&self) -> String; }
struct Person { name: String }
struct Robot  { model: String }
impl Greet for Person { fn hello(&self) -> String { format!("Hi, I'm {}!", self.name) } }
impl Greet for Robot  { fn hello(&self) -> String { format!("HELLO. I AM MODEL {}.", self.model) } }

fn make_greeter(formal: bool) -> Box<dyn Greet> {
    if formal {
        Box::new(Person { name: String::from("Butler") })
    } else {
        Box::new(Robot { model: String::from("RX-7") })
    }
}

fn main() {
    let g = make_greeter(true);
    println!("{}", g.hello());   // Hi, I'm Butler!
    let g2 = make_greeter(false);
    println!("{}", g2.hello());  // HELLO. I AM MODEL RX-7.
}
```

This is exactly the bridge to Part 4 — when the concrete type isn't known until runtime, `Box<dyn Trait>` is the right tool.

---

## Part 3: Derive vs Manual `impl` — Free Traits

Rust can auto-generate many common traits for you with `#[derive(...)]`. You've seen `Debug` and `Clone` — here are the ones you'll use most:

```rust
#[derive(Debug, Clone, PartialEq, Default)]
struct Point {
    x: f64,
    y: f64,
}

fn main() {
    let p1 = Point { x: 1.0, y: 2.0 };
    let p2 = p1.clone();                    // Clone ✅
    println!("{:?}", p1);                   // Debug ✅ → Point { x: 1.0, y: 2.0 }
    println!("{}", p1 == p2);               // PartialEq ✅ → true
    let origin = Point::default();          // Default ✅ → Point { x: 0.0, y: 0.0 }
    println!("{:?}", origin);
}
```

### What each derive gives you

```
┌─────────────────┬────────────────────────────────────────────────────┐
│  Derive         │  What it enables                                   │
├─────────────────┼────────────────────────────────────────────────────┤
│  Debug          │  {:?} and {:#?} printing                           │
│  Clone          │  .clone() — explicit deep copy                     │
│  Copy           │  Auto-copy on assignment (like integers)           │
│  PartialEq      │  == and !=  comparisons                            │
│  Eq             │  Full equality (use with PartialEq, e.g. HashMap)  │
│  PartialOrd     │  <, <=, >, >= comparisons                          │
│  Ord            │  Total ordering — .sort() on Vec<T>                │
│  Hash           │  Can be used as a HashMap key                      │
│  Default        │  Type::default() — zero/empty value                │
└─────────────────┴────────────────────────────────────────────────────┘
```

### When to implement manually

Derive works when all fields also implement the trait. Sometimes you need custom logic:

```rust
use std::fmt;

struct Temperature {
    celsius: f64,
}

// Custom Display — derive can't do this (it doesn't know how you want formatting)
impl fmt::Display for Temperature {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:.1}°C ({:.1}°F)", self.celsius, self.celsius * 9.0/5.0 + 32.0)
    }
}

fn main() {
    let t = Temperature { celsius: 22.5 };
    println!("{}", t);   // 22.5°C (72.5°F)
}
```

> `Display` is the trait behind `{}` formatting. `Debug` is behind `{:?}`. You implement `Display` when you care how your type looks to end users; `Debug` is for developers.

---

## Part 4: Trait Objects — `dyn Trait`

So far, traits have been **static dispatch** — the compiler knows at compile time exactly which type it's dealing with, generates optimised code, zero runtime cost.

But what if you need a **collection of mixed types** that all implement the same trait?

```rust
fn main() {
    // This does NOT compile — Vec can only hold one type
    let greeters: Vec<???> = vec![
        Person { name: String::from("Alice") },
        Robot  { model: String::from("R2") },
    ];
}
```

The solution is a **trait object**: a pointer to *something* that implements the trait, where the exact type is erased at compile time and resolved at runtime.

```rust
fn main() {
    // Box<dyn Greet> = "a heap-allocated thing that can Greet"
    let greeters: Vec<Box<dyn Greet>> = vec![
        Box::new(Person { name: String::from("Alice") }),
        Box::new(Robot  { model: String::from("R2") }),
    ];

    for g in &greeters {
        println!("{}", g.hello());
    }
}
```

```
Hi, I'm Alice!
HELLO. I AM MODEL R2.
```

### When to use `dyn Trait` vs `impl Trait`

```
┌─────────────────────────────────┬──────────────────────────────────┐
│  impl Trait / T: Trait          │  Box<dyn Trait>                  │
│  (static dispatch)              │  (dynamic dispatch)              │
├─────────────────────────────────┼──────────────────────────────────┤
│  Type known at compile time     │  Type known only at runtime      │
│  Zero runtime cost              │  Small overhead (pointer lookup) │
│  Can't mix types in a Vec       │  Can mix types in a Vec          │
│  Use: functions, generics       │  Use: collections, plugin systems│
└─────────────────────────────────┴──────────────────────────────────┘
```

---

## 🔍 Deep Dive — What's Happening at the Machine Level

### Static Dispatch: Monomorphization

When you write `fn f(x: &impl Greet)`, the Rust compiler creates **a separate copy of the function for every concrete type you pass**:

```
Source code:        Compiled to:
                    fn f_for_Person(x: &Person) { ... }
fn f(x: &impl Greet) ───────────► fn f_for_Robot(x: &Robot)  { ... }
                    (one copy per concrete type, generated at compile time)
```

This process is called **monomorphization**. The result is code as fast as if you'd written separate functions by hand — because you effectively did, just without the repetition. No runtime lookup. No overhead.

### Dynamic Dispatch: vtables

When you write `Box<dyn Greet>`, the type information is **erased**. Instead, a **vtable** (virtual method table) is created — a small array of function pointers, one per trait method:

```
Box<dyn Greet> in memory:
┌──────────────────────────────────────────────────────┐
│  FAT POINTER (16 bytes on 64-bit)                    │
│  ┌─────────────────┬────────────────────────────┐    │
│  │  data ptr       │  vtable ptr                │    │
│  │  → heap object  │  → [hello_fn, goodbye_fn]  │    │
│  └─────────────────┴────────────────────────────┘    │
└──────────────────────────────────────────────────────┘

vtable (lives in read-only memory):
┌──────────────────┬────────────────┐
│  hello:          │  0x4A3F... (→ Robot::hello or Person::hello)
│  goodbye:        │  0x5C2E... (→ Robot::goodbye or Person::goodbye)
│  drop:           │  0x6D1A... (→ destructor)
└──────────────────┴────────────────┘
```

Calling `g.hello()` now takes **two pointer dereferences**: one to find the vtable, one to call the function. This is why dynamic dispatch has a small but real runtime cost — and why you don't want it on a hot path in performance-critical code. But for most programs, it's negligible and the flexibility is worth it.

---

## Break It On Purpose

### Mistake 1: Calling a trait method without bringing the trait into scope

```rust
// ❌ Missing `use std::fmt::Write;` — the trait isn't in scope
fn main() {
    let mut s = String::new();
    write!(s, "hello {}", 42); // trait method not visible without the `use`
    println!("{}", s);
}
```

> **Error:** `error[E0599]: no method named 'write_fmt' found for struct 'String'`
>
> The method exists — but only if you've imported the trait. **You must `use` a trait to call its methods.** This is a deliberate design: Rust won't silently bring in methods you didn't ask for.
>
> **Fix:** Add `use std::fmt::Write;` at the top of your file:

```rust
use std::fmt::Write; // ✅ now the trait's methods are in scope

fn main() {
    let mut s = String::new();
    write!(s, "hello {}", 42).unwrap();
    println!("{}", s); // hello 42
}
```

### Mistake 2: The Orphan Rule

```rust
// In your crate:
impl std::fmt::Display for Vec<i32> { // ❌ ORPHAN RULE VIOLATION
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{:?}", self)
    }
}
```

> **Error:** `error[E0117]: only traits defined in the current crate can be implemented for types defined outside of the crate`
>
> **The Orphan Rule:** You can only implement a trait for a type if **at least one of** (the trait OR the type) is defined in *your* crate. You can't implement `Display` (standard library) for `Vec<i32>` (also standard library) — that would create conflicts if two crates did it.
>
> **Fix:** Either define your own wrapper type (`struct MyVec(Vec<i32>)`) or define your own trait.

### Mistake 3: Object-unsafe trait used as `dyn`

```rust
trait Clone2 {
    fn clone(&self) -> Self; // returns `Self` — not object-safe!
}

fn use_it(x: &dyn Clone2) {} // ❌ won't compile
```

> **Error:** `error[E0038]: the trait 'Clone2' cannot be made into an object`
>
> A trait is **object-safe** only if its methods don't return `Self` or use generic type parameters. That's because with a trait object, the concrete type is erased — Rust can't know the size of `Self` at runtime.
>
> **Fix:** Use `impl Trait` (static dispatch) instead of `dyn Trait` for traits involving `Self`.

---

## Try Yourself 🦀

Open the [Rust Playground](https://play.rust-lang.org) for each exercise.

1. **Define your own trait:** Create a `Summary` trait with a required `summarize(&self) -> String` method and a default `preview(&self) -> String` method that returns the first 50 chars of `summarize()`. Implement it for a `NewsArticle` struct and a `Tweet` struct.

2. **Default implementations:** Add a `word_count(&self) -> usize` default method to `Summary` that counts the words in `summarize()`. Confirm it works without re-implementing it on `NewsArticle` or `Tweet`.

3. **Trait as parameter:** Write a `notify(item: &impl Summary)` function that prints a formatted notification using the item's `summarize()`. Call it with both a `NewsArticle` and a `Tweet`.

4. **Derive and compare:** Create a `#[derive(Debug, Clone, PartialEq)]` struct `Colour { r: u8, g: u8, b: u8 }`. Verify you can clone it, print it with `{:?}`, and compare two instances with `==`.

5. **Dynamic dispatch:** Create a `Vec<Box<dyn Summary>>` containing a mix of `NewsArticle` and `Tweet` values. Iterate over it and print each item's `summarize()`. What size is `Box<dyn Summary>`? Check with `std::mem::size_of::<Box<dyn Summary>>()`.

6. **Orphan rule exploration:** Try to implement `Display` for `Vec<String>` and read the error. Then create a newtype wrapper `struct StringList(Vec<String>)` and implement `Display` on *that*. Confirm it compiles.

7. **`Display` vs `Debug`:** Implement both `Display` and `Debug` for a `Fraction { numerator: i32, denominator: i32 }` struct. `Display` should render as `"3/4"`, `Debug` as `"Fraction { 3, 4 }"`. Use both `{}` and `{:?}` in `println!`.

---

## 🧠 Memory Technique

> **TRAIT = JOB AD. IMPL = HIRING. `use` = SHOWING UP FOR WORK.**
>
> - Write a job ad (`trait Foo { fn bar(&self); }`) — describe what a type must do.
> - Hire a candidate (`impl Foo for MyType { fn bar(&self) { ... } }`) — teach the type to do it.
> - Show up for work (`use my_module::Foo;`) — bring the trait into scope before calling its methods.
>
> If a method seems to vanish, you probably forgot to show up for work.

---

## FAQ

**Q: What's the difference between a trait and an interface (Java/C#/TypeScript)?**
Very similar concept. Key Rust differences: (1) you can implement traits for types you didn't write (within the orphan rule), (2) default implementations are fully supported, (3) Rust traits have no inheritance, (4) the distinction between static/dynamic dispatch (`impl Trait` vs `dyn Trait`) is explicit.

**Q: Why do I need `use SomeTrait;` just to call its methods?**
Rust only brings into scope the methods of traits you explicitly import. This prevents two different crates from accidentally adding methods with the same name to your types without you knowing.

**Q: When should I use `Box<dyn Trait>` vs `impl Trait`?**
Use `impl Trait` (static dispatch) as the default — it's faster and simpler. Switch to `Box<dyn Trait>` (dynamic dispatch) when you need to: store mixed types in a collection, return different concrete types from a function, or build plugin-style systems where types are determined at runtime.

**Q: Can a struct implement multiple traits?**
Yes — as many as you like. `impl Greet for MyType {}` and `impl Display for MyType {}` are completely independent. This is Rust's alternative to multiple inheritance.

**Q: What's `Sized`? I keep seeing it in error messages.**
`Sized` is a special auto-trait meaning "this type has a known size at compile time." Almost all types are `Sized` automatically. It matters for trait objects: `dyn Trait` is *not* `Sized` (the size depends on the concrete type), which is why you always need a pointer like `Box<dyn Trait>` or `&dyn Trait`.

**Q: What are "marker traits"?**
Traits with no methods — they just "mark" a type as having some property. `Copy`, `Send`, and `Sync` are the most important. `Copy` marks types that can be duplicated by a bitwise copy. `Send` marks types safe to transfer across threads. `Sync` marks types safe to share across threads. Rust uses these to enforce safe concurrency at compile time.

---

## Cheat Card — Traits

```
┌───────────────────────────────────────────────────────────────┐
│  CARD 13: TRAITS                                              │
│  "A job description any type can apply for"                   │
├──────────────────────────┬────────────────────────────────────┤
│  trait Foo { fn bar(); } │  Define the contract               │
│  impl Foo for MyType {}  │  Fulfil the contract               │
│  use path::Foo;          │  Required to call trait methods    │
│  fn f(x: &impl Foo)      │  Accept any type implementing Foo  │
│  fn f<T: Foo>(x: &T)     │  Same — needed for generics        │
│  Box<dyn Foo>            │  Heap-allocated, type-erased Foo   │
│  #[derive(Debug,Clone)]  │  Auto-implement common traits      │
├──────────────────────────┴────────────────────────────────────┤
│  STATIC DISPATCH (impl Trait)   │  DYNAMIC DISPATCH (dyn)     │
│  • Type known at compile time   │  • Type known at runtime    │
│  • Zero overhead                │  • vtable lookup cost       │
│  • One type per call site       │  • Mixes types in Vec       │
├───────────────────────────────────────────────────────────────┤
│  ORPHAN RULE                                                  │
│  You can only impl a trait for a type if YOU own              │
│  the trait OR the type (not both from external crates).       │
├───────────────────────────────────────────────────────────────┤
│  🧠  TRAIT = JOB AD   IMPL = HIRING   use = SHOW UP           │
│  ⚠️  Forgot `use SomeTrait`? Methods will seem to disappear.  │
└───────────────────────────────────────────────────────────────┘
```

---

*Next: [Chapter 7 — Generics: Write Once, Use With Many Types](07_generics.md)*
*Previous: [Mini-Projects](05_mini_projects.md)*
