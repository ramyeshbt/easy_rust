# Foundations: Ownership, Borrowing & Lifetimes

> **The moment ownership clicks, Rust stops feeling like a fight and starts feeling like a superpower.**
> Almost every Rust developer remembers that moment. This chapter is built to get you there fast.

This chapter is the **heart of Rust**. Everything else in the language is built on top of what you'll learn here. It might feel unfamiliar at first — that's normal and expected. But once it clicks, you'll wonder how you ever coded without it.

We're going to learn three concepts:

| Concept | Real-World Analogy | What It Prevents |
|---|---|---|
| **Ownership** | A library book | Two people modifying the same data simultaneously |
| **Borrowing** | Lending your car | Accessing data that no longer exists |
| **Lifetimes** | A loan period | Using borrowed data after the owner is gone |

Let's take them one at a time.

---

## Part 1: Ownership — The Library Book Rule

### The Analogy

Imagine a **library**. There's one copy of a book. When you check it out, **you own the borrowing** — no one else can check out that same copy while you have it. When you return it, someone else can take it.

Simple, right?

Rust applies this exact idea to data in memory. Every piece of data has **exactly one owner** at a time. When the owner is done, the data is automatically cleaned up. No garbage collector needed.

### First, the "Why": Where Does Your Data Live?

Before the rules, you need one piece of background. Programs store data in two places:

```
┌────────────────────────────────────────────────────────────┐
│  THE STACK                    THE HEAP                      │
│  ───────────                  ─────────                     │
│  • Fast (just move a pointer) • Flexible (any size)         │
│  • Fixed, known size          • Size decided at runtime     │
│  • Auto-cleaned when scope    • Must be explicitly freed    │
│    ends (instant)               (or leaked — a bug!)        │
│  • Stores: integers, bools,   • Stores: String contents,    │
│    chars, pointers              Vec contents, big data      │
└────────────────────────────────────────────────────────────┘
```

Here's the key picture. When you write `let s = String::from("hi");`:

```
   STACK                          HEAP
┌──────────────┐              ┌──────────┐
│ s            │              │  h  i    │
│ ┌──────────┐ │   points to  │ 68 69    │
│ │ ptr ─────┼─┼─────────────▶│          │
│ │ len = 2  │ │              └──────────┘
│ │ cap = 2  │ │
│ └──────────┘ │
└──────────────┘
```

The variable `s` on the stack is small and fixed — just a pointer, a length, and a capacity. The *actual text* lives on the heap, where it can be any size.

**This is the whole reason ownership exists.** Heap memory must be freed exactly once — not zero times (a leak), not twice (a crash). Other languages solve this with a garbage collector (slow, unpredictable) or by trusting the programmer to do it manually (error-prone — this is the C/C++ nightmare). Rust solves it with **ownership rules checked at compile time**: the compiler knows exactly when each value's owner goes away, so it frees the heap memory at precisely the right moment — for free, with zero runtime cost.

Keep this picture in your head. Every ownership rule below exists to manage that pointer-to-heap relationship safely.

### The Three Rules of Ownership

Rust's ownership system has three rules. Read them slowly — everything else flows from these:

> 1. Every value in Rust has a single **owner** (a variable).
> 2. There can only be **one owner at a time**.
> 3. When the owner goes out of scope, the value is **automatically dropped** (memory freed).

### Let's See It in Code

```rust
fn main() {
    let book = String::from("The Rust Programming Language"); // book owns this String
    println!("I'm reading: {}", book);
} // <-- book goes out of scope here. Rust automatically frees the memory. Done.
```

No `free()`. No garbage collector. The moment `book` goes out of scope (the closing `}`), Rust drops it. Clean, automatic, zero overhead.

### What Happens When You "Move" Ownership

Here's where it gets interesting. What if you assign a variable to another variable?

```rust
fn main() {
    let book = String::from("The Rust Programming Language");
    let new_owner = book; // ownership MOVES from `book` to `new_owner`

    println!("{}", new_owner); // ✅ works fine
    println!("{}", book);      // ❌ ERROR: `book` no longer owns anything!
}
```

When you write `let new_owner = book`, you're not copying the book — you're **handing it over**. `book` is now empty. The library book is in `new_owner`'s hands.

