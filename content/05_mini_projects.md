# Mini-Projects — Build Real Things, Understand Deep Things

> "What I cannot create, I do not understand."
> — Richard Feynman

This chapter builds **five themed projects** of increasing complexity. Each one teaches moderate-level Rust — but more importantly, each one pulls back the curtain on what your program is *actually doing* at the system level: how memory is laid out, what the CPU is executing, what the operating system is managing, and why Rust's rules exist at the hardware level — not just as language design.

By the end, you won't just write Rust. You'll *see through it*, down to the metal.

---

## How to Read This Chapter

Each project has layers:

```
┌─────────────────────────────────────────┐
│  🎯 PROJECT GOAL    — what we're building │
│  📐 DESIGN          — how we'll structure it│
│  🔨 BUILD           — step-by-step code    │
│  🔍 DEEP DIVE       — system-level view    │
│  🧠 TECHNIQUE CARDS — what to memorize     │
│  🦀 ACTIVITIES      — your challenges      │
└─────────────────────────────────────────┘
```

You're encouraged to run every snippet in the [Rust Playground](https://play.rust-lang.org). The deep dives will transform "it works" into "I know *why* it works."

---

# Project 1: Name Card Generator

**Theme: Strings and Formatting**
**System Lens: Stack memory, string internals, UTF-8 encoding**

---

## 🎯 Goal

Build a program that takes raw name data and formats it into polished name cards — like a conference badge printer. You will understand why strings in Rust behave so differently from strings in Python or JavaScript.

**Final output:**
```
╔══════════════════════════════════╗
║  🦀 RUSTACEANS CONFERENCE 2024  ║
╠══════════════════════════════════╣
║  Name  :  Ramyesh Bt            ║
║  Role  :  Rust Developer        ║
║  Badge :  #0042                 ║
╚══════════════════════════════════╝
```

---

## 📐 Design

We need:
- A struct to hold raw name data
- String manipulation: trim, capitalize, format
- A display function that renders the card
- A batch processor for multiple names

---

## 🔨 Build — Step by Step

### Step 1: The Basic Name Struct

```rust
#[derive(Debug, Clone)]
struct Attendee {
    first_name: String,
    last_name: String,
    role: String,
    badge_number: u32,
}

impl Attendee {
    fn new(first: &str, last: &str, role: &str, badge: u32) -> Self {
        // .trim() removes whitespace; .to_string() converts &str → String
        Attendee {
            first_name: first.trim().to_string(),
            last_name: last.trim().to_string(),
            role: role.trim().to_string(),
            badge_number: badge,
        }
    }

    // Return a formatted full name with proper capitalisation
    fn full_name(&self) -> String {
        format!("{} {}", capitalise(&self.first_name), capitalise(&self.last_name))
    }

    fn badge_id(&self) -> String {
        format!("#{:04}", self.badge_number) // :04 = pad with zeros to 4 digits
    }
}

// Capitalise the first letter, lowercase the rest
fn capitalise(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => {
            // Chain: uppercase first char + rest of chars
            first.to_uppercase().to_string() + &chars.as_str().to_lowercase()
        }
    }
}

fn main() {
    let attendee = Attendee::new("  ramyesh  ", "bt", "Rust Developer", 42);
    println!("Name:  {}", attendee.full_name());
    println!("Role:  {}", attendee.role);
    println!("Badge: {}", attendee.badge_id());
}
```

```
Name:  Ramyesh Bt
Role:  Rust Developer
Badge: #0042
```

---

### Step 2: The Card Renderer

```rust
fn print_card(a: &Attendee) {
    let name  = a.full_name();
    let role  = &a.role;
    let badge = a.badge_id();

    // Pad strings to fixed widths for alignment
    let width = 34usize;
    let divider = "═".repeat(width);

    println!("╔{}╗", divider);
    println!("║{:^width$}║", "🦀 RUSTACEANS CONFERENCE 2024", width = width);
    println!("╠{}╣", divider);
    println!("║  {:<8}:  {:<22}║", "Name", name);
    println!("║  {:<8}:  {:<22}║", "Role", role);
    println!("║  {:<8}:  {:<22}║", "Badge", badge);
    println!("╚{}╝", divider);
}

fn main() {
    let attendees = vec![
        Attendee::new("ramyesh", "bt",       "Rust Developer",  42),
        Attendee::new("ALICE",   "SMITH",    "systems engineer", 7),
        Attendee::new("  bob",   "JOHNSON ", "Beginner",       128),
    ];

    for a in &attendees {
        print_card(a);
        println!();
    }
}
```

```
╔══════════════════════════════════╗
║   🦀 RUSTACEANS CONFERENCE 2024  ║
╠══════════════════════════════════╣
║  Name    :  Ramyesh Bt           ║
║  Role    :  Rust Developer       ║
║  Badge   :  #0042                ║
╚══════════════════════════════════╝
```

---

### Step 3: Sorting and Searching the Attendee List

```rust
fn find_by_badge(attendees: &[Attendee], badge: u32) -> Option<&Attendee> {
    attendees.iter().find(|a| a.badge_number == badge)
}

fn sorted_by_name(attendees: &[Attendee]) -> Vec<&Attendee> {
    let mut refs: Vec<&Attendee> = attendees.iter().collect();
    refs.sort_by(|a, b| a.last_name.cmp(&b.last_name));
    refs
}

fn main() {
    let mut attendees = vec![
        Attendee::new("ramyesh", "bt",      "Rust Developer",   42),
        Attendee::new("alice",   "smith",   "Systems Engineer",  7),
        Attendee::new("bob",     "johnson", "Beginner",         128),
        Attendee::new("carol",   "adams",   "Compiler Engineer",  3),
    ];

    println!("=== Sorted by Last Name ===");
    for a in sorted_by_name(&attendees) {
        println!("  {} — {}", a.full_name(), a.badge_id());
    }

    println!("\n=== Find Badge #7 ===");
    match find_by_badge(&attendees, 7) {
        Some(a) => println!("  Found: {}", a.full_name()),
        None    => println!("  Not found"),
    }
}
```

---

## 🔍 Deep Dive — What's Really Happening

### How a String Lives in Memory

When you write:
```rust
let name = String::from("Ramyesh");
```

Rust creates **two things** in two different places:

```
STACK (fast, fixed-size, per-function-call)
┌─────────────────────────────────┐
│  name  (String struct on stack) │
│  ┌──────────┬──────┬──────────┐ │
│  │  ptr     │ len  │ capacity │ │
│  │ 0x7f3a.. │  7   │    7     │ │
│  └────┬─────┴──────┴──────────┘ │
└───────┼─────────────────────────┘
        │ points to
        ▼
HEAP (slow to allocate, dynamic, survives function returns)
┌──────────────────────────┐
│  R  a  m  y  e  s  h    │  ← actual bytes, UTF-8 encoded
│  52 61 6d 79 65 73 68   │  ← hex values in memory
└──────────────────────────┘
```

