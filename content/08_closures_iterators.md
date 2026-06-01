# Chapter 8 — Closures & Iterators: Rust's Functional Side

> "The most powerful programs aren't the ones that do more — they're the ones
> that describe *what* to do and let the machine figure out *how*."

You already know how to write loops. This chapter will make you question whether
you ever need to write one again.

**Closures** are functions that carry their environment with them — like a chef
packing a to-go bag of ingredients before leaving the kitchen. **Iterators** are
lazy assembly lines that process sequences one item at a time, doing zero work
until you ask for results. Together they form the engine behind nearly all
idiomatic Rust code.

```
THE BIG PICTURE

  ┌─────────────────────────────────────────────────────────────────────┐
  │                                                                     │
  │   CLOSURE                      ITERATOR                            │
  │  "A function with a          "A lazy sequence                      │
  │   backpack of variables"      processor"                           │
  │                                                                     │
  │   |x| x * factor  ────────►  .map(|x| x * factor)                 │
  │        ▲                           │                               │
  │        │ captures 'factor'         ▼                               │
  │        │ from surroundings    .filter(|x| *x > threshold)         │
  │                                    │                               │
  │                                    ▼                               │
  │                               .collect::<Vec<_>>()   ← consumer   │
  │                                                                     │
  │   Together: replace 90% of hand-written for loops                  │
  │   with zero runtime overhead (monomorphized, LLVM-fused)           │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## Section Map

| # | Section | Core idea |
|---|---------|-----------|
| 1 | [Closures — The To-Go Bag](#section-1-closures--the-to-go-bag) | Pack variables, carry them anywhere |
| 2 | [The Ownership Hierarchy](#section-2-the-ownership-hierarchy-fn--fnmut--fnonce) | Fn / FnMut / FnOnce |
| 3 | [System Deep Dive: Closures Are Structs](#section-3--system-deep-dive-closures-are-anonymous-structs) | The compiler's secret |
| 4 | [⚠️ Closure Danger Zone](#section-4--danger-zone--closure-traps) | Three traps that will catch you |
| 5 | [Iterators — The Lazy Assembly Line](#section-5-iterators--the-lazy-assembly-line) | Nothing moves until a consumer pulls |
| 6 | [Three Ways to Iterate](#section-6-three-ways-to-iterate) | `.iter()` vs `.iter_mut()` vs `.into_iter()` |
| 7 | [Adapters & Consumers](#section-7-adapters--consumers) | Build pipelines, drain results |
| 8 | [⚠️ Iterator Danger Zone](#section-8--danger-zone--iterator-traps) | Three traps you will definitely hit |
| 9 | [Deep Dive: Zero-Cost Abstraction](#section-9--deep-dive-zero-cost-abstraction) | Iterators compile to tight loops |
| 10 | [Closures + Iterators Together](#section-10-closures--iterators-together-word-frequency-counter) | Real-world capstone |
| 11 | [Break It On Purpose](#break-it-on-purpose) | E0382, E0505, E0277 |

---

## Section 1: Closures — The To-Go Bag

### The Analogy

Imagine a restaurant kitchen. A customer orders food to go. The chef doesn't
hand the customer a copy of the whole kitchen — she packs a **to-go bag**
containing exactly the ingredients the customer needs, and the customer can
take that bag anywhere: home, office, a park bench.

A **closure** is that to-go bag. It's a function that captures (packs) the
variables it needs from the surrounding code and carries them with it — to be
called later, passed to other functions, or stored in a struct.

```
Surrounding scope:
  name = "Alice"       tax_rate = 0.08       discount = 15
       │                    │                      │
       ▼ (borrowed)         ▼ (copied — f64)       ▼ (moved — owns it)
  ┌────────────────────────────────────────────────────────────┐
  │  TO-GO BAG (closure)                                       │
  │                                                            │
  │  captured: &name     → reads the original                  │
  │            tax_rate  → has its own copy (f64 is Copy)      │
  │            discount  → has taken full ownership            │
  └────────────────────────────────────────────────────────────┘
       │
       ▼  the bag can travel: passed to thread::spawn, stored in Vec,
          returned from a function — the variables travel with it
```

### Closure Syntax

Closures use `|pipes|` instead of `(parens)` for parameters. Everything else
follows the same rules as a function:

```rust
// A regular named function
fn add_one_fn(x: i32) -> i32 { x + 1 }

// The same logic as a closure — four equivalent spellings:
let add_one = |x: i32| -> i32 { x + 1 };  // fully annotated
let add_one = |x: i32| x + 1;             // return type inferred
let add_one = |x| x + 1;                  // both inferred (most common)
let add_one = |x| { x + 1 };             // braces optional for single expr

fn main() {
    println!("{}", add_one(5));   // 6
    println!("{}", (|x| x * x)(4));  // 16 — immediate invocation
}
```

### Capturing Variables: By Reference and By Move

The big difference from a regular function: a closure can *see and use* variables
from the surrounding scope without them being passed as parameters.

```rust
fn main() {
    let greeting = String::from("Hello");
    let punctuation = '!';   // char is Copy

    // Capture by reference — greeting is borrowed, still usable after
    let say_hi = |name: &str| {
        println!("{}, {}{}", greeting, name, punctuation);
    };
    say_hi("Alice");   // Hello, Alice!
    say_hi("Bob");     // Hello, Bob!
    println!("{}", greeting);  // ✅ still here

    // Capture by move — force ownership into the closure
    let farewell = String::from("Goodbye");
    let say_bye = move |name: &str| {
        println!("{}, {}!", farewell, name);   // farewell is now owned by closure
    };
    say_bye("Carol");  // Goodbye, Carol!
    // println!("{}", farewell);  // would be E0382 — farewell was moved
}
```

**When do you need `move`?**
When the closure must outlive the current scope — most commonly when passing a
closure to a thread (the thread may run after the current function returns, so
borrowed references would dangle):

```rust
use std::thread;

