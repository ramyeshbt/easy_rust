# Playground Examples — Learning by Doing

> "Tell me and I forget. Teach me and I remember. Involve me and I learn."
> — Benjamin Franklin

This chapter is your **Rust sandbox**. Every example here is designed to be run, broken, modified, and understood — not just read.

Open the [Rust Playground](https://play.rust-lang.org) in another tab. You'll need it throughout this chapter.

---

## How to Use This Chapter

Each section follows this pattern:

1. **Concept recap** — one sentence reminder
2. **Working example** — code that compiles and runs correctly
3. **Break it on purpose** — intentionally wrong versions with explained errors
4. **Try Yourself** — challenges to push your understanding
5. **Memory Technique** — a trick to remember the rule forever
6. **FAQ** — questions real beginners ask

Don't skip the "Break it on purpose" parts. **Making the compiler angry is the fastest way to learn Rust.**

> 📖 **This is a long chapter — that's intentional.** It's your reference sandbox. Don't try to do it all in one sitting; jump to a section using the map below, try the examples, then come back. Bookmark it.

### Section Map

| # | Section | Core idea |
|---|---------|-----------|
| 1 | [Variables & Mutability](#section-1-variables-and-mutability) | Frozen by default; `mut` to change |
| 2 | [Data Types](#section-2-data-types--the-labeled-boxes) | Every value has a known type |
| 3 | [Ownership](#section-3-ownership--live-examples) | One owner; move vs clone vs copy |
| 4 | [Borrowing](#section-4-borrowing--live-examples) | Read with `&`, write with `&mut` |
| 5 | [Control Flow](#section-5-control-flow--making-decisions) | `if`/`match` are expressions |
| 6 | [Functions](#section-6-functions--your-building-blocks) | Last expression = return value |
| 7 | [Structs](#section-7-structs--your-custom-types) | Your own data types |
| 8 | [Enums](#section-8-enums--values-with-meaning) | One-of-several values, with data |
| 9 | [Error Handling](#section-9-error-handling--the-honest-approach) | `Result`, `Option`, `?` |

---

## Section 1: Variables and Mutability

### Concept
In Rust, variables are **immutable by default**. You must explicitly say `mut` to allow changes.

### Working Example

```rust
fn main() {
    let language = "Rust";          // immutable — cannot be changed
    let mut version = 1;            // mutable — CAN be changed

    println!("Learning {} version {}", language, version);

    version = 2;                    // ✅ allowed — version is mut
    println!("Now version {}", version);
}
```

```
Learning Rust version 1
Now version 2
```

### Break It On Purpose

**Attempt 1: Change an immutable variable**
```rust
fn main() {
    let score = 10;
    score = 20; // ❌ try this
    println!("{}", score);
}
```
> **Error:** `cannot assign twice to immutable variable`
>
> **What it teaches:** Rust forces you to be *intentional* about what changes. If you never meant to change `score`, this saves you from a subtle bug where something changes it accidentally.

**Attempt 2: Use before declaring**
```rust
fn main() {
    println!("{}", name); // ❌ used before declared
    let name = "Ferris";
}
```
> **Error:** `cannot find value 'name' in this scope`
>
> **What it teaches:** Rust reads top to bottom. No surprises, no hoisting.

### Try Yourself 🦀

1. Create an immutable variable `city` with your city name. Try changing it. Read the error.
2. Create a mutable counter starting at 0. Add 1 to it three times. Print it each time.
3. Declare a variable without using it. What warning does Rust give you? (Hint: prefix with `_` to silence it.)
4. Try: `let x = 5; let x = "hello";` — does it compile? What is Rust doing here? (This is called **shadowing** — research it!)

### Memory Technique 🧠

> **"Rust variables are frozen until you say mut."**
>
> Imagine every variable is an ice cube. To change it, you must first declare it `mut` (put it in warm water). Otherwise it stays frozen.

### FAQ

**Q: Why are variables immutable by default? Isn't that annoying?**
Most bugs in programs come from data changing when you didn't expect it to. Immutability by default forces you to be conscious about every change. You'll thank Rust for this later.

**Q: What's the difference between `mut` and making a new variable?**
`mut` changes the same variable in place. A new variable creates a new slot in memory. Use `mut` when you're updating a value over time (a counter, a score). Use a new variable when the meaning changes entirely.

**Q: What is shadowing?**
Shadowing is declaring a new variable with the same name as a previous one. The new one "shadows" the old. It's useful for transformations: `let x = "5"; let x: i32 = x.parse().unwrap();` — same name, completely new value and type.

---

## Section 2: Data Types — The Labeled Boxes

### Concept
Rust is **statically typed** — every value has a type known at compile time. Types are like labels on boxes: the compiler always knows what's inside.

### The Basic Types at a Glance

```
┌─────────────┬──────────────────┬────────────────────────────┐
│ Category    │ Types            │ Example                    │
├─────────────┼──────────────────┼────────────────────────────┤
│ Integer     │ i8, i16, i32,    │ let age: i32 = 25;         │
│             │ i64, i128, isize │                            │
│ Unsigned    │ u8, u16, u32,    │ let pixels: u32 = 1920;    │
│ Integer     │ u64, u128, usize │                            │
│ Float       │ f32, f64         │ let pi: f64 = 3.14159;     │
│ Boolean     │ bool             │ let is_fun: bool = true;   │
│ Character   │ char             │ let crab: char = '🦀';     │
│ String      │ String, &str     │ let s = String::from("hi") │
│ Tuple       │ (T1, T2, ...)    │ let pair = (1, "hello");   │
│ Array       │ [T; N]           │ let arr = [1, 2, 3, 4, 5]; │
└─────────────┴──────────────────┴────────────────────────────┘
```

### Working Example — Playing With Types

```rust
fn main() {
    // Integers
    let age: i32 = 28;
    let year: u32 = 2024;

    // Floats
    let height: f64 = 1.75;

    // Boolean
    let loves_rust: bool = true;

    // Character (NOTE: single quotes, not double)
    let mascot: char = '🦀';

    // Tuple — group different types together
    let profile: (&str, i32, bool) = ("Ramyesh", 28, true);

    // Array — same type, fixed length
    let scores: [i32; 5] = [95, 87, 92, 78, 88];

    println!("Age: {}, Year: {}", age, year);
    println!("Height: {}m, Loves Rust: {}", height, loves_rust);
    println!("Mascot: {}", mascot);
    println!("Name: {}, Age: {}, Active: {}", profile.0, profile.1, profile.2);
    println!("First score: {}, Last: {}", scores[0], scores[4]);
}
```

```
Age: 28, Year: 2024
Height: 1.75m, Loves Rust: true
Mascot: 🦀
Name: Ramyesh, Age: 28, Active: true
First score: 95, Last: 88
```

### Break It On Purpose

**Attempt 1: Wrong type**
```rust
fn main() {
    let age: i32 = "twenty-eight"; // ❌ string into integer
}
```
> **Error:** `mismatched types — expected i32, found &str`

**Attempt 2: Array out of bounds at compile time**
```rust
fn main() {
    let scores = [95, 87, 92];
    println!("{}", scores[10]); // ❌ index 10 doesn't exist
}
```
> Rust may catch this at compile time or panic at runtime depending on context. Either way — **no silent memory corruption like in C**.

**Attempt 3: Integer overflow (debug mode)**
```rust
fn main() {
    let x: u8 = 255; // u8 max is 255
    let y = x + 1;   // ❌ overflow in debug mode
    println!("{}", y);
}
```
> In debug mode Rust **panics** (crashes with a clear message) rather than silently wrapping around. In release mode it wraps — but you can control this explicitly with `.wrapping_add()`, `.checked_add()`, etc.

### Try Yourself 🦀

1. Create a tuple storing a book's title (`&str`), year published (`u32`), and rating (`f32`). Print each field using `.0`, `.1`, `.2`.
2. Create an array of 7 days of the week as `&str`. Print the first and last day.
3. What happens when you try to store `256` in a `u8`? Try it and read the error.
4. Try: `let x = 2.0; let y = 2;` then `let z = x + y;` — what happens? What does this teach you about Rust's type strictness?
5. **Exploration challenge:** Look up `usize` — what makes it different from `u32`? When would you use it?

### Memory Technique 🧠

> **The "i/u + size" rule:**
> - `i` = "I can go negative" (signed)
> - `u` = "Only Up from zero" (unsigned)
> - The number = bits used (8, 16, 32, 64)
>
> So `i32` = signed, 32-bit. Range: -2,147,483,648 to +2,147,483,647.
> And `u32` = unsigned, 32-bit. Range: 0 to 4,294,967,295.

### FAQ

**Q: Should I always specify the type, or can Rust figure it out?**
Rust has **type inference** — it can usually figure out the type from context. `let x = 5;` — Rust infers `i32`. Only specify the type when it's ambiguous or when you want to be explicit for clarity.

**Q: What's the difference between `String` and `&str`?**
`String` is an owned, heap-allocated string you can modify. `&str` is a borrowed reference to string data (often a string literal baked into your program). Use `&str` for reading, `String` for owning and modifying. You'll see this pattern constantly in Rust.

**Q: Why are there so many integer types?**
Precision and memory control. Embedded systems or network protocols need exact byte sizes. For general use, `i32` (integer) and `f64` (float) are the defaults and cover 99% of cases.

---

## Section 3: Ownership — Live Examples

### Concept
Every value has one owner. When the owner leaves scope, the value is dropped.

### Working Example — The Full Ownership Lifecycle

```rust
fn main() {
    // === BIRTH ===
    let message = String::from("Hello, Rustacean!");
    println!("Created: {}", message);

    // === MOVE ===
    let new_home = message; // ownership moves — `message` is gone
    println!("Moved to: {}", new_home);

    // === CLONE (explicit copy) ===
    let backup = new_home.clone(); // explicit deep copy — both exist
    println!("Original: {}, Backup: {}", new_home, backup);

    // === FUNCTION MOVE ===
    takes_ownership(new_home); // new_home moves INTO the function

    // println!("{}", new_home); // ❌ would fail — new_home was moved

    // === RETURN OWNERSHIP ===
    let returned = gives_ownership(); // function creates and gives us ownership
    println!("Got back: {}", returned);

} // backup and returned are dropped here

fn takes_ownership(s: String) {
    println!("I now own: {}", s);
} // s is dropped here — memory freed

fn gives_ownership() -> String {
    String::from("A gift from a function")
}
```

```
Created: Hello, Rustacean!
Moved to: Hello, Rustacean!
Original: Hello, Rustacean!, Backup: Hello, Rustacean!
I now own: Hello, Rustacean!
Got back: A gift from a function
```

### Ownership Decision Flowchart

```
Do you need the value after passing it to a function?
            │
    ┌───────┴───────┐
   YES              NO
    │                │
Use &reference    Move it (default)
(borrow it)      — or return it back
    │
Do you need to modify it?
    │
  ┌─┴─┐
 YES   NO
  │     │
&mut   &T
```

### Break It On Purpose

**Attempt 1: Use after move**
```rust
fn main() {
    let s = String::from("rust");
    let t = s;
    println!("{}", s); // ❌ s was moved
}
```

**Attempt 2: Double free simulation (that Rust prevents)**
```rust
// This is what C would let you do — Rust won't:
fn main() {
    let s = String::from("danger");
    drop(s);           // explicitly drop (free)
    println!("{}", s); // ❌ use after drop
}
```
> **Error:** `borrow of moved value: 's'`
> In C this would be a use-after-free — a security vulnerability. Rust: compile error.

### Try Yourself 🦀

1. Write a function `shout(s: String) -> String` that takes ownership of a string, converts it to uppercase, and returns ownership back. Use `.to_uppercase()`.
2. Write a function that takes `&String` (borrows) and prints its length with `.len()`. Confirm you can still use the string after calling it.
3. Try cloning a large string vs. borrowing it. Which feels more natural for a "read only" operation? Why?
4. **Deep exploration:** What happens with `let x = 5; let y = x; println!("{}", x);`? Why doesn't this error? Look up the `Copy` trait.
5. Create a `Vec<String>` (a list of strings), add 3 items, pass it to a function that prints the count, then try to use the Vec after. Fix it using borrowing.

### Memory Technique 🧠

> **The "Hot Potato" rule:**
> A value is like a hot potato. Only one person holds it at a time. When you pass it to someone (a function, another variable), you let go. If you want to keep it — clone it, or just pass a reference.

### FAQ

**Q: When should I clone vs. borrow?**
Default to borrowing (`&`). Clone only when you genuinely need two independent copies. Cloning is explicit and has a cost — Rust makes you type `.clone()` so you're always aware.

**Q: Do I always have to return values from functions to get them back?**
No — that's what references are for. If a function only needs to *read or modify* your data, pass a reference and your ownership stays with you.

**Q: What happens to stack-allocated data (like integers)?**
They're `Copy` — they're duplicated automatically because they're tiny and cheap. Ownership rules still technically apply, but you'll never notice for basic types.

---

## Section 4: Borrowing — Live Examples

### Working Example — Reading Without Taking

```rust
fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");

    let word_count = count_words(&novel);    // borrow novel — don't take it
    let char_count = count_chars(&novel);    // borrow again — still fine

    println!("Novel: '{}'", &novel[..20]);  // still ours!
    println!("Words: {}, Characters: {}", word_count, char_count);
}

fn count_words(text: &String) -> usize {
    text.split_whitespace().count()
}

fn count_chars(text: &String) -> usize {
    text.chars().count()
}
```

```
Novel: 'Call me Ishmael. Som'
Words: 6, Characters: 33
```

### Working Example — Modifying With a Mutable Reference

```rust
fn main() {
    let mut essay = String::from("Rust is interesting");

    println!("Before: {}", essay);

    add_enthusiasm(&mut essay);  // lend essay for modification

    println!("After:  {}", essay);  // our essay has changed!
}

fn add_enthusiasm(text: &mut String) {
    text.push_str("!!!");
}
```

```
Before: Rust is interesting
After:  Rust is interesting!!!
```

### The Borrow Rules Visualized

```
Your Data: [  "hello"  ]
                │
          Owner: s (mut)
                │
    ╔═══════════╩═══════════╗
    ║   What can you do?    ║
    ╠═══════════════════════╣
    ║  &s        → read     ║  many at once ✅
    ║  &s + &s   → read×2   ║  fine ✅
    ║  &mut s    → write    ║  only ONE, no reads ✅
    ║  &s + &mut → read+write│  FORBIDDEN ❌
    ║  &mut + &mut → 2 write │  FORBIDDEN ❌
    ╚═══════════════════════╝
```

### Break It On Purpose

**Attempt 1: Two mutable references**
```rust
fn main() {
    let mut s = String::from("hello");
    let r1 = &mut s;
    let r2 = &mut s; // ❌ second mutable reference
    println!("{} {}", r1, r2);
}
```
> **Error:** `cannot borrow 's' as mutable more than once at a time`

**Attempt 2: Mutable and immutable at the same time**
```rust
fn main() {
    let mut s = String::from("hello");
    let r1 = &s;      // immutable borrow starts
    let r2 = &mut s;  // ❌ mutable borrow while immutable exists
    println!("{} {}", r1, r2);
}
```

**Attempt 3: Dangling reference**
```rust
fn dangle() -> &String {    // ❌ trying to return a reference to local data
    let s = String::from("hello");
    &s  // s will be dropped at end of function!
}
fn main() {
    let r = dangle();
}
```
> **Error:** `missing lifetime specifier` — Rust is telling you this reference would outlive the data.

### Try Yourself 🦀

1. Write a function `to_uppercase_ref(s: &mut String)` that modifies a string in place using `.make_ascii_uppercase()`. Call it and print before/after.
2. Try creating 5 immutable references to the same String simultaneously. Does Rust care? What does this tell you?
3. Write a function that tries to return a reference to a String created inside it. Read the error. Then fix it by returning the owned String instead.
4. **Challenge:** Write a function `replace_word(text: &mut String, from: &str, to: &str)` that replaces all occurrences of `from` with `to`. Hint: use the `.replace()` method, then reassign with `*text = ...`.
5. **Think about it:** Why does Rust allow many immutable references but only one mutable reference? What real-world problems does this prevent in multi-threaded programs?

### Memory Technique 🧠

> **The "Library Reading Room" rule:**
> - Many people can **read** the same book at the same time (many `&T`)
> - Only one person can **write** in a book at a time (one `&mut T`)
> - You can't read AND write at the same time (no mix of `&T` and `&mut T`)
>
> This is literally how databases handle concurrent access too.

### FAQ

**Q: Can I change a variable through a mutable reference and also use it directly?**
Not at the same time. Once you create a `&mut` reference, the original variable is "locked" until the reference's scope ends.

**Q: What's a "slice" — I keep seeing `&str` and `&[i32]`?**
A slice is a reference to a contiguous portion of a collection. `&str` is a string slice — a view into part of a String. `&[i32]` is a slice of integers. They're incredibly useful and you'll use them constantly.

**Q: Why does Rust use `&` for references when C uses `*` and `&` differently?**
In C, `&` takes an address and `*` dereferences it. Rust simplifies this: `&` creates a reference, and the compiler handles dereferencing automatically in most cases through a feature called **auto-deref**. You'll rarely need `*` explicitly.

---

## Section 5: Control Flow — Making Decisions

### Concept
Rust's `if`, `loop`, `while`, and `for` work similarly to other languages — with some powerful extras.

### Working Example — if as an Expression

In Rust, `if` is an **expression** — it returns a value!

```rust
fn main() {
    let temperature = 22;

    // Traditional if-else
    if temperature > 30 {
        println!("It's hot!");
    } else if temperature > 20 {
        println!("It's pleasant.");
    } else {
        println!("Grab a jacket.");
    }

    // if as an expression — assigns a value directly
    let description = if temperature > 20 { "warm" } else { "cool" };
    println!("Weather is {}", description);

    // Useful in function calls
    let advice = if temperature > 25 {
        "Stay hydrated"
    } else {
        "Enjoy the weather"
    };
    println!("{}", advice);
}
```

```
It's pleasant.
Weather is warm
Enjoy the weather
```

### Working Example — Loops

```rust
fn main() {
    // === loop — repeat forever until break ===
    let mut count = 0;
    let result = loop {
        count += 1;
        if count == 5 {
            break count * 2; // loop returns a value!
        }
    };
    println!("Loop result: {}", result); // 10

    // === while — repeat while condition is true ===
    let mut number = 3;
    while number > 0 {
        println!("{}...", number);
        number -= 1;
    }
    println!("Liftoff!");

    // === for — iterate over a range or collection ===
    for i in 1..=5 {
        println!("Step {}", i);
    }

    // Iterate over an array
    let languages = ["Rust", "Python", "Go", "JavaScript"];
    for lang in &languages {
        println!("Language: {}", lang);
    }

    // Enumerate — index AND value
    for (index, lang) in languages.iter().enumerate() {
        println!("{}: {}", index + 1, lang);
    }
}
```

### Working Example — Pattern Matching with `match`

`match` is like a supercharged `switch` — but it's **exhaustive** (Rust forces you to handle every case).

```rust
fn main() {
    let dice_roll = 4;

    match dice_roll {
        1 => println!("Critical failure!"),
        2 | 3 => println!("Not great..."),
        4 | 5 => println!("Pretty good!"),
        6 => println!("Critical success!"),
        _ => println!("Invalid roll"), // _ catches everything else
    }

    // match with return value
    let outcome = match dice_roll {
        6 => "legendary",
        4 | 5 => "good",
        1..=3 => "rough",
        _ => "unknown",
    };
    println!("Outcome: {}", outcome);
}
```

```
Pretty good!
Outcome: good
```

### Break It On Purpose

**Attempt 1: Non-exhaustive match**
```rust
fn main() {
    let x: i32 = 5;
    match x {
        1 => println!("one"),
        2 => println!("two"),
        // ❌ what about 3, 4, 5... and everything else?
    }
}
```
> **Error:** `non-exhaustive patterns: i32 not covered`
> Rust forces you to handle ALL cases. Add `_ => println!("other")` to fix it.

**Attempt 2: Mismatched types in if branches**
```rust
fn main() {
    let x = if true { 5 } else { "six" }; // ❌ one branch returns i32, other &str
}
```
> **Error:** `if and else have incompatible types`
> Both branches of an `if` expression must return the same type.

### Try Yourself 🦀

1. Write a `match` on a `&str` variable (your favorite programming language). Handle at least 3 cases and a catch-all.
2. Use a `for` loop with `1..=10` to print only even numbers. Hint: use `if n % 2 == 0`.
3. Use `loop` with a `break` value to find the first number in range 1–100 divisible by both 7 and 11.
4. **Challenge:** Write a simple grading function using `match` — takes a score (`u32`) and returns `"A"`, `"B"`, `"C"`, `"D"`, or `"F"`. Use ranges like `90..=100`.
5. **Exploration:** What is `continue` in a loop? What does `break` with a label look like? (Hint: `'outer: loop { ... break 'outer; }`)

### Memory Technique 🧠

> **"`match` is a contract."**
> When you write `match`, you're signing a contract with the compiler: "I will handle EVERY possible value." The `_` wildcard is the "everything else" clause that fulfills the contract.

---

## Section 6: Functions — Your Building Blocks

### Working Example — Functions in Depth

```rust
// Function with parameters and return value
fn add(a: i32, b: i32) -> i32 {
    a + b  // no semicolon = this is the return value (expression)
}

// Function with early return
fn divide(a: f64, b: f64) -> f64 {
    if b == 0.0 {
        return 0.0; // early return with semicolon
    }
    a / b // implicit return
}

// Function returning multiple values via tuple
fn min_max(numbers: &[i32]) -> (i32, i32) {
    let mut min = numbers[0];
    let mut max = numbers[0];

    for &n in numbers {
        if n < min { min = n; }
        if n > max { max = n; }
    }

    (min, max) // return a tuple
}

fn main() {
    println!("5 + 3 = {}", add(5, 3));
    println!("10 / 2 = {}", divide(10.0, 2.0));
    println!("10 / 0 = {}", divide(10.0, 0.0));

    let scores = [42, 17, 88, 5, 63, 91, 30];
    let (low, high) = min_max(&scores); // destructure tuple
    println!("Min: {}, Max: {}", low, high);
}
```

```
5 + 3 = 8
10 / 2 = 5
10 / 0 = 0
Min: 5, Max: 91
```

### The Expression vs Statement Distinction

This trips up almost every beginner. In Rust:
- **Statement** = does something, no return value (ends with `;`)
- **Expression** = evaluates to a value (no `;`)

```rust
fn main() {
    // Statement — no value returned
    let x = 5;

    // Block expression — the block evaluates to its last expression
    let y = {
        let a = 3;
        let b = 4;
        a + b  // no semicolon — this is the value of the block
    };

    println!("y = {}", y); // 7
}
```

> **Golden Rule:** Remove the semicolon from the last line of a function body → that becomes the return value.

### Try Yourself 🦀

1. Write a function `is_palindrome(s: &str) -> bool` that returns true if the string reads the same forwards and backwards.
2. Write a function `fizzbuzz(n: u32) -> String` — returns `"Fizz"` for multiples of 3, `"Buzz"` for multiples of 5, `"FizzBuzz"` for both, and the number as string otherwise.
3. Write a function `celsius_to_fahrenheit(c: f64) -> f64`.
4. **Challenge:** Write a recursive function `factorial(n: u64) -> u64`. Test with `factorial(10)`.
5. **Exploration:** What does `-> ()` mean as a return type? What is the unit type in Rust?

### Memory Technique 🧠

> **"Semicolons are silent."**
> A line with `;` does something but says nothing back.
> A line without `;` returns its value.
> Functions automatically return their last expression.

---

## Section 7: Structs — Your Custom Types

### Concept
A `struct` groups related data together under a single name. Think of it as a template for an object.

### Working Example

```rust
// Define the struct
// #[derive(...)] auto-generates useful behaviour for you:
//   Debug → lets you print with {:?}    Clone → lets you call .clone()
#[derive(Debug, Clone)]
struct Developer {
    name: String,
    language: String,
    years_experience: u32,
    loves_rust: bool,
}

// Add methods to the struct
impl Developer {
    // Constructor (by convention called `new`)
    fn new(name: &str, language: &str, years: u32) -> Developer {
        Developer {
            name: String::from(name),
            language: String::from(language),
            years_experience: years,
            loves_rust: false,
        }
    }

    // Method — takes &self (borrows, doesn't consume)
    fn introduce(&self) {
        println!(
            "Hi! I'm {} and I use {}. {} years experience.",
            self.name, self.language, self.years_experience
        );
    }

    // Mutable method — takes &mut self
    fn discover_rust(&mut self) {
        self.loves_rust = true;
        self.language = String::from("Rust");
        println!("{} has discovered Rust! 🦀", self.name);
    }

    // Method that returns a value
    fn is_senior(&self) -> bool {
        self.years_experience >= 5
    }
}

fn main() {
    let mut dev = Developer::new("Ramyesh", "Python", 3);
    dev.introduce();
    println!("Senior? {}", dev.is_senior());

    dev.discover_rust();
    dev.introduce();

    // Thanks to #[derive(Debug)] we can print the whole struct:
    println!("{:?}", dev);
    // And #[derive(Clone)] lets us make an independent copy:
    let backup = dev.clone();
    println!("Backup of: {}", backup.name);
}
```

```
Hi! I'm Ramyesh and I use Python. 3 years experience.
Senior? false
Hi! I'm Ramyesh and I use Rust. 3 years experience.
Ramyesh has discovered Rust! 🦀
Developer { name: "Ramyesh", language: "Rust", years_experience: 3, loves_rust: true }
Backup of: Ramyesh
```

> 💡 Without `#[derive(Debug)]`, the line `println!("{:?}", dev)` would fail with *"`Developer` doesn't implement `Debug`"* — one of the most common errors new Rustaceans hit. Now you know the fix: add `#[derive(Debug)]` above the struct.

### Try Yourself 🦀

1. Create a `Book` struct with `title: String`, `author: String`, `pages: u32`, `rating: f32`. Add a `describe()` method and a `is_long_read()` method (returns true if pages > 400).
2. Create a `Rectangle` struct with `width` and `height`. Add `area()` and `perimeter()` methods.
3. **Challenge:** Add a method `scale(&mut self, factor: f64)` to Rectangle that multiplies both dimensions by the factor.
4. **Exploration:** Look up **tuple structs** — like `struct Color(u8, u8, u8);`. When would you use them vs. named structs?
5. Create two `Book` instances and compare their ratings to find the higher-rated one.

---

## Section 8: Enums — Values With Meaning

### Concept
An `enum` defines a type that can be one of several variants. Each variant can optionally hold data.

### Working Example — Enums Without Data

```rust
enum Direction {
    North,
    South,
    East,
    West,
}

fn describe_direction(dir: &Direction) -> &str {
    match dir {
        Direction::North => "Heading toward the cold",
        Direction::South => "Heading toward warmth",
        Direction::East => "Heading where the sun rises",
        Direction::West => "Heading where the sun sets",
    }
}

fn main() {
    let journey = Direction::East;
    println!("{}", describe_direction(&journey));
}
```

### Working Example — Enums WITH Data (The Real Power)

```rust
// Each variant can hold different data — like a tagged union
enum Shape {
    Circle(f64),              // radius
    Rectangle(f64, f64),     // width, height
    Triangle(f64, f64, f64), // three sides
}

impl Shape {
    fn area(&self) -> f64 {
        match self {
            Shape::Circle(r) => std::f64::consts::PI * r * r,
            Shape::Rectangle(w, h) => w * h,
            Shape::Triangle(a, b, c) => {
                // Heron's formula
                let s = (a + b + c) / 2.0;
                (s * (s - a) * (s - b) * (s - c)).sqrt()
            }
        }
    }

    fn describe(&self) -> String {
        match self {
            Shape::Circle(r) => format!("Circle with radius {}", r),
            Shape::Rectangle(w, h) => format!("{}x{} Rectangle", w, h),
            Shape::Triangle(a, b, c) => format!("Triangle ({}, {}, {})", a, b, c),
        }
    }
}

fn main() {
    let shapes = vec![
        Shape::Circle(5.0),
        Shape::Rectangle(4.0, 6.0),
        Shape::Triangle(3.0, 4.0, 5.0),
    ];

    for shape in &shapes {
        println!("{} → Area: {:.2}", shape.describe(), shape.area());
    }
}
```

```
Circle with radius 5 → Area: 78.54
4x6 Rectangle → Area: 24.00
Triangle (3, 4, 5) → Area: 6.00
```

### Try Yourself 🦀

1. Create an `enum Season` with four variants. Write a `is_warm()` function using `match` that returns true for Summer and Spring.
2. Create an `enum Message` where variants can hold data: `Quit` (no data), `Move { x: i32, y: i32 }` (named fields), `Write(String)`, `Color(u8, u8, u8)`. Write a function that handles each.
3. **Exploration:** Look up `Option<T>` — Rust's built-in enum for "value or nothing". Write a function `find_first_even(numbers: &[i32]) -> Option<i32>` that returns `Some(n)` or `None`.

---

## Section 9: Error Handling — The Honest Approach

### Concept
Rust has **no exceptions**. Instead, functions that can fail return `Result<T, E>` — either `Ok(value)` or `Err(error)`. You're forced to decide what to do when something goes wrong.

### Working Example

```rust
use std::num::ParseIntError;

fn parse_age(input: &str) -> Result<u32, ParseIntError> {
    let age: u32 = input.trim().parse()?; // ? propagates errors upward
    Ok(age)
}

fn main() {
    let inputs = ["25", "abc", " 30 ", "-5", "999"];

    for input in &inputs {
        match parse_age(input) {
            Ok(age) => println!("'{}' → Valid age: {}", input, age),
            Err(e)  => println!("'{}' → Error: {}", input, e),
        }
    }
}
```

```
'25' → Valid age: 25
'abc' → Error: invalid digit found in string
' 30 ' → Valid age: 30
'-5' → Error: invalid digit found in string
'999' → Valid age: 999
```

### The `?` Operator — Propagating Errors Cleanly

The `?` at the end of a fallible call means: "If this is `Err`, return it immediately. If it's `Ok`, unwrap the value."

```rust
// Without ?  — verbose
fn read_username() -> Result<String, std::io::Error> {
    let result = std::fs::read_to_string("username.txt");
    match result {
        Ok(s) => Ok(s),
        Err(e) => Err(e),
    }
}

// With ? — clean
fn read_username_clean() -> Result<String, std::io::Error> {
    let s = std::fs::read_to_string("username.txt")?;
    Ok(s)
}
```

### Option — When a Value Might Be Absent

`Result` is for operations that can **fail with a reason**. `Option` is for values that might simply **not be there** — Rust's safe replacement for `null`. It has two variants: `Some(value)` or `None`.

```rust
// Searching might not find anything → return Option
fn find_even(numbers: &[i32]) -> Option<i32> {
    for &n in numbers {
        if n % 2 == 0 {
            return Some(n);   // found one
        }
    }
    None                       // nothing matched
}

fn main() {
    let a = [1, 3, 5, 8, 9];
    let b = [1, 3, 5, 7, 9];

    // Four idiomatic ways to handle an Option:

    // 1. match — full control
    match find_even(&a) {
        Some(n) => println!("First even: {}", n),
        None    => println!("No evens found"),
    }

    // 2. if let — when you only care about the Some case
    if let Some(n) = find_even(&a) {
        println!("Got: {}", n);
    }

    // 3. unwrap_or — supply a fallback
    let result = find_even(&b).unwrap_or(-1);
    println!("Even or fallback: {}", result); // -1

    // 4. map — transform the value only if it exists
    let doubled = find_even(&a).map(|n| n * 2);
    println!("{:?}", doubled); // Some(16)
}
```

```
First even: 8
Got: 8
Even or fallback: -1
Some(16)
```

> **The big idea:** there is no `null` in Rust. If a value can be absent, its type is `Option<T>`, and the compiler *forces* you to handle the `None` case. The billion-dollar `null` mistake — calling a method on something that turned out to be empty — is impossible here.

**Common `Option`/`Result` helpers you'll use constantly:**

| Method | What it does |
|--------|--------------|
| `.unwrap()` | Get the value or **panic** — use only when you're certain |
| `.expect("msg")` | Like `unwrap` but with your own panic message |
| `.unwrap_or(x)` | Get the value or fall back to `x` |
| `.unwrap_or_default()` | Fall back to the type's default (`0`, `""`, etc.) |
| `.map(\|v\| ...)` | Transform the inner value if present |
| `.is_some()` / `.is_none()` | Check without consuming |
| `?` | Propagate `None`/`Err` to the caller |

### Try Yourself 🦀

1. Write a `divide(a: f64, b: f64) -> Result<f64, String>` that returns `Err("Cannot divide by zero".to_string())` when `b == 0.0`.
2. Use `.unwrap_or(default)` to handle an `Option` without a `match` — e.g., `let x: Option<i32> = None; let val = x.unwrap_or(0);`
3. **Challenge:** Chain multiple `?` operators in a function that: reads a string, parses it as `f64`, and doubles it.
4. **Exploration:** Look up `panic!` vs `Result`. When is it acceptable to use `panic!`? When is it not?

### Memory Technique 🧠

> **"Result is an honest return type."**
> A function returning `Result` is saying: "I might fail, and I'm telling you upfront." No surprises. No exceptions that crash your whole program silently.
> `Ok` = success. `Err` = known failure. Handle both.

---

## Master Reference: Common Patterns at a Glance

### Ownership Patterns

```
┌────────────────────────────────────────────────────────────────┐
│ GOAL                  │ HOW                    │ EXAMPLE        │
├────────────────────────────────────────────────────────────────┤
│ Read data in fn       │ Pass &T                │ fn f(s: &str)  │
│ Modify data in fn     │ Pass &mut T            │ fn f(s: &mut S)│
│ Transfer ownership    │ Pass T (no &)          │ fn f(s: String)│
│ Keep + modify own var │ Clone first            │ f(s.clone())   │
│ Return new value      │ Return T               │ -> String      │
│ Return maybe-nothing  │ Return Option<T>       │ -> Option<i32> │
│ Return maybe-error    │ Return Result<T,E>     │ -> Result<i32> │
└────────────────────────────────────────────────────────────────┘
```

### Quick Syntax Reference

```rust
// Variables
let x = 5;                    // immutable
let mut x = 5;                // mutable
let x: i32 = 5;               // explicit type

// References
let r = &x;                   // immutable reference
let r = &mut x;               // mutable reference (x must be mut)
*r = 10;                      // dereference to modify

// Strings
let s = String::from("hi");   // owned String
let s: &str = "hi";           // string literal (borrowed)
let s = format!("{} {}", a, b); // format into new String

// Collections
let v: Vec<i32> = Vec::new(); // empty vector
let v = vec![1, 2, 3];        // vector literal
v.push(4);                    // add element (v must be mut)
v[0]                          // access (panics if out of bounds)
v.get(0)                      // safe access → Option<&i32>

// Control flow
if condition { } else { }     // branches
match value { pat => expr, }  // exhaustive matching
for x in collection { }       // iterate
while condition { }           // loop while true
loop { break value; }         // infinite loop, optionally returns value

// Functions
fn name(param: Type) -> RetType { expr }
fn name(param: Type) { stmt; } // returns ()

// Structs
struct Name { field: Type }
impl Name { fn method(&self) { } }

// Enums
enum Name { Variant1, Variant2(Type) }
```

---

## The "Error Museum" — Common Mistakes Collected

Every Rustacean makes these. Now you'll recognize them instantly:

| Error Message Snippet | What It Means | Quick Fix |
|---|---|---|
| `cannot borrow as mutable` | Variable isn't `mut` | Add `mut` to declaration |
| `borrow of moved value` | Used after move | Clone, or use `&` reference |
| `cannot borrow as mutable, also borrowed as immutable` | Mixed borrows | Finish immutable borrow first |
| `does not live long enough` | Reference outlives its data | Return owned value, not reference |
| `mismatched types` | Wrong type passed | Check type annotations |
| `cannot find value in scope` | Typo or out-of-scope | Check spelling and scope |
| `non-exhaustive patterns` | `match` missing cases | Add `_ => ()` wildcard arm |
| `expected ... found ()` | Missing return value | Remove `;` from last expression |

---

## Graduating from the Playground: Meet Cargo

The Playground is perfect for learning, but real Rust projects live on your own machine and are managed by **Cargo** — Rust's build tool and package manager, installed automatically with [rustup.rs](https://rustup.rs). It's consistently rated one of the best tooling experiences in any language.

Here are the only commands you need to start:

```bash
cargo new hello_rust      # create a new project folder with everything set up
cd hello_rust

cargo run                 # compile AND run your program
cargo check               # type-check fast WITHOUT producing a binary (great while learning)
cargo build               # compile to target/debug/
cargo build --release     # compile optimized, for real performance
cargo test                # run your tests
```

A fresh `cargo new` project looks like this:

```
hello_rust/
├── Cargo.toml      ← project name, version, and dependencies
└── src/
    └── main.rs     ← your code starts here (with a Hello World already written)
```

To add a library (called a **crate**) from [crates.io](https://crates.io), you just list it in `Cargo.toml` or run `cargo add <name>`:

```toml
[dependencies]
rand = "0.8"     # now `use rand::...` works in your code
```

> 💡 **Workflow tip while learning:** run `cargo check` constantly. It's much faster than a full build because it skips code generation — it just runs the borrow checker and type checker, which is exactly the feedback you want when you're still learning the rules.

---

## Your Learning Path Forward

You've now seen Rust's core features in action. Here's the recommended path from here:

```
Where you are now:
  ✅ Variables & types
  ✅ Ownership, borrowing, lifetimes
  ✅ Control flow
  ✅ Functions
  ✅ Structs & enums
  ✅ Error handling basics

Coming up next:
  📌 Cheat Cards — visual one-pagers to memorize everything
  📌 Mini-Projects — build a name formatter and calculator
  📌 Traits — defining shared behaviour
  📌 Generics — writing flexible, reusable code
  📌 Closures & iterators — Rust's functional side
  📌 Modules — organizing growing codebases
```

---

## Quick FAQ — Everything Else You Wondered

**Q: Do I need to install Rust to use this guide?**
Not yet! Everything in this chapter runs in the [Rust Playground](https://play.rust-lang.org). When you're ready to build real projects, install Rust with [rustup.rs](https://rustup.rs) — one command.

**Q: How do I print debug output for any type?**
Use `{:?}` in format strings and add `#[derive(Debug)]` above your struct/enum:
```rust
#[derive(Debug)]
struct Point { x: i32, y: i32 }
let p = Point { x: 1, y: 2 };
println!("{:?}", p);   // Point { x: 1, y: 2 }
println!("{:#?}", p);  // pretty-printed version
```

**Q: What's the difference between `println!` and `print!`?**
`println!` adds a newline at the end. `print!` doesn't. Use `eprintln!` to print to stderr (for error messages).

**Q: What are those `::` double colons I see everywhere?**
`::` is the path separator. `String::from(...)` calls the `from` function in the `String` type's namespace. `std::io::Error` refers to `Error` inside the `io` module inside the `std` (standard library) crate.

**Q: What is `&[i32]` vs `Vec<i32>`?**
`Vec<i32>` is an owned, growable list on the heap. `&[i32]` is a borrowed slice — a view into any contiguous sequence of `i32`. Functions should prefer `&[i32]` over `&Vec<i32>` because it's more flexible (works with both Vec and arrays).

**Q: I keep seeing `unwrap()` — is it safe?**
`unwrap()` on an `Option` or `Result` panics if the value is `None`/`Err`. It's fine in small programs or when you're certain it won't fail. In production code, handle the error explicitly with `match`, `if let`, or `?`.

**Q: What does `use` do at the top of a file?**
It brings names into scope so you don't have to write full paths. `use std::collections::HashMap;` lets you write `HashMap` instead of `std::collections::HashMap`.

---

*Next: [Cheat Cards — Everything on One Page](04_cheat_cards.md)*
*Previous: [Foundations via Analogy](02_foundations_analogy.md)*