**Three fields on the stack:**
1. `ptr` — a memory address pointing to the heap
2. `len` — how many bytes are currently used (7 for "Ramyesh")
3. `capacity` — how many bytes are allocated (could be more than len)

This is exactly why `String` is 24 bytes on a 64-bit system regardless of content — the *struct* is always the same size. The content lives on the heap and can be any length.

### What Happens on `let b = a` (Move)

```
BEFORE:                          AFTER let b = a:
stack: a → heap:"Ramyesh"        stack: a = INVALID
                                 stack: b → heap:"Ramyesh"
```

Only the 24-byte struct is copied. The heap data doesn't move — just the pointer. Rust marks `a` as moved to prevent two pointers pointing at the same heap data. If both could `drop()`, the heap data would be freed twice — a **double-free** bug. Rust prevents it with zero runtime cost.

### What Happens on `.clone()`

```rust
let b = a.clone();
```

```
stack: a → heap:"Ramyesh" (original)
stack: b → heap:"Ramyesh" (new copy — new heap allocation)
```

Two separate heap allocations. Two separate structs on the stack. Changing one doesn't affect the other. This is why `.clone()` is explicit — it costs a heap allocation and a memory copy.

### What Happens at `}` (Drop)

When a `String` goes out of scope:
1. Rust calls `drop()` on it (automatic — RAII pattern)
2. `drop()` calls the **memory allocator** (`free()` under the hood — typically `jemalloc` or the system allocator)
3. The allocator marks that memory region as available for reuse
4. The stack frame is popped — the 24-byte struct disappears

No garbage collector. No background thread. No pause. Deterministic, immediate, zero overhead.

### UTF-8: Why `s[0]` Is Forbidden

```rust
let s = String::from("Héllo");
// s[0] ← ❌ Rust forbids this
```

In UTF-8, a single character can be 1–4 bytes. `'H'` is 1 byte (0x48). `'é'` is **2 bytes** (0xC3 0xA9). If Rust let you do `s[0]`, you'd get a raw byte — not a character — and potentially split a multi-byte character in half, corrupting data.

Instead:
```rust
s.chars().nth(0)     // get the Nth Unicode character (scalar value)
s.as_bytes()[0]      // get the Nth raw byte (only safe for ASCII)
s.get(0..1)          // safely slice bytes → returns Option<&str>
```

This is not Rust being difficult. This is Rust being correct about how text actually works.

---

## 🧠 Technique Card — Strings

```
┌───────────────────────────────────────────────────────────┐
│  String = ptr(8) + len(8) + cap(8) = 24 bytes on stack   │
│  Content lives on heap. Length is in BYTES not chars.     │
│                                                           │
│  CONVERSIONS                                              │
│  "literal" → String     :  "x".to_string()               │
│                             String::from("x")             │
│  String → &str          :  &my_string  or  &my_string[..]│
│  number → String        :  42.to_string()                 │
│  String → number        :  "42".parse::<i32>().unwrap()   │
│                                                           │
│  CRITICAL METHOD ORDER                                    │
│  Always: .trim() first, then .parse() or .to_lowercase()  │
│  Never:  index with [i] — use .chars().nth(i) instead     │
└───────────────────────────────────────────────────────────┘
```

---

## 🦀 Activities

1. Add an `email: Option<String>` field to `Attendee`. Print `"(no email)"` if `None`.
2. Write a function that finds all attendees whose role contains a given keyword (case-insensitive). Use `.to_lowercase().contains()`.
3. Add a `vip: bool` field. Print a `★` next to VIP names on the card.
4. **Challenge:** Sort attendees by badge number AND print a second sorted list by last name — without cloning the Vec. (Hint: `sort_by_key`)
5. **System challenge:** Use `std::mem::size_of::<Attendee>()` to print the size of your struct. Calculate it by hand first — add up each field's size. Does it match? Look up **struct padding and alignment**.

---

# Project 2: Smart Calculator

**Theme: Enums, Pattern Matching, Error Handling**
**System Lens: How enums are stored, tagged unions, Result propagation chain**

---

## 🎯 Goal

Build a calculator that handles operations safely — no panics, no crashes, clear error messages. It should handle divide-by-zero, invalid input, and unknown operations gracefully.

**Final output:**
```
10 + 5  = 15
10 / 0  = Error: Division by zero
10 % 0  = Error: Modulo by zero
abc + 5 = Error: Invalid number: 'abc'
10 ^ 0  = Error: Unknown operator: '^'
```

---

## 📐 Design

```
Input string "10 / 3"
      │
      ▼
  parse() → Result<(f64, char, f64), CalcError>
      │
      ▼
  calculate() → Result<f64, CalcError>
      │
      ▼
  display result or error
```

---

## 🔨 Build

### Step 1: Define the Error Type

```rust
#[derive(Debug)]
enum CalcError {
    InvalidNumber(String),      // "abc" is not a number
    UnknownOperator(char),      // '^' is not supported
    DivisionByZero,             // cannot divide by zero
    ModuloByZero,               // cannot modulo by zero
    BadFormat(String),          // wrong number of parts
}

// Implement Display so we can print it cleanly
use std::fmt;
impl fmt::Display for CalcError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CalcError::InvalidNumber(s)   => write!(f, "Invalid number: '{}'", s),
            CalcError::UnknownOperator(c) => write!(f, "Unknown operator: '{}'", c),
            CalcError::DivisionByZero     => write!(f, "Division by zero"),
            CalcError::ModuloByZero       => write!(f, "Modulo by zero"),
            CalcError::BadFormat(s)       => write!(f, "Bad format: '{}'", s),
        }
    }
}
```

### Step 2: Parse the Input

```rust
fn parse_expression(expr: &str) -> Result<(f64, char, f64), CalcError> {
    // Split on whitespace: "10 + 5" → ["10", "+", "5"]
    let parts: Vec<&str> = expr.trim().split_whitespace().collect();

    if parts.len() != 3 {
        return Err(CalcError::BadFormat(expr.to_string()));
    }

    // Parse left operand
    let left: f64 = parts[0]
        .parse()
        .map_err(|_| CalcError::InvalidNumber(parts[0].to_string()))?;

    // Extract operator — must be exactly one character
    let op_str = parts[1];
    if op_str.len() != 1 {
        return Err(CalcError::UnknownOperator('?'));
    }
    let op = op_str.chars().next().unwrap();

    // Parse right operand
    let right: f64 = parts[2]
        .parse()
        .map_err(|_| CalcError::InvalidNumber(parts[2].to_string()))?;

    Ok((left, op, right))
}
```

### Step 3: Calculate