fn main() {
    let message = String::from("Hello from the closure!");

    // Without `move`, this would fail — message might be dropped before thread runs
    let handle = thread::spawn(move || {
        println!("{}", message);  // closure owns message — safe ✅
    });

    handle.join().unwrap();
}
```

---

## Section 2: The Ownership Hierarchy — `Fn` / `FnMut` / `FnOnce`

The three closure traits form a strict **hierarchy** based on what the closure
does with its captured variables. Understanding this hierarchy unlocks why the
compiler rejects some closure uses and accepts others.

```
  MOST RESTRICTIVE (can only call once)
  ┌──────────────────────────────────────────────────────┐
  │  FnOnce   — "I consume what I captured"              │
  │             closure moves a captured value OUT       │
  │             can only be called ONCE                  │
  └──────────────────────────────────────────────────────┘
           ▲  every FnMut is also FnOnce
  ┌──────────────────────────────────────────────────────┐
  │  FnMut    — "I mutate what I captured"               │
  │             closure modifies captured values         │
  │             can be called multiple times (needs mut) │
  └──────────────────────────────────────────────────────┘
           ▲  every Fn is also FnMut and FnOnce
  ┌──────────────────────────────────────────────────────┐
  │  Fn       — "I only read what I captured"            │
  │             closure reads captured values            │
  │             can be called any number of times freely │
  └──────────────────────────────────────────────────────┘
  LEAST RESTRICTIVE (most widely usable)

  Rule: Fn ⊂ FnMut ⊂ FnOnce
  (A closure that satisfies Fn also satisfies FnMut and FnOnce)
```

**Three closures — each trait in action:**

```rust
fn main() {
    // --- Fn: reads captured value ---
    let factor = 3;
    let multiply = |x: i32| x * factor;   // only reads factor
    println!("{}", multiply(4));   // 12
    println!("{}", multiply(5));   // 15  ← can call many times ✅

    // --- FnMut: mutates captured value ---
    let mut count = 0;
    let mut increment = || {
        count += 1;   // mutates captured count
        count
    };
    println!("{}", increment());  // 1
    println!("{}", increment());  // 2
    println!("{}", increment());  // 3  ← multiple calls ✅, count keeps changing

    // --- FnOnce: moves a captured value out ---
    let name = String::from("Alice");
    let consume = || {
        let taken = name;   // moves name OUT of the closure
        println!("Consumed: {}", taken);
    };
    consume();   // ✅ first call — name is moved out
    // consume();  // ❌ second call would be E0382 — name is already gone
}
```

**Accepting closures as function parameters:**

```rust
// Fn — reads only, call as many times as you like
fn apply_twice<F: Fn(i32) -> i32>(f: F, x: i32) -> i32 {
    f(f(x))
}

// FnMut — may mutate captures, must bind as mut
fn apply_n_times<F: FnMut()>(mut f: F, n: usize) {
    for _ in 0..n { f(); }
}

// FnOnce — call it, but only once; used for one-shot callbacks
fn run_once<F: FnOnce() -> String>(f: F) -> String {
    f()
}

fn main() {
    println!("{}", apply_twice(|x| x + 3, 7));   // 13

    let mut total = 0;
    apply_n_times(|| { total += 10; }, 5);
    println!("total = {}", total);    // 50

    let msg = String::from("hello");
    let result = run_once(move || msg.to_uppercase());
    println!("{}", result);   // HELLO
}
```

---

## Section 3: 🔍 System Deep Dive — Closures Are Anonymous Structs

This is the part most Rust courses skip — and it's the key to understanding
*why* closures work exactly the way they do.

**Every closure the compiler compiles becomes a hidden struct.** The captured
variables become *fields* of that struct. The closure body becomes a method.

```rust
// What you write:
let offset = 10;
let add_offset = |x: i32| x + offset;
println!("{}", add_offset(5));  // 15

// What the compiler silently generates (conceptually):
// struct __Closure_add_offset { offset: i32 }
//
// impl Fn(i32) -> i32 for __Closure_add_offset {
//     fn call(&self, x: i32) -> i32 {
//         x + self.offset   // captured field
//     }
// }
```

```
MEMORY LAYOUT on the stack:

┌────────────────────────────────────────────────────────────────┐
│  add_offset  (the closure "object")                            │
│  ┌──────────┐                                                  │
│  │ offset:  │ 10   ← captured variable becomes a struct field  │
│  │ (i32)    │                                                  │
│  └──────────┘                                                  │
│                                                                │
│  The function code (|x| x + offset) lives in the .text        │
│  segment — NOT in this struct. The struct only holds data.     │
│                                                                │
│  Size of closure = size of all captured variables              │
│  (a closure that captures NOTHING has size 0 — ZST!)           │
└────────────────────────────────────────────────────────────────┘
```

**The three traits map directly to the three ways a method can take `self`:**

```
Trait       struct method signature     meaning
─────────────────────────────────────────────────────────────────
Fn          fn call(&self, ...)         borrows self — safe to call many times
FnMut       fn call(&mut self, ...)     mutably borrows self — data changes each call
FnOnce      fn call(self, ...)          consumes self — struct destroyed after call
```

**Proving closures are structs — size and type inspection:**

```rust
use std::mem::size_of_val;