Try this in the [Rust Playground](https://play.rust-lang.org) — the compiler error message will tell you exactly what happened and why.

> **Compiler Error You'll See:**
> ```
> error[E0382]: borrow of moved value: `book`
> ```
> This is Rust saying: "You moved `book` to `new_owner`. You can't use `book` anymore."

### Why Does This Matter?

In C or C++, two variables could point to the same data. If one frees it and the other tries to use it — crash. This is called a **use-after-free bug** and it's one of the most common security vulnerabilities in software history.

Rust makes this **impossible at compile time**. The compiler catches it before your program ever runs.

#### See the Difference: The Same Bug in C vs Rust

```c
// C — compiles fine, then explodes at runtime 💥
#include <stdlib.h>
#include <stdio.h>

int main() {
    char *data = malloc(20);
    sprintf(data, "hello");

    char *alias = data;   // two pointers to the SAME memory
    free(data);           // memory freed here

    printf("%s\n", alias); // ☠️ USE-AFTER-FREE — undefined behaviour
    free(alias);           // ☠️ DOUBLE-FREE — corruption / crash
    return 0;
}
```

The C compiler says nothing. The program might print garbage, might crash, might appear to work — and might be silently exploitable by an attacker. The bug only surfaces *at runtime*, often in production.

```rust
// Rust — refuses to compile the equivalent mistake ✅
fn main() {
    let data = String::from("hello");
    let alias = data;        // ownership MOVES to `alias`; `data` is now invalid

    println!("{}", alias);   // ✅ fine — alias owns it
    println!("{}", data);    // ❌ COMPILE ERROR: borrow of moved value: `data`
}
```

```
error[E0382]: borrow of moved value: `data`
```

Rust won't even build this program. There is no "two pointers to the same memory" situation, so there's no use-after-free and no double-free — **by construction**, before the code ever runs. The bug class simply cannot exist.

### What About Simple Numbers?

You might wonder: does `let y = x` also "move" x?

```rust
fn main() {
    let x = 5;
    let y = x; // x is COPIED, not moved

    println!("x = {}, y = {}", x, y); // ✅ Both work fine
}
```

Simple types like integers, floats, and booleans are **copied** because they're tiny and cheap to duplicate. Rust handles this automatically through a trait called `Copy` — you'll learn about traits later. For now, just remember: **big, complex data moves; small, simple data copies**.

---

## Part 2: Borrowing — Lending Your Car

### The Analogy

You own a car. Your friend needs to run an errand. You lend them the car — they drive it, use it, return it. You still own the car. They just had temporary access.

**That's borrowing in Rust.**

Instead of moving ownership, you give a reference — a way to *look at* or *use* the data without taking it over.

### References: The `&` Symbol

```rust
fn main() {
    let book = String::from("The Rust Programming Language");

    read_book(&book); // lend the book — pass a REFERENCE

    println!("I still have my book: {}", book); // ✅ book still owned here
}

fn read_book(b: &String) { // b is a reference — it borrows, doesn't own
    println!("Reading: {}", b);
} // b goes out of scope, but the book is NOT dropped — we didn't own it
```

The `&` symbol means "a reference to". You're not giving `read_book` the book — you're giving it a reference, like handing someone a photocopy of the cover while you keep the original.

### Two Types of Borrows

There are two kinds of references in Rust — and the rules around them are key:

#### 1. Immutable Reference `&T` — "Look but don't touch"

```rust
fn main() {
    let book = String::from("Clean Code");

    let r1 = &book; // immutable reference
    let r2 = &book; // another immutable reference — ALLOWED

    println!("r1: {}, r2: {}", r1, r2); // ✅ fine — both just reading
}
```

**You can have as many immutable references as you want.** Everyone can look at the book at the same time — as long as nobody is writing in it.

#### 2. Mutable Reference `&mut T` — "You have the pen"

```rust
fn main() {
    let mut book = String::from("Clean Code");

    let r1 = &mut book; // mutable reference — one editor at a time
    r1.push_str(" — 2nd Edition");

    println!("{}", r1); // ✅ "Clean Code — 2nd Edition"
}
```

**You can only have ONE mutable reference at a time.** Only one person can edit the book at once — otherwise you'd have conflicting edits, which is exactly what causes data races in multi-threaded programs.

### The Golden Rule of Borrowing

Rust enforces one simple rule:

> At any given time, you can have **either**:
> - Any number of **immutable** references (`&T`)
> - **OR** exactly one **mutable** reference (`&mut T`)
> - But **never both at the same time**

This rule eliminates an entire class of bugs — **data races** — that plague multi-threaded programs in other languages. Rust makes them impossible.

### What Happens If You Break the Rule?

```rust
fn main() {
    let mut book = String::from("Clean Code");

    let r1 = &book;     // immutable borrow
    let r2 = &mut book; // ❌ ERROR: can't mutably borrow while immutably borrowed

    println!("{}", r1);
}
```

> **Compiler Error:**
> ```
> error[E0502]: cannot borrow `book` as mutable because it is also borrowed as immutable
> ```

The compiler caught a potential data race before the program even ran. That's Rust working for you.

---

## Part 3: Lifetimes — The Loan Period

### The Analogy

You lend a friend your car for the weekend. They say they'll return it Sunday. But what if you sold the car Saturday, then your friend showed up Sunday expecting to drive it?

That's a disaster. The car no longer exists. Your friend is holding a reference to something that's gone.

**Lifetimes** are Rust's way of making sure this *never happens*. They track how long references are valid and ensure a reference never outlives the data it points to.

### A Concrete Example

```rust
fn main() {
    let result;

    {
        let book = String::from("Rust in Action"); // book is created here
        result = &book; // result borrows book
    } // book is DROPPED here — it goes out of scope

    println!("{}", result); // ❌ ERROR: result refers to dropped data
}
```

> **Compiler Error:**
> ```
> error[E0597]: `book` does not live long enough
> ```

The compiler noticed: `result` holds a reference to `book`, but `book` is dropped before `result` is used. It refuses to compile this — preventing a **dangling pointer** (a reference to freed memory), one of the most dangerous bugs in systems programming.

### Lifetimes in Functions

Most of the time, Rust figures out lifetimes for you automatically. But sometimes — especially in functions that return references — you need to be explicit.

```rust
// This function takes two string slices and returns the longer one.
// The lifetime annotation 'a says:
// "the returned reference lives at least as long as both inputs"
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

fn main() {
    let s1 = String::from("long string");
    let result;
    {
        let s2 = String::from("xyz");
        result = longest(s1.as_str(), s2.as_str());
        println!("Longest: {}", result); // ✅ both s1 and s2 alive here
    }
}
```

The `'a` syntax looks strange at first — but it's just a label. It tells the compiler: "the reference I'm returning is tied to the inputs — it won't outlive them." You're not setting a time limit; you're describing a *relationship*.

### Why Can't the Compiler Just Figure It Out?

Good question — and most of the time, it *does*. Look at this `longest` function without annotations:

```rust
fn longest(x: &str, y: &str) -> &str {  // ❌ won't compile
    if x.len() > y.len() { x } else { y }
}
```

```
error[E0106]: missing lifetime specifier
help: this function's return type contains a borrowed value, but the
      signature does not say whether it is borrowed from `x` or `y`
```

The compiler is genuinely stuck. The returned reference could come from `x` *or* `y` — and they might have different lifetimes. The compiler can't guess which, so it asks *you* to clarify with `'a`. You're not doing the compiler's job; you're giving it the one fact it cannot deduce.

### The "Lifetime Elision" Shortcut

For the common cases, Rust applies automatic rules called **lifetime elision** so you never type `'a`. The simplest rule: **if a function takes exactly one reference and returns a reference, the output borrows from that input.**

```rust
// No annotation needed — only one input reference, so the
// compiler knows the output must come from it.
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &b) in bytes.iter().enumerate() {
        if b == b' ' {
            return &s[..i];
        }
    }
    s
}
```

This compiles cleanly with zero lifetime syntax. The `longest` function needed annotations only because it had **two** input references and the compiler couldn't pick.

### When Will You Actually Write Lifetimes?

Be honest with yourself about the 90/10 rule here:

| Situation | Do you write `'a`? |
|-----------|--------------------|
| Functions that take/return owned values (`String`, `Vec`) | ❌ Never |
| Functions with one reference in, one reference out | ❌ Elided automatically |
| Functions with multiple references where output borrows | ✅ Yes |
| Structs that *hold* references | ✅ Yes |
| Most beginner code | ❌ Almost never |

> **Don't worry if lifetimes feel abstract right now.** Most everyday Rust code doesn't require explicit lifetime annotations — the compiler infers them. You'll only write them in specific situations, and the compiler will tell you *exactly* when with a clear error message. Many Rust developers go weeks before writing their first `'a`. Understand the *concept* now; the *syntax* will come when you need it.

---

## The Big Picture: How These Three Work Together

Ownership, borrowing, and lifetimes aren't three separate features — they're one unified system called the **borrow checker**. It runs at compile time and guarantees:

- No use-after-free bugs
- No dangling pointers
- No data races
- No double-frees (freeing memory twice)

All without a garbage collector. All with zero runtime cost.

Let's see all three working together in a realistic example:

```rust
fn summarize(text: &str) -> String {
    // `text` is borrowed (we don't own it)
    // We return a brand-new String — owned by the caller
    let words: Vec<&str> = text.split_whitespace().collect();
    let first_five = words[..5.min(words.len())].join(" ");
    format!("{}...", first_five)
}

fn main() {
    let article = String::from("Rust is a systems programming language focused on safety speed and concurrency");

    // We borrow `article` — ownership stays here
    let preview = summarize(&article);

    // Both are usable — article wasn't moved
    println!("Full: {}", article);
    println!("Preview: {}", preview);
}
```

```
Full: Rust is a systems programming language focused on safety speed and concurrency
Preview: Rust is a systems programming...
```

`article` is borrowed by `summarize`. The function reads it and returns a new, owned `String`. The original is untouched. Clean, clear, zero ambiguity.

---

## Common Beginner Mistakes (And How to Fix Them)

These are the errors every new Rustacean hits. Seeing them now will save you hours later.

### Mistake 1: Using a value after moving it

```rust
let s = String::from("hello");
let t = s;
println!("{}", s); // ❌ s was moved to t
```
**Fix:** Clone if you need both, or use a reference:
```rust
let s = String::from("hello");
let t = s.clone(); // explicit copy
println!("{} and {}", s, t); // ✅
```

### Mistake 2: Mutable and immutable references at the same time

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];   // immutable borrow
v.push(4);           // ❌ mutable borrow while immutable exists
println!("{}", first);
```
**Fix:** Finish using the immutable borrow before mutating:
```rust
let mut v = vec![1, 2, 3];
let first_val = v[0]; // copy the value, not a reference
v.push(4);            // ✅ no active borrow
println!("{}", first_val);
```

### Mistake 3: Returning a reference to a local variable

```rust
fn make_greeting() -> &String { // ❌ returning reference to local data
    let s = String::from("hello");
    &s // s will be dropped when the function ends!
}
```
**Fix:** Return the owned value:
```rust
fn make_greeting() -> String { // ✅ return ownership
    String::from("hello")
}
```

---

## Visualizing the Borrow Checker

Think of the borrow checker as a **traffic controller** for your data:

```
Data: [ "hello" ]
         |
     OWNER: s
         |
    +---------+----------+
    |                    |
  READ?              WRITE?
(&s allowed          (&mut s allowed
 many times)          only ONCE,
                    no reads at
                    same time)
```

One lane for writing, unlimited lanes for reading — but never both at once. That's it. That's the whole idea.

---

## Quick Recap — All Three Concepts in One View

| Concept | Analogy | Plain English | What It Prevents | You Write… |
|---|---|---|---|---|
| **Ownership** | A library book | Every value has one owner. When the owner is gone, the value is gone. | Double-frees, memory leaks | `let`, moves, `.clone()` |
| **Borrowing** | Lending your car | Lend your data. Readers: as many as you want. Writers: only one, and no readers at the same time. | Data races, conflicting writes | `&t`, `&mut t` |
| **Lifetimes** | A loan period | A borrowed reference can never outlive the data it borrows. The compiler checks this for you. | Dangling pointers (use-after-free) | usually nothing; `'a` when ambiguous |

**The unifying idea:** all three are one system — the **borrow checker** — answering one question at compile time: *"Is every reference guaranteed to point at valid, non-conflicting data for as long as it's used?"* If yes, your program compiles. If no, you get an error instead of a 2 a.m. production crash.

---

## Try It Yourself 🦀

Open the [Rust Playground](https://play.rust-lang.org) and try these exercises:

1. **Move:** Create a `String`, move it to another variable, then try to print the original. Read the error carefully — what does it tell you?
2. **Borrow to read:** Write a function that takes a `&String`, reads it, and returns nothing. Confirm the original is still usable after the call.
3. **Break the golden rule:** Try creating both an immutable and a mutable reference to the same variable at the same time. What does the compiler say?
4. **Fix a move error:** Take the broken code from exercise 1 and make it work two different ways — once with `.clone()`, once with a `&` reference. Which feels more appropriate, and why?
5. **Mutate through a borrow:** Write a function `add_exclamation(s: &mut String)` that appends `"!"`. Call it three times on the same string and print the result.
6. **Trigger a lifetime error:** Recreate the "dangling reference" example (a reference that outlives its data) and read the `does not live long enough` error. Then fix it by moving the `println!` inside the inner scope.
7. **Stretch:** Write the `longest` function from the lifetimes section *without* the `'a` annotations. Read the error. Then add them back and watch it compile. You just experienced exactly why lifetimes exist.

The errors Rust gives you aren't walls — they're **signposts**. Each one is teaching you something about how memory works.

---

## What's Coming Next

You've now grasped the foundation that makes Rust unique. From here, everything gets more *fun* — you'll use what you know to build real things.

Next up: **Runnable Examples for Every Concept** — we'll take ownership, borrowing, and lifetimes and write small programs you can run, modify, and break on purpose to deepen your understanding.

> The best way to learn Rust is to make the compiler angry, read what it says, and fix it. Every error is a free lesson.

---

*Next: [Playground Examples — Learning by Doing](03_playground_examples.md)*
*Previous: [Why Rust? The Hook](01_hook.md)*