```rust
fn calculate(expr: &str) -> Result<f64, CalcError> {
    let (left, op, right) = parse_expression(expr)?; // ? propagates parse errors

    match op {
        '+' => Ok(left + right),
        '-' => Ok(left - right),
        '*' => Ok(left * right),
        '/' => {
            if right == 0.0 {
                Err(CalcError::DivisionByZero)
            } else {
                Ok(left / right)
            }
        }
        '%' => {
            if right == 0.0 {
                Err(CalcError::ModuloByZero)
            } else {
                Ok(left % right)
            }
        }
        other => Err(CalcError::UnknownOperator(other)),
    }
}
```

### Step 4: The Display Layer

```rust
fn run(expr: &str) {
    match calculate(expr) {
        Ok(result) => {
            // Format nicely: no ".0" for whole numbers
            if result.fract() == 0.0 {
                println!("{:<15} = {}", expr, result as i64);
            } else {
                println!("{:<15} = {:.4}", expr, result);
            }
        }
        Err(e) => println!("{:<15} = Error: {}", expr, e),
    }
}

fn main() {
    let expressions = [
        "10 + 5",
        "100 - 37",
        "6 * 7",
        "22 / 7",
        "10 / 0",
        "17 % 5",
        "10 % 0",
        "abc + 5",
        "10 ^ 3",
        "1 2 3 4",
    ];

    println!("{}", "=".repeat(35));
    println!("  SMART CALCULATOR");
    println!("{}", "=".repeat(35));

    for expr in &expressions {
        run(expr);
    }
}
```

```
===================================
  SMART CALCULATOR
===================================
10 + 5          = 15
100 - 37        = 63
6 * 7           = 42
22 / 7          = 3.1429
10 / 0          = Error: Division by zero
17 % 5          = 2
10 % 0          = Error: Modulo by zero
abc + 5         = Error: Invalid number: 'abc'
10 ^ 3          = Error: Unknown operator: '^'
1 2 3 4         = Error: Bad format: '1 2 3 4'
```

---

## 🔍 Deep Dive — Enums and Memory

### How Enums Are Stored in Memory

An enum in Rust is a **tagged union** — one of the oldest computer science concepts, implemented safely.

```
CalcError in memory:
┌──────────┬────────────────────────┐
│  TAG (u8)│  PAYLOAD               │
│          │  (size of largest variant)│
└──────────┴────────────────────────┘
```

The tag (discriminant) is an integer that says *which* variant this is. The payload holds that variant's data. The whole enum takes up as much space as the *largest* variant (plus the tag).

```rust
use std::mem::size_of;

println!("{}", size_of::<CalcError>());
// Each variant:
// InvalidNumber(String) = 24 bytes (String = ptr+len+cap)
// UnknownOperator(char) = 4 bytes
// DivisionByZero        = 0 bytes
// ModuloByZero          = 0 bytes
// BadFormat(String)     = 24 bytes
// 
// Total = tag(1 byte) + max payload(24 bytes) + alignment padding
// ≈ 32 bytes for the whole enum — every variant takes the same space
```

This means a `CalcError::DivisionByZero` (no data) takes the same space as `CalcError::InvalidNumber(String)` (24 bytes). That's the cost of uniformity — the compiler needs a predictable size for every enum value.

### The `?` Operator Unrolled

```rust
let left: f64 = parts[0].parse().map_err(|_| CalcError::InvalidNumber(...))?;
```

The `?` expands to roughly:
```rust
let left: f64 = match parts[0].parse().map_err(|_| CalcError::InvalidNumber(...)) {
    Ok(val) => val,          // success: unwrap and continue
    Err(e)  => return Err(e), // failure: exit this function immediately
};
```

No hidden control flow. No exceptions. `?` is just a shortcut for `match + return Err`. The entire error path is explicit and traceable.

### How the Call Stack Looks During `calculate("abc + 5")`

```
CALL STACK (grows downward):
┌──────────────────────────┐  ← top of stack (most recent call)
│  parse_expression()      │
│  parts = ["abc","+","5"] │
│  Tries: "abc".parse()    │
│  Returns: Err(InvalidNum)│
└──────────┬───────────────┘
           │ ? propagates the Err up
┌──────────▼───────────────┐
│  calculate()             │
│  Receives Err from parse │
│  Returns: Err(InvalidNum)│
└──────────┬───────────────┘
           │ match handles it
┌──────────▼───────────────┐
│  run()                   │
│  Prints: "Error: ..."    │
└──────────────────────────┘  ← bottom of stack (main)
```

No exception objects flying through the air. No hidden jumps. Just return values, moving up the call stack in a straight line.

### What `.map_err()` Does

```rust
parts[0].parse::<f64>()
    .map_err(|_| CalcError::InvalidNumber(parts[0].to_string()))
```

`parse()` returns `Result<f64, ParseFloatError>`. But our function returns `Result<f64, CalcError>`. The types don't match.

`.map_err()` transforms the error type: "if this is `Err(anything)`, replace it with `Err(CalcError::InvalidNumber(...))`. If it's `Ok`, leave it alone." This is **error type mapping** — a critical pattern in real Rust codebases.

---

## 🧠 Technique Card — Error Handling Patterns

```
┌───────────────────────────────────────────────────────────┐
│  FOUR WAYS TO HANDLE Result/Option                        │
│                                                           │
│  1. match          — full control, verbose                │
│     match r { Ok(v) => ..., Err(e) => ... }               │
│                                                           │
│  2. if let          — when you only care about one case   │
│     if let Ok(v) = r { use v }                            │
│                                                           │
│  3. ?               — propagate to caller                 │
│     let v = might_fail()?;                                │
│                                                           │
│  4. .unwrap_or(x)   — use x as default on failure        │
│     let v = r.unwrap_or(0);                               │
│                                                           │
│  TRANSFORM ERRORS                                         │
│  .map_err(|e| MyError::from(e))  — convert error type    │
│  .map(|v| v * 2)                 — transform Ok value    │
│  .and_then(|v| next_op(v))       — chain fallible ops    │
│                                                           │
│  RULE: never .unwrap() in library code.                   │
│        .unwrap() is fine in main() and tests.             │
└───────────────────────────────────────────────────────────┘
```

---

## 🦀 Activities

1. Add a `pow` operation: `"2 p 10"` → `2^10 = 1024`. Use `left.powf(right)`.
2. Add a square root: `"25 r 0"` → `5`. Handle negative input as an error.
3. Write a function `calculate_chain(exprs: &[&str]) -> Vec<Result<f64, CalcError>>` that processes a list and returns all results.
4. **Challenge:** Add a `history: Vec<String>` to a `Calculator` struct that stores every successful calculation. Implement a `last_result(&self) -> Option<f64>` method.
5. **System challenge:** Print `std::mem::size_of::<CalcError>()` before and after adding a new large variant (like `History(Vec<String>)`). Notice how the entire enum grows to fit the largest variant.

---

# Project 3: Student Grade Tracker

**Theme: Structs, Vec, HashMap, Iterators**
**System Lens: Heap layout of Vec, iterator zero-cost abstraction, cache locality**

---

## 🎯 Goal