fn main() {
    // Zero-capture closure: size = 0
    let no_capture = || println!("no captures");
    println!("no_capture size: {} bytes", size_of_val(&no_capture));    // 0

    // One captured i32: size = 4
    let x: i32 = 42;
    let one_capture = move || println!("{}", x);
    println!("one_capture size: {} bytes", size_of_val(&one_capture));  // 4

    // One captured String: size = 24 (String = ptr + len + capacity on 64-bit)
    let s = String::from("hello");
    let string_capture = move || println!("{}", s);
    println!("string_capture size: {} bytes", size_of_val(&string_capture)); // 24
}
```

This is also why two closures with the same body but different captures are
**different types** — the compiler generates a unique struct for each. You can't
store them in the same `Vec<ClosureType>` without boxing.

---

## Section 4: ⚠️ DANGER ZONE — Closure Traps

These three traps are responsible for a huge share of beginner confusion. Read
each one carefully — the compiler's error messages will make immediate sense once
you understand what's happening underneath.

---

### 💀 TRAP 1 — The Moved Variable Ghost

**The crime:** you move a value into a closure, then try to use the original.

```
   String "Alice"
       │
       │  move  ──────────────────────────────────────────────────────►
       │                                                               │
   ┌───┴───────────────────────┐         ┌──────────────────────────┐ │
   │  name (original home)     │         │  closure (new home)      │ │
   │  [ EMPTY — value is gone ]│         │  captured name: "Alice"  │◄┘
   └───────────────────────────┘         └──────────────────────────┘
         ↑
         trying to use this = GHOST REFERENCE
```

```rust
fn main() {
    let name = String::from("Alice");
    let greet = move || println!("Hello, {}!", name);  // name MOVED here
    greet();
    println!("{}", name);  // ❌ E0382 — name moved into closure above
}
```

> **Error:** `error[E0382]: borrow of moved value: 'name'`
>
> The value has left the building. Its original binding is an empty room.
>
> **Fix options:**
> 1. Clone before moving: `let greet = move || println!("Hello, {}!", name.clone());` — but `name` is then cloned INTO the closure, original stays
> 2. Borrow instead of move: remove `move`, capture by reference (valid if closure doesn't outlive the scope)
> 3. Clone the name before creating the closure: `let name_copy = name.clone(); let greet = move || println!("Hello, {}!", name_copy);` — now you have both

```rust
// ✅ Fix: capture by reference (closure doesn't outlive the scope)
fn main() {
    let name = String::from("Alice");
    let greet = || println!("Hello, {}!", name);  // borrows, doesn't own
    greet();
    println!("{}", name);  // ✅ still here
}
```

---

### 💣 TRAP 2 — The FnOnce Landmine

**The crime:** you try to call a FnOnce closure a second time — it has already
detonated and consumed everything it had.

```rust
fn main() {
    let message = String::from("BOOM");
    let explode = || {
        let _taken = message;   // moves message OUT of the closure — FnOnce
        println!("detonated!");
    };
    explode();   // ✅ first call — message consumed
    explode();   // ❌ E0382 — closure already consumed its contents
}
```

> **Error:** `error[E0382]: use of moved value: 'explode'`
>
> The closure itself was consumed on the first call. Calling it a second time
> is using a moved value. The compiler catches this before it can run.
>
> **Fix:** If you need to call it multiple times, don't move *out* of the captured
> value — use a reference or clone the data instead of taking ownership:

```rust
// ✅ Fix: read instead of move — closure becomes Fn, can call many times
fn main() {
    let message = String::from("repeated");
    let print_it = || println!("{}", message);  // borrows message — Fn
    print_it();   // ✅
    print_it();   // ✅
    print_it();   // ✅
}
```

---

### ❄️ TRAP 3 — The Borrow Freeze

**The crime:** a closure borrows a variable by reference, and that live borrow
prevents you from mutating the variable while the closure exists.

```rust
fn main() {
    let mut data = vec![1, 2, 3];

    let inspector = || println!("data has {} elements", data.len()); // immutable borrow

    data.push(4);    // ❌ E0502 — can't mutate while immutable borrow is live
    inspector();
}
```

> **Error:** `error[E0502]: cannot borrow 'data' as mutable because it is also borrowed as immutable`
>
> The closure `inspector` holds an immutable borrow of `data`. That borrow
> stays alive for as long as the closure lives. You can't mutate `data`
> while that borrow exists.
>
> **Fix:** End the borrow before mutating — either use the closure first, or
> limit the closure's scope with a block:

```rust
// ✅ Fix: use the closure before mutating
fn main() {
    let mut data = vec![1, 2, 3];
    {
        let inspector = || println!("data has {} elements", data.len());
        inspector();
    } // ← borrow ends here, inspector is dropped

    data.push(4);   // ✅ mutation now safe
    println!("after push: {:?}", data);  // [1, 2, 3, 4]
}
```

---

## Section 5: Iterators — The Lazy Assembly Line

### The Analogy

A factory assembly line has stations. Station 1 welds. Station 2 paints.
Station 3 inspects. **Nothing moves through the line until the shipping dock
(the consumer) pulls the next unit.** If shipping stops, the whole line pauses.

Rust iterators work exactly the same way:

```
RAW MATERIAL            ADAPTERS                           CONSUMER
                    (lazy — do nothing alone)
┌──────────────┐                                          ┌──────────┐
│  data source │──► [map: ×2] ──► [filter: >5] ──► [take: 3] ──► collect()
│  (Vec, file, │                                          │  results │
│  range, ...)  │                                          └──────────┘
└──────────────┘
       ▲
       │
  IMPORTANT: the adapters are IDLE until collect() pulls.
  Without a consumer: map()──►filter()──►take() = zero work done.
```

### The `Iterator` Trait

Every iterator in Rust implements one trait with one required method:

```rust
// The core of Rust's iterator system (simplified):
pub trait Iterator {
    type Item;                         // the type of thing this yields

    fn next(&mut self) -> Option<Self::Item>;  // return Some(item) or None when done