Build a grade tracking system that stores students, computes statistics, ranks them, and generates a report — all with efficient, idiomatic Rust.

**Final output:**
```
╔══════════════════════════════════════════════╗
║           GRADE REPORT — TERM 1              ║
╠══════════════════════════════════════════════╣
║  Rank │ Name              │ Avg  │ Grade     ║
╠══════════════════════════════════════════════╣
║   1   │ Carol Adams       │ 94.3 │  A        ║
║   2   │ Ramyesh Bt        │ 88.0 │  B+       ║
║   3   │ Alice Smith       │ 79.7 │  C+       ║
║   4   │ Bob Johnson       │ 65.0 │  D        ║
╠══════════════════════════════════════════════╣
║  Class average: 81.8                         ║
║  Highest score: 98 (Carol Adams — Rust)      ║
║  Lowest score:  55 (Bob Johnson — Maths)     ║
╚══════════════════════════════════════════════╝
```

---

## 🔨 Build

### Step 1: Data Structures

```rust
use std::collections::HashMap;

#[derive(Debug, Clone)]
struct Student {
    name: String,
    scores: HashMap<String, u32>, // subject → score
}

impl Student {
    fn new(name: &str) -> Self {
        Student {
            name: name.to_string(),
            scores: HashMap::new(),
        }
    }

    fn add_score(&mut self, subject: &str, score: u32) {
        self.scores.insert(subject.to_string(), score);
    }

    fn average(&self) -> f64 {
        if self.scores.is_empty() { return 0.0; }
        let total: u32 = self.scores.values().sum();
        total as f64 / self.scores.len() as f64
    }

    fn grade(&self) -> &str {
        match self.average() as u32 {
            90..=100 => "A",
            85..=89  => "B+",
            80..=84  => "B",
            75..=79  => "C+",
            70..=74  => "C",
            60..=69  => "D",
            _        => "F",
        }
    }

    fn highest_score(&self) -> Option<(&str, u32)> {
        self.scores
            .iter()
            .max_by_key(|(_, &score)| score)
            .map(|(subject, &score)| (subject.as_str(), score))
    }

    fn lowest_score(&self) -> Option<(&str, u32)> {
        self.scores
            .iter()
            .min_by_key(|(_, &score)| score)
            .map(|(subject, &score)| (subject.as_str(), score))
    }
}
```

### Step 2: The Classroom

```rust
struct Classroom {
    students: Vec<Student>,
}

impl Classroom {
    fn new() -> Self {
        Classroom { students: Vec::new() }
    }

    fn add(&mut self, student: Student) {
        self.students.push(student);
    }

    fn ranked(&self) -> Vec<&Student> {
        let mut refs: Vec<&Student> = self.students.iter().collect();
        refs.sort_by(|a, b| {
            b.average()
                .partial_cmp(&a.average())
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        refs
    }

    fn class_average(&self) -> f64 {
        if self.students.is_empty() { return 0.0; }
        let sum: f64 = self.students.iter().map(|s| s.average()).sum();
        sum / self.students.len() as f64
    }

    fn top_score(&self) -> Option<(&str, &str, u32)> {
        // Returns (student_name, subject, score) for the highest score overall
        self.students.iter().flat_map(|student| {
            student.scores.iter().map(move |(subj, &score)| {
                (student.name.as_str(), subj.as_str(), score)
            })
        })
        .max_by_key(|(_, _, score)| *score)
    }

    fn bottom_score(&self) -> Option<(&str, &str, u32)> {
        self.students.iter().flat_map(|student| {
            student.scores.iter().map(move |(subj, &score)| {
                (student.name.as_str(), subj.as_str(), score)
            })
        })
        .min_by_key(|(_, _, score)| *score)
    }
}
```

### Step 3: The Report

```rust
fn print_report(classroom: &Classroom) {
    let ranked = classroom.ranked();
    let width = 46usize;
    let div = "═".repeat(width);

    println!("╔{}╗", div);
    println!("║{:^width$}║", "GRADE REPORT — TERM 1", width = width);
    println!("╠{}╣", div);
    println!("║  {:<5}│ {:<18}│ {:<5}│ {:<9}║", "Rank", "Name", "Avg", "Grade");
    println!("╠{}╣", div);

    for (i, student) in ranked.iter().enumerate() {
        println!(
            "║  {:<5}│ {:<18}│ {:<5.1}│  {:<8}║",
            i + 1,
            student.name,
            student.average(),
            student.grade()
        );
    }

    println!("╠{}╣", div);
    println!("║  Class average: {:<28.1}║", classroom.class_average());

    if let Some((name, subj, score)) = classroom.top_score() {
        println!("║  Highest score: {:<28}║",
            format!("{} ({} — {})", score, name, subj));
    }
    if let Some((name, subj, score)) = classroom.bottom_score() {
        println!("║  Lowest score:  {:<28}║",
            format!("{} ({} — {})", score, name, subj));
    }

    println!("╚{}╝", div);
}

fn main() {
    let mut room = Classroom::new();

    let mut s1 = Student::new("Ramyesh Bt");
    s1.add_score("Rust",   92); s1.add_score("Maths",  85);
    s1.add_score("Systems",87);

    let mut s2 = Student::new("Alice Smith");
    s2.add_score("Rust",   78); s2.add_score("Maths",  82);
    s2.add_score("Systems",79);

    let mut s3 = Student::new("Bob Johnson");
    s3.add_score("Rust",   70); s3.add_score("Maths",  55);
    s3.add_score("Systems",70);

    let mut s4 = Student::new("Carol Adams");
    s4.add_score("Rust",   98); s4.add_score("Maths",  91);
    s4.add_score("Systems",94);

    room.add(s1); room.add(s2); room.add(s3); room.add(s4);

    print_report(&room);
}
```

---

## 🔍 Deep Dive — Vec Internals and Iterator Zero-Cost

### How Vec Lives in Memory

```rust
let mut v: Vec<u32> = Vec::new();
v.push(10);
v.push(20);
v.push(30);
```

```
STACK:
┌────────────────────────────────┐
│  v: Vec<u32>                   │
│  ┌─────────────┬─────┬───────┐ │
│  │  ptr        │ len │ cap   │ │
│  │  0xABCD1234 │  3  │  4   │ │
│  └──────┬──────┴─────┴───────┘ │
└─────────┼──────────────────────┘
          │
          ▼
HEAP (contiguous block):
┌────┬────┬────┬────┐
│ 10 │ 20 │ 30 │ ?? │  ← capacity 4, only 3 used
└────┴────┴────┴────┘
  each is 4 bytes (u32)
```

**Key insight:** Vec data is **contiguous in memory**. All elements sit next to each other. This matters enormously for performance because of **CPU cache lines**.

### CPU Cache and Why Contiguous Data Wins

A modern CPU doesn't read one byte at a time from RAM. It reads a **cache line** — typically 64 bytes — all at once. If your data is contiguous (like a Vec), reading element 0 also loads elements 1–15 into the CPU cache for free.

If your data is scattered (like a linked list), each element requires a separate cache miss — a round-trip to RAM that costs ~100x more time than reading from cache.

```
Vec lookup (cache-friendly):
[0][1][2][3][4][5][6][7][8][9][10][11][12][13][14][15]  ← all loaded in 1 cache line
  ↑
  read [0] → CPU loads [0]..[15] for free

Linked List (cache-hostile):
[0]→pointer→[1]→pointer→[2]→pointer→...
  ↑
  read [0] → must follow pointer → cache miss → read [1] → cache miss → ...
```

When Rust's borrow checker forces you to use `&[T]` slices and contiguous Vecs, it's also nudging you toward cache-friendly patterns.

### Vec Growth Strategy (Amortised O(1))

When `push()` exceeds capacity, Vec doubles its allocation:

```
Start:   capacity 0, len 0
push(1): allocate 4,  copy, len 1, cap 4
push(2): len 2, cap 4 (no allocation)
push(3): len 3, cap 4 (no allocation)
push(4): len 4, cap 4 (no allocation)
push(5): allocate 8,  copy all, len 5, cap 8  ← reallocation
push(6): len 6, cap 8 (no allocation)
...
```

Doubling means you reallocate logarithmically — O(log n) times for n pushes. Spread over n operations: **O(1) amortised per push**. If you know the size upfront, use `Vec::with_capacity(n)` to skip all reallocations.

### Iterator Zero-Cost Abstraction

```rust
let sum: f64 = self.students.iter().map(|s| s.average()).sum();
```

This looks like Python-style functional code — but compiles to the **same machine code** as a manual `for` loop. The compiler inlines each `.map()`, `.filter()`, etc. at compile time, producing a tight loop with no overhead.

This is what Rust means by **zero-cost abstractions**: you pay for what you use, and you use what you want — the abstraction is free.

Underneath, the iterator is a state machine: a struct with a `next()` method that the compiler expands into a loop. No closures survive to runtime. No function call overhead. The CPU sees a simple increment-and-compare loop.

---

## 🧠 Technique Card — Iterators

```
┌───────────────────────────────────────────────────────────┐
│  ITERATOR CHEAT CARD                                      │
│                                                           │
│  PRODUCERS (start the chain)                              │
│  .iter()          → references: &T                        │
│  .iter_mut()      → mutable refs: &mut T                  │
│  .into_iter()     → consumes collection, gives owned T    │
│                                                           │
│  ADAPTERS (transform — lazy, no work until consumed)      │
│  .map(|x| ...)    → transform each element                │
│  .filter(|x| ...) → keep only matching elements           │
│  .flat_map(...)   → map then flatten one level            │
│  .enumerate()     → yields (index, value) pairs           │
│  .zip(other)      → pair up two iterators                 │
│  .take(n)         → only first n elements                 │
│  .skip(n)         → skip first n elements                 │
│  .chain(other)    → concatenate two iterators             │
│                                                           │
│  CONSUMERS (trigger computation, return a value)          │
│  .collect()       → gather into Vec, HashMap, etc.        │
│  .sum()           → add all values                        │
│  .count()         → number of elements                    │
│  .max() / .min()  → largest/smallest (returns Option)     │
│  .find(|x| ...)   → first matching element (Option)       │
│  .any(|x| ...)    → true if any element matches           │
│  .all(|x| ...)    → true if all elements match            │
│  .fold(init, fn)  → accumulate into any type              │
│                                                           │
│  GOLDEN RULE: adapters are lazy. consumers drive them.    │
└───────────────────────────────────────────────────────────┘
```

---

## 🦀 Activities

1. Add a `subjects_above(threshold: u32) -> Vec<&str>` method to `Student` that returns subjects where the score exceeds the threshold.
2. Compute the **median** score across all students for a specific subject. Handle the case where no student has that subject.
3. Add a `struggling_students(threshold: f64) -> Vec<&Student>` method to `Classroom` that returns students below the given average.
4. **Challenge:** Use `.fold()` to compute both the min and max average in a single pass through the students, returning `(f64, f64)`.
5. **System challenge:** Use `Vec::with_capacity(100)` for the students Vec. Compare `v.len()` and `v.capacity()` after adding 4 students. Why is capacity 100 and len 4?

---

# Project 4: Memory Explorer

**Theme: Box, References, Sizes, Pointers**
**System Lens: Stack vs heap, virtual memory, OS pages, the allocator**

---

## 🎯 Goal

Build a tool that **inspects its own memory** — printing sizes, addresses, and layouts of data structures. This is the most system-focused project. You'll see exactly where your data lives and why.

---

## 🔨 Build

### Step 1: Measuring Sizes

```rust
use std::mem::{size_of, size_of_val};

fn main() {
    // Primitive sizes
    println!("=== PRIMITIVE SIZES ===");
    println!("bool    : {} bytes", size_of::<bool>());
    println!("char    : {} bytes", size_of::<char>());   // 4! Unicode scalar
    println!("i32     : {} bytes", size_of::<i32>());
    println!("i64     : {} bytes", size_of::<i64>());
    println!("f64     : {} bytes", size_of::<f64>());
    println!("usize   : {} bytes", size_of::<usize>()); // pointer size: 8 on 64-bit

    // Compound types
    println!("\n=== COMPOUND TYPES ===");
    println!("&str    : {} bytes", size_of::<&str>());   // ptr + len = 16
    println!("String  : {} bytes", size_of::<String>()); // ptr + len + cap = 24
    println!("Vec<i32>: {} bytes", size_of::<Vec<i32>>());  // same as String: 24

    // Pointer types
    println!("\n=== POINTER TYPES ===");
    println!("&i32    : {} bytes", size_of::<&i32>());   // just a pointer: 8
    println!("Box<i32>: {} bytes", size_of::<Box<i32>>()); // just a pointer: 8
    println!("Option<&i32>: {} bytes", size_of::<Option<&i32>>()); // still 8! (null optimisation)
    println!("Option<i32>: {} bytes",  size_of::<Option<i32>>());  // 8 (4 + tag)
}
```

```
=== PRIMITIVE SIZES ===
bool    : 1 bytes
char    : 4 bytes
i32     : 4 bytes
i64     : 8 bytes
f64     : 8 bytes
usize   : 8 bytes

=== COMPOUND TYPES ===
&str    : 16 bytes
String  : 24 bytes
Vec<i32>: 24 bytes

=== POINTER TYPES ===
&i32    : 8 bytes
Box<i32>: 8 bytes
Option<&i32>: 8 bytes
Option<i32> : 8 bytes
```

### Step 2: Printing Memory Addresses