    // All adapter and consumer methods are provided HERE as defaults —
    // you only need to implement `next()` and you get them all for free.
}
```

A for loop is just `next()` in a loop — syntactic sugar:

```rust
fn main() {
    let v = vec![10, 20, 30];

    // What you write:
    for x in v.iter() {
        println!("{}", x);
    }

    // What the compiler sees:
    let mut iter = v.iter();
    loop {
        match iter.next() {
            Some(x) => println!("{}", x),
            None    => break,
        }
    }
}
```

---

## Section 6: Three Ways to Iterate

This is the section most beginners skip — and regret later. The three iteration
methods give you different *access levels* and have very different ownership consequences:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  METHOD         YIELDS       ORIGINAL VEC SURVIVES?   MODIFY ELEMENT?   │
├──────────────────────────────────────────────────────────────────────────┤
│  .iter()        &T           ✅ Yes — borrowed         ❌ No (read only) │
│  .iter_mut()    &mut T       ✅ Yes — mutably borrowed  ✅ Yes           │
│  .into_iter()   T (owned)    ❌ No  — consumed          N/A (owns it)   │
└──────────────────────────────────────────────────────────────────────────┘

  Rule of thumb:
    Reading data?          → .iter()
    Modifying in place?    → .iter_mut()
    Moving data out/away?  → .into_iter() (or just `for x in vec`)
```

**All three on the same Vec:**

```rust
fn main() {
    let mut scores = vec![85, 92, 78, 96, 61];

    // .iter() — borrow each element, Vec is still usable after
    println!("Scores:");
    for score in scores.iter() {
        print!("{} ", score);   // score: &i32
    }
    println!();
    println!("Vec still alive: {:?}", scores);  // ✅

    // .iter_mut() — mutable borrow, modify in place
    for score in scores.iter_mut() {
        *score += 5;   // dereference to modify; score: &mut i32
    }
    println!("After +5 bonus: {:?}", scores);  // [90, 97, 83, 101, 66] ✅

    // .into_iter() — takes ownership, Vec is consumed
    let passing: Vec<i32> = scores.into_iter().filter(|s| *s >= 70).collect();
    println!("Passing scores: {:?}", passing);  // [90, 97, 83, 101]
    // println!("{:?}", scores); // ❌ scores was moved by into_iter()
}
```

> 💡 **Quick rule:** `for x in &vec` is `.iter()`. `for x in &mut vec` is `.iter_mut()`.
> `for x in vec` is `.into_iter()` — and the Vec is gone afterward.

---

## Section 7: Adapters & Consumers

### Adapters — Build the Pipeline (Lazy)

Adapters take an iterator and return a **new iterator**. They do *nothing* until
a consumer drives them. Chain as many as you like — there's no cost until you pull.

```rust
fn main() {
    let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

    // Chain: map → filter → take  (all lazy — no work yet)
    let pipeline = numbers.iter()
        .map(|x| x * x)       // 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
        .filter(|x| *x > 20)  // 25, 36, 49, 64, 81, 100
        .take(3);              // 25, 36, 49  ← only first 3

    // collect() is the consumer — THIS is when the work happens
    let result: Vec<i32> = pipeline.collect();
    println!("{:?}", result);  // [25, 36, 49]
}
```

**Adapter quick reference:**

```
Adapter              What it does
──────────────────────────────────────────────────────────────────────
.map(|x| ...)        Transform each element — returns new type if needed
.filter(|x| ...)     Keep elements where closure returns true
.flat_map(|x| ...)   Map then flatten — handy for Option/Vec-producing funcs
.enumerate()         Wrap each element: (index, element)
.zip(other_iter)     Pair elements: (a, b) from two iterators
.take(n)             Stop after n elements
.skip(n)             Skip first n elements
.chain(other)        Append two iterators end-to-end
.peekable()          Lets you peek at next element without consuming
.rev()               Reverse (works on DoubleEndedIterator types)
.cloned()            &T → T by cloning (when T: Clone)
.copied()            &T → T by copying (when T: Copy)
```

### Consumers — Drain the Pipeline (Eager)

Consumers *call* `next()` until `None`, collecting or reducing the results:

```rust
fn main() {
    let data = vec![3, 1, 4, 1, 5, 9, 2, 6, 5];

    // collect — most versatile consumer
    let doubled: Vec<i32> = data.iter().map(|x| x * 2).collect();
    println!("{:?}", doubled);

    // sum — add up all elements
    let total: i32 = data.iter().sum();
    println!("sum = {}", total);   // 36

    // fold — like sum, but you control what accumulates
    let product: i32 = data.iter().fold(1, |acc, x| acc * x);
    println!("product = {}", product);  // 3*1*4*1*5*9*2*6*5 = 32400

    // find — first match, or None
    let first_big = data.iter().find(|&&x| x > 5);
    println!("first > 5: {:?}", first_big);  // Some(9)

    // any / all — short-circuit boolean checks
    println!("any > 8? {}", data.iter().any(|&x| x > 8));   // true
    println!("all > 0? {}", data.iter().all(|&x| x > 0));   // true

    // count — how many items
    let big_count = data.iter().filter(|&&x| x > 4).count();
    println!("{} elements > 4", big_count);  // 3

    // max / min
    println!("max = {:?}", data.iter().max());  // Some(9)
    println!("min = {:?}", data.iter().min());  // Some(1)
}
```

**Consumer quick reference:**

```
Consumer                  What it does
────────────────────────────────────────────────────────────────────────
.collect::<Vec<T>>()      Drain into any collection (Vec, HashMap, HashSet…)
.sum()                    Add all elements (T must implement Sum)
.product()                Multiply all elements
.fold(init, |acc, x|)     General accumulation — most powerful consumer
.for_each(|x| ...)        Side-effectful drain (like a consuming for loop)
.count()                  How many elements
.find(|x| ...)            First element matching predicate, or None
.position(|x| ...)        Index of first match, or None
.any(|x| ...)             True if any element matches (short-circuits)
.all(|x| ...)             True if all elements match (short-circuits)
.max() / .min()           Largest / smallest (returns Option<T>)
.last()                   Last element, or None
.nth(n)                   Element at index n, or None
```

### The `enumerate()` + `zip()` Duo

Two adapters worth special attention because they're used constantly:

```rust
fn main() {
    let fruits = vec!["apple", "banana", "cherry"];

    // enumerate: adds an index to each element
    for (i, fruit) in fruits.iter().enumerate() {
        println!("{}: {}", i, fruit);
        // 0: apple
        // 1: banana
        // 2: cherry
    }

    let prices = vec![1.20, 0.50, 2.75];

    // zip: pairs two iterators element by element
    let menu: Vec<(&str, f64)> = fruits.iter()
        .map(|s| *s)
        .zip(prices.iter().copied())
        .collect();
    println!("{:?}", menu);
    // [("apple", 1.2), ("banana", 0.5), ("cherry", 2.75)]
}
```

---

## Section 8: ⚠️ DANGER ZONE — Iterator Traps

---

### 👻 TRAP 1 — The Consumed Iterator Phantom

**The crime:** you consume an iterator with `.collect()` and then try to use it again.
After a consumer drains an iterator, it's gone. There is no rewinding.

```
Before collect():          After collect():
  iter ──► Some(1)           iter ──► None  ← forever empty
       ──► Some(2)
       ──► Some(3)

  The iterator walked off the end of the data. It has no memory of what it saw.
  Calling .collect() a second time gives you an empty Vec, not an error.
  (Or an E0382 if the iterator itself was moved.)
```

```rust
fn main() {
    let v = vec![1, 2, 3];
    let mut iter = v.iter();

    // Drain the iterator once
    let first_pass: Vec<&i32> = iter.by_ref().take(2).collect();
    println!("{:?}", first_pass);   // [1, 2]

    // iter is now positioned at element 3 — not rewound
    let second_pass: Vec<&i32> = iter.collect();
    println!("{:?}", second_pass);  // [3]  ← NOT [1, 2, 3] !

    // ❌ If you had moved iter into collect(), you couldn't use it at all:
    // let iter2 = v.iter();
    // let a: Vec<_> = iter2.collect();  // iter2 moved
    // let b: Vec<_> = iter2.collect();  // ❌ E0382 — use of moved value
}
```

> **Fix:** Call `.iter()` again — it costs nothing (just a new pointer). Or use
> `.clone()` on the iterator if you need to iterate the same data multiple times
> and can't call `.iter()` again (e.g. iterating a custom iterator twice).

---

### 😴 TRAP 2 — The Idle Pipeline

**The crime:** you build a beautiful chain of adapters and forget the consumer.
The pipeline is a dormant machine. Zero work happens. The compiler even warns you.

```rust
fn main() {
    let v = vec![1, 2, 3, 4, 5];

    // ⚠️ This builds an adapter — but NOTHING IS EXECUTED
    v.iter().map(|x| {
        println!("processing {}", x);  // this NEVER runs
        x * 2
    });
    // warning: unused `Map` that must be used
    // = note: iterators are lazy and do nothing unless consumed
}
```

```
WHAT THE PROGRAMMER IMAGINED:       WHAT ACTUALLY HAPPENS:

[1,2,3,4,5] ──map──► processing     [1,2,3,4,5] ──map──► idle struct
                      processing                            (never called)
                      processing
                      ...

The machine is assembled. The power is off.
```

> **Fix:** Add a consumer. The most common fix:

```rust
fn main() {
    let v = vec![1, 2, 3, 4, 5];

    // ✅ .for_each() is the consuming version of a side-effectful loop
    v.iter().map(|x| x * 2).for_each(|x| println!("{}", x));

    // ✅ Or collect() if you want the results
    let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();
    println!("{:?}", doubled);
}
```

---

### 🔪 TRAP 3 — The `into_iter()` Gotcha on `Vec`

**The crime:** you write `for x in vec` (natural, readable) and then try to use
the Vec afterward — but it's gone. `for x in vec` silently calls `.into_iter()`,
which consumes the Vec by taking ownership of each element.

```rust
fn main() {
    let names = vec![String::from("Alice"), String::from("Bob")];

    for name in names {   // ← implicitly calls names.into_iter() — CONSUMING
        println!("{}", name);
    }

    println!("{:?}", names);  // ❌ E0382 — names was moved into the for loop
}
```

```
  for name in names              for name in &names
         ↑                               ↑
  into_iter() — owns each element    iter() — borrows each element
  Vec is consumed after the loop     Vec is alive after the loop
```

> **Fix:** Borrow with `&` to preserve the Vec:

```rust
fn main() {
    let names = vec![String::from("Alice"), String::from("Bob")];

    for name in &names {   // ✅ borrows — names is alive after
        println!("{}", name);
    }

    println!("still here: {:?}", names);  // ✅
}
```

---

## Section 9: 🔍 Deep Dive — Zero-Cost Abstraction

Rust makes a bold promise: **iterator chains have zero runtime overhead compared
to hand-written loops**. This is not marketing — it's a verifiable property of
how LLVM optimises Rust code.

### How It Works: Iterator State Machines

When you write a chain like `iter.map(...).filter(...).take(3)`, the compiler
builds a **nested struct** on the stack:

```
Take<Filter<Map<Iter<'_, i32>, closure_A>, closure_B>>
     └── wraps ────────────────────────────────────┘
           Filter<Map<...>, closure_B>
                 └── wraps ──────────┘
                       Map<Iter, closure_A>
                             └── wraps ──┘
                                   Iter<'_, i32>
```