```rust
fn main() {
    let stack_int: i32 = 42;
    let stack_str: &str = "hello";
    let heap_string = String::from("world");
    let boxed = Box::new(100i32);

    println!("=== MEMORY ADDRESSES ===");
    println!("stack_int  lives at: {:p}", &stack_int);
    println!("stack_str  lives at: {:p}", &stack_str);
    println!("heap data  lives at: {:p}", heap_string.as_ptr()); // actual heap addr
    println!("String struct at:    {:p}", &heap_string);         // stack addr of struct
    println!("boxed ptr  lives at: {:p}", &boxed);               // stack addr of Box
    println!("boxed data lives at: {:p}", &*boxed);              // heap addr of value
}
```

```
=== MEMORY ADDRESSES ===
stack_int  lives at: 0x7ffd5e3a1b4c     ← high address = stack
stack_str  lives at: 0x7ffd5e3a1b50
heap data  lives at: 0x55d8b2c4f9a0     ← low address = heap
String struct at:    0x7ffd5e3a1b58     ← struct is on stack
boxed ptr  lives at: 0x7ffd5e3a1b68     ← Box handle on stack
boxed data lives at: 0x55d8b2c4f9c0     ← data on heap
```

> **Pattern to notice:** Stack addresses are high (start near top of virtual address space and grow down). Heap addresses are low (start near the bottom and grow up). They grow toward each other. On a 64-bit system there's so much virtual address space between them that they'll never meet.

### Step 3: Box — Heap Allocation with Ownership

```rust
fn main() {
    // Without Box — data on stack
    let stack_val: i32 = 42;

    // With Box — data on heap, ownership tracked
    let heap_val: Box<i32> = Box::new(42);

    // Dereferencing works transparently
    println!("stack: {}", stack_val);
    println!("heap:  {}", *heap_val);   // explicit deref
    println!("heap:  {}", heap_val);    // auto-deref in println

    // Box is useful for:
    // 1. Recursive types (size unknown at compile time)
    // 2. Large values you want on the heap
    // 3. Trait objects (dyn Trait)

    // Recursive type — only possible with Box
    #[derive(Debug)]
    enum List {
        Node(i32, Box<List>), // Box breaks the infinite size recursion
        End,
    }

    let list = List::Node(1,
                Box::new(List::Node(2,
                    Box::new(List::Node(3,
                        Box::new(List::End))))));

    println!("{:?}", list);
}
```

### Step 4: Observing Drop Order

```rust
struct Droppable {
    name: &'static str,
}

impl Drop for Droppable {
    fn drop(&mut self) {
        println!("  → Dropping: {}", self.name);
    }
}

fn demonstrate_drop() {
    println!("[entering function scope]");
    let a = Droppable { name: "a — first created" };
    let b = Droppable { name: "b — second created" };
    {
        let c = Droppable { name: "c — inner scope" };
        println!("[exiting inner scope]");
    } // c dropped here
    let d = Droppable { name: "d — after inner scope" };
    println!("[exiting function scope]");
    // d, b, a dropped here — in REVERSE order of creation (LIFO)
}

fn main() {
    demonstrate_drop();
}
```

```
[entering function scope]
[exiting inner scope]
  → Dropping: c — inner scope
[exiting function scope]
  → Dropping: d — after inner scope
  → Dropping: b — second created
  → Dropping: a — first created
```

**LIFO (Last In, First Out)** — the same order as a stack. Variables are dropped in reverse creation order because that's the order the stack unwinds. This is deterministic, predictable, and essential for managing resources like file handles and network connections.

---

## 🔍 Deep Dive — Virtual Memory and the OS

### What "Memory Address" Actually Means

When your program prints `0x7ffd5e3a1b4c`, that's a **virtual address** — not a physical RAM address. The OS gives every process its own private virtual address space (on 64-bit: 128 TB of address space on Linux).

```
YOUR PROCESS VIRTUAL ADDRESS SPACE (simplified):
┌──────────────────────────────┐  ← High addresses (~0x7FFFFFFF)
│  Stack                       │  grows ↓
│  (local vars, function args) │
├──────────────────────────────┤
│                              │  (huge empty space — virtual)
│  (unmapped — would fault)    │
│                              │
├──────────────────────────────┤
│  Heap                        │  grows ↑
│  (malloc/Box/Vec/String data)│
├──────────────────────────────┤
│  BSS (uninitialised globals) │
├──────────────────────────────┤
│  Data (initialised globals)  │
├──────────────────────────────┤
│  Text (your compiled code)   │  ← Low addresses (~0x400000)
└──────────────────────────────┘
```

The OS **memory-maps** virtual addresses to physical RAM pages (4KB each) on demand. When you first write to a new page, a **page fault** fires — the CPU traps to the OS kernel, which finds a free physical page, maps it to your virtual address, and resumes your program. You never see this happen.

### What `Box::new(42)` Does at the OS Level

```
1. Rust calls the allocator (e.g., jemalloc or system malloc)
2. Allocator checks its free list for a suitable block
3. If no block: calls mmap() or brk() syscall → OS kernel
4. Kernel finds a physical page, maps it to virtual address
5. Allocator returns pointer to the block
6. Box::new writes 42 into those bytes
7. Box stores the pointer on the stack (8 bytes)

When Box drops:
1. Rust calls drop() → calls the allocator free()
2. Allocator marks the block as available in its free list
3. Physical page is NOT immediately returned to OS (reused later)
```

### What a Stack Frame Is

Every function call creates a **stack frame** — a region of the stack holding that function's local variables, parameters, and return address.

```
main() calls calculate() calls parse_expression():

STACK (grows downward):
┌──────────────────────┐ ← stack pointer (SP)
│  parse_expression    │
│  parts: Vec (24 B)   │
│  left:  f64  (8 B)   │
│  op:    char (4 B)   │
│  right: f64  (8 B)   │
├──────────────────────┤
│  calculate           │
│  expr: &str (16 B)   │
│  return address      │
├──────────────────────┤
│  main                │
│  expressions: [...]  │
└──────────────────────┘ ← stack base
```

When `parse_expression()` returns, its entire frame is **popped** in a single CPU instruction (adjusting the stack pointer). No allocation. No deallocation. Instant.

This is why stack allocation is so much faster than heap allocation — it's just a pointer adjustment.

---

## 🧠 Technique Card — Memory Mental Model

```
┌───────────────────────────────────────────────────────────┐
│  WHERE DOES MY DATA LIVE?                                 │
│                                                           │
│  STACK  — fast, automatic, size known at compile time     │
│    • All integer/float/bool/char variables                │
│    • Struct instances (if not Boxed)                      │
│    • String/Vec/Box HANDLES (the ptr+len+cap structs)     │
│    • Function parameters and return addresses             │
│                                                           │
│  HEAP   — flexible, manual (via allocator), any size      │
│    • The actual content of String, Vec, Box               │
│    • Anything you explicitly Box::new()                   │
│    • Data that outlives a single function call            │
│                                                           │
│  BINARY  — read-only, baked in at compile time            │
│    • String literals: "hello" ← this never moves         │
│    • Your compiled machine code                           │
│    • Static/const data                                    │
│                                                           │
│  QUICK TEST: "does the compiler know the size at         │
│  compile time?" YES → stack.  NO → heap.                 │
└───────────────────────────────────────────────────────────┘
```

---

## 🦀 Activities

1. Print the size of your `Attendee` struct from Project 1 using `size_of::<Attendee>()`. Calculate it manually field by field. If it's larger, research **struct field alignment padding**.
2. Create a `Box<Vec<String>>`. Print the addresses of: the Box handle, the Vec struct inside it, and the first String's heap data. Draw the chain on paper.
3. Implement the `Drop` trait for a `DatabaseConnection` struct that prints `"Closing connection..."`. Prove it fires at the right time.
4. **Challenge:** Create a `List` enum (as shown above) with 1,000 nodes. Use `Box` to put each node on the heap. What happens if you make it recursive WITHOUT `Box`? (Hint: infinite size — won't compile.)
5. **System challenge:** Print the address of two consecutive stack variables. Subtract them. What is the gap? Does it match the size of the first variable? What does this tell you about stack layout?

---

# Project 5: Mini Command-Line Todo App

**Theme: Everything combined + user input + modules**
**System Lens: stdin/stdout as file descriptors, system calls, process memory**

---

## 🎯 Goal

Build a complete, interactive command-line todo list app. This project combines every concept from the course into one working program.

```
╔════════════════════════════════╗
║     🦀 RUST TODO MANAGER      ║
╠════════════════════════════════╣
║  Commands:                     ║
║  add <task>    — add a task    ║
║  done <id>     — mark done     ║
║  remove <id>   — remove task   ║
║  list          — show all      ║
║  clear         — remove done   ║
║  quit          — exit          ║
╚════════════════════════════════╝
> add Learn Rust ownership
✅ Added: "Learn Rust ownership" [#1]
> add Write cheat cards
✅ Added: "Write cheat cards" [#2]
> list

  #1  [ ] Learn Rust ownership
  #2  [ ] Write cheat cards

> done 1
✅ Marked done: "Learn Rust ownership"
> list

  #1  [✓] Learn Rust ownership
  #2  [ ] Write cheat cards

> quit
Goodbye! 👋
```

---

## 🔨 Build

### Step 1: Core Data Types

```rust
use std::io::{self, BufRead, Write};

#[derive(Debug, Clone)]
struct Task {
    id: u32,
    description: String,
    done: bool,
}

impl Task {
    fn new(id: u32, description: &str) -> Self {
        Task {
            id,
            description: description.trim().to_string(),
            done: false,
        }
    }

    fn display(&self) {
        let check = if self.done { "✓" } else { " " };
        println!("  #{:<3} [{}] {}", self.id, check, self.description);
    }
}
```

### Step 2: The App State and Commands

```rust
#[derive(Debug)]
enum Command {
    Add(String),
    Done(u32),
    Remove(u32),
    List,
    Clear,
    Quit,
    Unknown(String),
}

fn parse_command(input: &str) -> Command {
    let input = input.trim();
    let (cmd, rest) = input
        .split_once(' ')
        .map(|(a, b)| (a, b.trim()))
        .unwrap_or((input, ""));

    match cmd.to_lowercase().as_str() {
        "add"    if !rest.is_empty() => Command::Add(rest.to_string()),
        "done"   => rest.parse::<u32>().map(Command::Done)
                        .unwrap_or(Command::Unknown("done needs a number".into())),
        "remove" => rest.parse::<u32>().map(Command::Remove)
                        .unwrap_or(Command::Unknown("remove needs a number".into())),
        "list"   => Command::List,
        "clear"  => Command::Clear,
        "quit" | "exit" | "q" => Command::Quit,
        _        => Command::Unknown(input.to_string()),
    }
}

struct TodoApp {
    tasks: Vec<Task>,
    next_id: u32,
}

impl TodoApp {
    fn new() -> Self {
        TodoApp { tasks: Vec::new(), next_id: 1 }
    }

    fn run_command(&mut self, cmd: Command) -> bool {
        match cmd {
            Command::Add(desc) => {
                let id = self.next_id;
                self.tasks.push(Task::new(id, &desc));
                self.next_id += 1;
                println!("✅ Added: \"{}\" [#{}]", desc, id);
            }
            Command::Done(id) => {
                match self.tasks.iter_mut().find(|t| t.id == id) {
                    Some(task) => {
                        task.done = true;
                        println!("✅ Marked done: \"{}\"", task.description);
                    }
                    None => println!("❌ No task with id #{}", id),
                }
            }
            Command::Remove(id) => {
                let before = self.tasks.len();
                self.tasks.retain(|t| t.id != id);
                if self.tasks.len() < before {
                    println!("🗑️  Removed task #{}", id);
                } else {
                    println!("❌ No task with id #{}", id);
                }
            }
            Command::List => {
                if self.tasks.is_empty() {
                    println!("  (no tasks)");
                } else {
                    println!();
                    for task in &self.tasks {
                        task.display();
                    }
                    let done_count = self.tasks.iter().filter(|t| t.done).count();
                    println!("\n  {}/{} done", done_count, self.tasks.len());
                }
            }
            Command::Clear => {
                let before = self.tasks.len();
                self.tasks.retain(|t| !t.done);
                let removed = before - self.tasks.len();
                println!("🧹 Cleared {} completed task(s)", removed);
            }
            Command::Quit => {
                println!("Goodbye! 👋");
                return false; // signal to stop the loop
            }
            Command::Unknown(s) => {
                println!("❓ Unknown command: \"{}\"", s);
            }
        }
        true // continue running
    }
}
```

### Step 3: The Main Loop

```rust
fn print_banner() {
    println!("╔════════════════════════════════╗");
    println!("║     🦀 RUST TODO MANAGER      ║");
    println!("╠════════════════════════════════╣");
    println!("║  add <task>  done <id>         ║");
    println!("║  remove <id> list  clear  quit ║");
    println!("╚════════════════════════════════╝");
}

fn main() {
    print_banner();

    let mut app = TodoApp::new();
    let stdin = io::stdin();

    loop {
        print!("> ");
        io::stdout().flush().unwrap(); // ensure ">" appears before input

        let mut line = String::new();
        match stdin.lock().read_line(&mut line) {
            Ok(0) => break, // EOF — user pressed Ctrl+D
            Ok(_) => {
                let cmd = parse_command(&line);
                if !app.run_command(cmd) {
                    break;
                }
            }
            Err(e) => {
                eprintln!("Read error: {}", e);
                break;
            }
        }
    }
}
```

---

## 🔍 Deep Dive — stdin, stdout, and System Calls

### File Descriptors — Everything Is a File

In Unix-like systems (and Windows similarly), every I/O channel is represented as a **file descriptor** — a small integer:

```
File Descriptor 0 = stdin  (keyboard by default)
File Descriptor 1 = stdout (terminal by default)
File Descriptor 2 = stderr (terminal, unbuffered)
```

When your program calls `println!("hello")`:
1. Rust calls the `write()` **system call** with fd=1 and the bytes `"hello\n"`
2. The CPU switches from **user mode** to **kernel mode** (a privilege boundary)
3. The kernel's `write` handler receives the bytes
4. The kernel finds the terminal driver associated with fd 1
5. The terminal driver converts the bytes to screen output
6. Control returns to your program in user mode

This context switch (user mode ↔ kernel mode) takes ~100–1000 nanoseconds. It's why **buffering** exists — instead of one `write()` syscall per character, Rust's `BufWriter` accumulates data and flushes in large batches.

### Why `stdout().flush()` Is Needed

```rust
print!("> ");              // writes to buffer — NOT yet on screen
io::stdout().flush()?;     // force the buffer to emit a syscall NOW
```

`print!` (without newline) writes to a **buffered** stdout. The buffer only flushes automatically when it's full or when a newline is written. Without `flush()`, the prompt `>` wouldn't appear before the program blocks waiting for input — the user would see a blank line.

### `.retain()` — How In-Place Filtering Works

```rust
self.tasks.retain(|t| t.id != id);
```

Under the hood, `retain()` does a single pass through the Vec:

```
Before: [T1, T2(remove), T3, T4]
                ↑ should be removed

retain scans left-to-right with two indices:
  read_idx  = 0, 1, 2, 3  (reads every element)
  write_idx = 0,    1, 2  (writes only kept elements)

After one pass:
  [T1, T3, T4, ??]   ← write_idx = 3
  truncate to len 3
  [T1, T3, T4]
```

One pass. No second allocation. O(n) time, O(1) extra memory. This is the Rust way — efficient by default.

### `.iter_mut()` — Mutable References Inside a Borrow

```rust
self.tasks.iter_mut().find(|t| t.id == id)
```

`iter_mut()` yields `&mut Task` — mutable references to each task. Crucially, Rust guarantees you can only have one `&mut Task` alive at a time, so you can't accidentally call `iter_mut()` twice simultaneously. The borrow checker enforces this, preventing data races even in single-threaded code.

---

## 🧠 Final Technique Card — Putting It All Together

```
┌────────────────────────────────────────────────────────────┐
│  PATTERNS EVERY RUST DEVELOPER USES DAILY                  │
│                                                            │
│  ① OPTION/RESULT CHAINS                                    │
│    value.map(|v| transform(v))                             │
│         .and_then(|v| fallible(v))                         │
│         .unwrap_or(default)                                │
│                                                            │
│  ② ITERATOR PIPELINES                                      │
│    collection.iter()                                       │
│              .filter(|x| condition)                        │
│              .map(|x| transform)                           │
│              .collect::<Vec<_>>()                          │
│                                                            │
│  ③ IN-PLACE MUTATION                                       │
│    vec.retain(|x| keep_condition);   // filter             │
│    vec.sort_by_key(|x| x.field);     // sort               │
│    vec.dedup();                       // remove duplicates  │
│                                                            │
│  ④ PATTERN MATCH ON FIRST WORD                             │
│    match input.split_once(' ') {                           │
│        Some((cmd, rest)) => ...,                           │
│        None              => handle_single_word             │
│    }                                                       │
│                                                            │
│  ⑤ ENTRY API (HashMap upsert)                              │
│    map.entry(key).or_insert(0) += 1;                       │
│                                                            │
│  ⑥ BUFFERED I/O                                            │
│    Always flush() after print!()                          │
│    Use BufReader/BufWriter for file I/O                    │
└────────────────────────────────────────────────────────────┘
```

---

## 🦀 Final Activities — Full Challenge Set

**Beginner:**
1. Add a `priority: u8` field (1–3) to `Task`. Print high-priority tasks with `❗` prefix.
2. Add an `edit <id> <new text>` command that updates a task's description.

**Moderate:**
3. Add `save` and `load` commands using `std::fs::write` and `std::fs::read_to_string`. Serialize tasks as plain text (one per line: `id|done|description`).
4. Add a `search <keyword>` command that lists tasks containing the keyword (case-insensitive).

**Advanced:**
5. Add a `stats` command that prints: total tasks, done count, pending count, longest task description, and average description length.
6. **System challenge:** Use `std::time::Instant` to timestamp when each task was created. Print how long ago each task was created in the `list` command. Research `Duration` and `.elapsed()`.

---

## Your Complete Journey So Far

```
✅ Project 1 — Name Card Generator
   Strings · Formatting · Structs · Sorting
   SYSTEM: String memory layout · UTF-8 · Stack vs Heap

✅ Project 2 — Smart Calculator
   Enums · Pattern matching · Custom errors · ? operator
   SYSTEM: Enum tagged unions · Call stack · Error propagation

✅ Project 3 — Student Grade Tracker
   HashMap · Vec · Iterators · Sorting
   SYSTEM: Vec contiguous memory · Cache lines · Zero-cost iterators

✅ Project 4 — Memory Explorer
   Box · Drop · size_of · Memory addresses
   SYSTEM: Virtual memory · OS pages · Stack frames · Allocator

✅ Project 5 — Todo App
   All concepts combined · stdin/stdout · Modules · State
   SYSTEM: File descriptors · Syscalls · User/Kernel mode · Buffering
```

Every bug you hit, every compiler error you read, every `unwrap()` you replaced with proper error handling — that's not frustration. That's Rust teaching you to think like the machine, one concept at a time.

---

## Where to Go From Here

You've completed the core of this guide. You can read Rust, reason about ownership, handle errors honestly, and you've seen what happens beneath your code at the memory and OS level. That's a genuine foundation — be proud of it.

To keep going, these are the best free next steps:

| Resource | What it's good for |
|----------|--------------------|
| [The Rust Book](https://doc.rust-lang.org/book/) | The official, complete guide — your natural next read |
| [Rustlings](https://github.com/rust-lang/rustlings) | Small hands-on exercises that compile-check your understanding |
| [Rust by Example](https://doc.rust-lang.org/rust-by-example/) | Runnable examples for nearly every feature |
| [Rust Playground](https://play.rust-lang.org) | Keep experimenting — break things, read errors, learn |

**Topics to explore next**, now that the foundation is solid:

- **Traits** — shared behaviour across types (like interfaces, but better)
- **Generics** — write code once, use it with many types
- **Closures & iterators** — Rust's expressive functional style (you've already tasted these)
- **Modules & crates** — organizing larger projects with Cargo
- **Concurrency** — Rust's "fearless concurrency," where the borrow checker prevents data races across threads

> The rules you learned here — ownership, borrowing, lifetimes — don't change as you advance. Everything else in Rust is built on the foundation you now have. Keep building. 🦀

---

*Previous: [Cheat Cards](04_cheat_cards.md)*
*Back to start: [Why Rust? The Hook](01_hook.md)*