This entire chain is a **single stack-allocated value**. No heap allocation.
No virtual dispatch. No function call overhead between stages.

When `.collect()` calls `next()` on `Take`, `Take` calls `next()` on `Filter`,
which calls `next()` on `Map`, which calls `next()` on `Iter`. The compiler
**inlines all of these calls** and LLVM sees one tight loop.

### Three-Column Comparison

```
HAND-WRITTEN LOOP           ITERATOR CHAIN              WHAT THE OPTIMIZER SEES
─────────────────────       ───────────────────         ──────────────────────
let mut out = vec![];       let out: Vec<i32> =         Both become identical
let cap = v.len();          v.iter()                    machine code after LLVM
out.reserve(cap);               .filter(|&&x| x > 0)   optimization:
for &x in &v {                  .map(|&x| x * 2)
  if x > 0 {                    .collect();             - single tight loop
    out.push(x * 2);                                    - no per-element alloc
  }                                                     - SIMD if applicable
}                                                       - loop unrolling
```

### `size_hint()` — Smarter Memory Allocation

Iterators can tell the consumer how many items to expect. `collect()` uses this
to pre-allocate the right capacity, avoiding repeated re-allocations:

```rust
fn main() {
    let v = vec![1, 2, 3, 4, 5];

    // size_hint returns (min, Option<max>)
    let iter = v.iter();
    println!("{:?}", iter.size_hint());  // (5, Some(5))

    // filter doesn't know how many will pass — lower bound is 0
    let filtered = v.iter().filter(|&&x| x > 2);
    println!("{:?}", filtered.size_hint());  // (0, Some(5))
    // collect() uses the max hint to pre-allocate, avoiding extra allocs
}
```

### The Cost Table

```
Abstraction          Runtime cost     Notes
──────────────────────────────────────────────────────────────────
for loop             baseline         Direct — what everything compiles to
.iter() chain        same             LLVM inlines and fuses the chain
Box<dyn Iterator>    tiny overhead    Virtual dispatch per .next() call
Python list comprehension  higher     Interpreted, no specialisation
Java stream          higher           Object boxing, JIT warms up
```

> **The bottom line:** `map().filter().collect()` is not "slower than a loop."
> It *is* the loop, dressed in a cleaner coat. Use it without guilt.

---

## Section 10: Closures + Iterators Together — Word Frequency Counter

This section brings everything together: closures carry context, iterators
process sequences, and together they express rich data transformations in a way
that's both readable and fast.

**Goal:** Read a sentence, count how often each word appears, and print the top 5.

```rust
use std::collections::HashMap;

fn word_frequency(text: &str) -> Vec<(String, usize)> {
    // Step 1: split into words, normalize to lowercase
    let counts: HashMap<String, usize> = text
        .split_whitespace()                    // iterator over &str tokens
        .map(|word| {                          // normalize each word
            word.chars()
                .filter(|c| c.is_alphabetic()) // strip punctuation
                .flat_map(|c| c.to_lowercase())
                .collect::<String>()
        })
        .filter(|word| !word.is_empty())       // skip empty strings
        .fold(HashMap::new(), |mut map, word| {
            *map.entry(word).or_insert(0) += 1; // closure mutates the HashMap
            map
        });

    // Step 2: sort by frequency descending — closure does the comparison
    let mut pairs: Vec<(String, usize)> = counts.into_iter().collect();
    pairs.sort_by(|a, b| b.1.cmp(&a.1));   // closure: compare by count, descending

    // Step 3: take top 5
    pairs.into_iter().take(5).collect()
}

fn main() {
    let text = "the quick brown fox jumps over the lazy dog \
                the dog barked and the fox ran away quickly";

    let top = word_frequency(text);

    println!("Top words:");
    for (i, (word, count)) in top.iter().enumerate() {
        println!("  {}. {:12} — {} time(s)", i + 1, word, count);
    }
}
```

```
Top words:
  1. the          — 5 time(s)
  2. fox          — 2 time(s)
  3. dog          — 2 time(s)
  4. quick        — 1 time(s)
  5. brown        — 1 time(s)
```

**What's happening at each step:**

```
"the quick brown fox …"
        │
  split_whitespace()   ──► "the", "quick", "brown", "fox", …  (lazy)
        │
  .map(normalize)      ──► "the", "quick", "brown", "fox", …  (lazy)
        │
  .filter(non-empty)   ──► same tokens, empties dropped        (lazy)
        │
  .fold(HashMap)       ──► {"the":5, "fox":2, …}              (EAGER — drains)
        │
  sort_by(closure)     ──► sorted Vec by count desc           (in-place)
        │
  .take(5)             ──► first 5 pairs                      (lazy)
        │
  .collect()           ──► Vec<(String, usize)>               (EAGER — final drain)
```

> Notice the `fold` closure is **`FnMut`** — it mutates the HashMap on every
> call. And `sort_by` takes a closure that's also `FnMut` (the comparison).
> Neither needs to own anything, but both modify state — that's `FnMut` in
> its natural habitat.

---

## Break It On Purpose

### Mistake 1: Use of moved value — variable moved into closure then used

```rust
fn main() {
    let data = vec![1, 2, 3];
    let process = move || println!("{:?}", data);  // data MOVED into closure
    process();
    println!("{:?}", data);  // ❌ E0382 — data moved into closure above
}
```

> **Error:** `error[E0382]: borrow of moved value: 'data'`
>
> `move` forced `data` into the closure's captured struct. The original
> binding is empty. To keep the original alive: remove `move` and borrow,
> or clone before moving.

```rust
// ✅ Fix: capture by reference — no move needed
fn main() {
    let data = vec![1, 2, 3];
    let process = || println!("{:?}", data);  // borrows, not moves
    process();
    println!("{:?}", data);  // ✅
}
```

### Mistake 2: Mutate while closure holds an immutable borrow

```rust
fn main() {
    let mut v = vec![1, 2, 3];
    let show = || println!("{:?}", v);  // immutable borrow of v
    v.push(4);   // ❌ E0502 — cannot mutate while immutably borrowed
    show();
}
```

> **Error:** `error[E0502]: cannot borrow 'v' as mutable because it is also borrowed as immutable`
>
> The closure `show` holds a live borrow of `v`. That borrow prevents mutation.
> The borrow lasts as long as `show` is in scope.
>
> **Fix:** Use the closure before mutating (or scope it to end early):

```rust
// ✅ Fix: use the closure first, then mutate
fn main() {
    let mut v = vec![1, 2, 3];
    { let show = || println!("{:?}", v); show(); }  // borrow ends here
    v.push(4);   // ✅
    println!("{:?}", v);  // [1, 2, 3, 4]
}
```

---

### Mistake 3: Vec is not an iterator — you must call `.iter()` first

**What goes wrong:** A `Vec` is a *container*, not an iterator. You can't call
adapter methods like `.map()` or `.filter()` directly on it. You need to
produce an iterator from the Vec first by calling `.iter()`, `.iter_mut()`, or
`.into_iter()`.

```rust
fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    let doubled: Vec<i32> = numbers.map(|x| x * 2).collect();  // ❌ E0599
}
```

> **Error:** `error[E0599]: no method named 'map' found for struct 'Vec<i32>'`
>
> In Rust 1.65, calling `.map()` directly on a `Vec` gives E0599 — the method
> doesn't exist on Vec, only on iterators.
>
> Conceptually this is "Vec doesn't implement Iterator" — calling `.iter()` first
> fixes it because `.iter()` returns a real `Iter<'_, i32>` which does implement Iterator.
>
> **Fix:** Call `.iter()` (or `.into_iter()` if you want owned values):

```rust
// ✅ Fix: convert Vec to iterator first
fn main() {
    let numbers = vec![1, 2, 3, 4, 5];
    let doubled: Vec<i32> = numbers.iter().map(|x| x * 2).collect();  // ✅
    println!("{:?}", doubled);  // [2, 4, 6, 8, 10]
}
```

---

## Try Yourself 🦀

Open the [Rust Playground](https://play.rust-lang.org) and work through each exercise.

1. **Counter closure (FnMut):** Write a function `make_counter() -> impl FnMut() -> i32`
   that returns a closure. Each time the closure is called, it returns the next integer
   starting from 1. Test by calling it 5 times. Hint: capture a `count: i32` and mutate it.

2. **Custom filter:** Start with `let numbers = vec![1,2,3,4,5,6,7,8,9,10];` and use a
   single iterator chain to produce a `Vec<i32>` containing only the even numbers multiplied
   by 3. Expected: `[6, 12, 18, 24, 30]`.

3. **Transform pipeline:** Given `let words = vec!["hello", "world", "rust", "is", "great"];`,
   use iterators to produce a `Vec<String>` of words that are longer than 3 characters,
   converted to uppercase. Expected: `["HELLO", "WORLD", "RUST", "GREAT"]`.

4. **fold to joined string:** Use `.fold()` to join a `Vec<&str>` with commas into a
   single `String`. `vec!["one", "two", "three"]` → `"one, two, three"`. Do it without
   using `.join()` — the goal is to practice `fold`.

5. **zip two Vecs:** Given `let names = vec!["Alice", "Bob", "Carol"];` and
   `let scores = vec![95, 72, 88];`, use `.zip()` to produce a `Vec<String>` where
   each element is `"Alice: 95"`, `"Bob: 72"`, `"Carol: 88"`.

6. **Find the first match:** Use `.find()` to locate the first element in
   `vec!["apple", "mango", "rust", "raspberry"]` that starts with 'r'. Then use
   `.position()` to find its index. What's the difference between the two methods?

7. **Move closure preview — thread spawn:** Run this on your local Rust installation
   (not the Playground — it works there too but threads shine locally):
   ```rust
   use std::thread;
   fn main() {
       let message = String::from("hello from thread");
       let handle = thread::spawn(move || println!("{}", message));
       handle.join().unwrap();
   }
   ```
   Now try removing `move` — read the compiler error carefully. Why does the thread
   require ownership rather than a borrow? Connect this to the closure lifetime rules
   from Section 4, Trap 1.

---

## 🧠 Memory Technique

> **CLOSURE = TO-GO BAG &nbsp; | &nbsp; ITERATOR = ASSEMBLY LINE**
>
> **Packing the bag:**
> - Default capture: Rust borrows when it can, copies `Copy` types.
> - `move` keyword: pack everything by value — the bag owns it all.
> - `Fn` = peeking in the bag. `FnMut` = restocking the bag. `FnOnce` = eating everything.
>
> **Running the assembly line:**
> - Adapters (`map`, `filter`, `take`…) build the line. **They do nothing alone.**
> - Consumers (`collect`, `sum`, `fold`…) start the machine. **One pull, all the work.**
> - "Why is my `map()` not running?" → No consumer at the end.
>
> **The three iteration modes — say it aloud:**
> - `&vec` → borrow, nothing taken.
> - `&mut vec` → borrow mutably, can change.
> - `vec` → consumed, gone forever.
>
> **If the compiler yells at you:**
> - "moved value" near a closure → check if `move` was used or if a value was taken out.
> - "doesn't implement Iterator" on a Vec → add `.iter()` first.
> - "immutable borrow" blocking mutation → the closure is still alive; end its scope first.

---

## FAQ

**Q: When should I use a closure vs a named function?**
Use a closure when the logic is short, used in one place, and needs to capture
variables from the surrounding context. Use a named function when the logic is
reusable across modules, long enough to deserve a name, or needs to be stored in
a `fn` pointer (not a closure trait). Closures that capture nothing *can* be
coerced to `fn` pointers, but in general use closures for small local logic and
named functions for shared reusable logic.

**Q: What's the difference between `.map()` and `.for_each()`?**
`.map()` transforms each element and returns a new iterator (lazy adapter — does
nothing alone). `.for_each()` calls a closure on each element and returns `()`
(eager consumer — drives the iteration). Use `.map()` when you want the
transformed values; use `.for_each()` when you only want side effects (printing,
logging, mutating external state).

**Q: Why does `.iter()` sometimes give me `&&T` inside a closure?**
Because `.iter()` yields `&T`, and `.filter()`'s closure receives a reference to
that: `&&T`. Solution: double-dereference `|&&x|` or use `|x| **x > 5`. This is
the most common point of "why are there two `&`s??" confusion. The rule: `filter`
passes a reference to the iterator's item, so if the iterator yields `&T`, filter
gives you `&&T`.

**Q: How do I collect into a `HashMap` instead of a `Vec`?**
```rust
use std::collections::HashMap;
let map: HashMap<&str, i32> = vec![("a", 1), ("b", 2)].into_iter().collect();
```
`collect()` can build any collection that implements `FromIterator`. Pass a type
annotation or use turbofish (`::<HashMap<_, _>>`) to tell it which to build.
The iterator must yield `(key, value)` tuples for `HashMap`.

**Q: What is `flatten()` and when do I need it?**
`.flatten()` collapses one level of nesting. If you have an iterator of `Vec<T>`
or `Option<T>` or `Result<T, E>`, `.flatten()` turns it into an iterator of `T`
(skipping `None`/`Err` in the process). `.flat_map()` is `.map().flatten()` in
one step — the most common use case.
```rust
let nested = vec![vec![1,2], vec![3,4], vec![5]];
let flat: Vec<i32> = nested.into_iter().flatten().collect();  // [1,2,3,4,5]
```

**Q: Are closures slower than regular functions?**
No — in release builds, the compiler inlines closures that are passed as
`impl Fn` / `impl FnMut` / `impl FnOnce` (static dispatch). The resulting code
is identical to a hand-written function call. The only closures with overhead are
`Box<dyn Fn(...)>` (heap-allocated, virtual dispatch). Use unboxed closures
(those accepted via trait bounds `F: Fn(...)`) and the overhead is zero.

**Q: Can I collect into a `String` instead of a `Vec<char>`?**
Yes! `String` implements `FromIterator<char>`:
```rust
let chars = vec!['h','e','l','l','o'];
let s: String = chars.into_iter().collect();  // "hello"
// Also useful for transforming strings:
let shouted: String = "hello".chars().map(|c| c.to_uppercase().next().unwrap()).collect();
```

---

## Cheat Card — Closures & Iterators

```
┌──────────────────────────────────────────────────────────────────────┐
│  CARD 15: CLOSURES & ITERATORS                                       │
│  "Pack a bag. Build a pipeline. Pull the results."                   │
├──────────────────────────────────┬───────────────────────────────────┤
│  CLOSURE SYNTAX                  │  CAPTURE MODES                    │
│  |x| x + 1                       │  default: borrow if possible      │
│  |x: i32| -> i32 { x + 1 }       │  move: force ownership into bag   │
│  move |x| x + captured_var       │                                   │
├──────────────────────────────────┼───────────────────────────────────┤
│  Fn        reads captures        │  most flexible — call any times   │
│  FnMut     mutates captures      │  needs mut binding                │
│  FnOnce    consumes captures     │  call once only                   │
├──────────────────────────────────┴───────────────────────────────────┤
│  THREE ITERATION MODES                                               │
│  .iter()       → &T        Vec survives  (read only)                 │
│  .iter_mut()   → &mut T    Vec survives  (modify in place)           │
│  .into_iter()  → T         Vec consumed  (for x in vec)              │
├──────────────────────────────────────────────────────────────────────┤
│  ADAPTERS (lazy — chain them, nothing runs)                          │
│  .map(f)  .filter(f)  .flat_map(f)  .take(n)  .skip(n)              │
│  .enumerate()  .zip(iter)  .chain(iter)  .cloned()  .rev()           │
├──────────────────────────────────────────────────────────────────────┤
│  CONSUMERS (eager — start the machine)                               │
│  .collect()  .sum()  .fold(init,f)  .for_each(f)  .count()          │
│  .find(f)  .position(f)  .any(f)  .all(f)  .max()  .min()           │
├──────────────────────────────────────────────────────────────────────┤
│  ZERO-COST RULE                                                      │
│  map().filter().collect() compiles to the SAME loop as hand-written  │
│  LLVM inlines the entire chain — no overhead in release builds       │
├──────────────────────────────────────────────────────────────────────┤
│  🧠  CLOSURE = TO-GO BAG  |  ITERATOR = ASSEMBLY LINE               │
│  ⚠️  No consumer? → pipeline is IDLE. Nothing runs.                  │
│  ⚠️  `for x in vec` → Vec CONSUMED. Use `for x in &vec` to borrow.  │
│  ⚠️  Iterator consumed? → call .iter() again. No rewind.             │
└──────────────────────────────────────────────────────────────────────┘
```

---

*Next: [Chapter 9 — Modules, Crates & Cargo: Organizing Growing Code](09_modules_crates.md)*
*Previous: [Chapter 7 — Generics](07_generics.md)*
