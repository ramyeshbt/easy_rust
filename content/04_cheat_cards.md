# Cheat Cards — Everything on One Page

> "The secret of a good memory is attention, and attention to a subject depends upon our interest in it."
> — Tryon Edwards

These cards are designed to be **scanned, not read**. Each one is a one-page summary of a core concept. Use them to:

- **Review** before sleep (spaced repetition works)
- **Reference** when your code won't compile
- **Print** and pin near your desk
- **Quiz yourself** — cover the right column and recall the left

---

## How to Use These Cards

Each card follows this layout:

```
┌─────────────────────────────────┐
│  CARD TITLE          #NUMBER   │
│  One-line summary               │
├────────────────┬────────────────┤
│  RULE / TERM   │  MEANING       │
│  ...           │  ...           │
├────────────────┴────────────────┤
│  CODE SNAPSHOT                  │
├─────────────────────────────────┤
│  🧠 MEMORY HOOK                 │
│  ⚠️  COMMON MISTAKE             │
└─────────────────────────────────┘
```

---

## Card 1 — Variables & Mutability

> **Core idea:** Variables are frozen by default. You must opt in to change.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 1: VARIABLES & MUTABILITY                             │
│  "Frozen until you say mut"                                 │
├───────────────────────┬─────────────────────────────────────┤
│  let x = 5            │  Immutable — cannot be changed      │
│  let mut x = 5        │  Mutable — can be reassigned        │
│  let x: i32 = 5       │  Explicit type annotation           │
│  let x = 5; let x = 6 │  Shadowing — new variable, same name│
│  const MAX: u32 = 100 │  Compile-time constant, always typed│
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  let score = 10;         // frozen                          │
│  let mut lives = 3;      // changeable                      │
│  lives -= 1;             // ✅ allowed                      │
│  score = 20;             // ❌ error: cannot assign twice   │
│                                                             │
│  let msg = "hello";      // shadowing                       │
│  let msg = msg.len();    // msg is now usize 5, not &str    │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  Variables are ICE CUBES. Add `mut` to thaw them.          │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Forgetting `mut` on a loop counter or accumulator.        │
│  Fix: let mut total = 0;                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 2 — Data Types at a Glance

> **Core idea:** Every value has a type. Rust always knows what's in the box.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 2: DATA TYPES                                         │
│  "Labeled boxes — the compiler always knows what's inside"  │
├───────────────────────┬─────────────────────────────────────┤
│  i32                  │  Signed integer (default int)       │
│  u32                  │  Unsigned integer (no negatives)    │
│  f64                  │  Float (default decimal, 64-bit)    │
│  bool                 │  true / false                       │
│  char                 │  Single character — use ' '         │
│  &str                 │  Borrowed string literal            │
│  String               │  Owned, growable string             │
│  (i32, &str, bool)    │  Tuple — mixed types, fixed size    │
│  [i32; 5]             │  Array — same type, fixed size      │
│  Vec<i32>             │  Vector — same type, growable       │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  let age: i32 = 28;                                         │
│  let pi = 3.14_f64;          // _ as digit separator       │
│  let active: bool = true;                                   │
│  let grade: char = 'A';                                     │
│  let name: &str = "Ferris";  // literal — lives in binary  │
│  let s = String::from("hi"); // heap-allocated             │
│  let pair = (42, "hello");   // tuple                      │
│  let nums = [1, 2, 3, 4, 5]; // array, length = 5         │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  i = "I can go negative"  (signed)                         │
│  u = "Up from zero only"  (unsigned)                       │
│  The number = bits:  8 / 16 / 32 / 64 / 128               │
│                                                             │
│  &str = a VIEW of a string (borrowed)                      │
│  String = the string ITSELF (owned)                        │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Mixing &str and String in the same collection.             │
│  Fix: Vec<String> and call .to_string() on literals.       │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 3 — Ownership

> **Core idea:** Every value has one owner. One owner only. Owner gone → value gone.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 3: OWNERSHIP                                          │
│  "One value. One owner. Always."                            │
├───────────────────────┬─────────────────────────────────────┤
│  RULE 1               │  Every value has one owner          │
│  RULE 2               │  Only one owner at a time           │
│  RULE 3               │  Owner out of scope → value dropped │
│  Move                 │  let b = a  →  a is gone            │
│  Clone                │  let b = a.clone()  →  both exist   │
│  Copy                 │  Integers/bools — auto-copied, not moved│
│  drop()               │  Explicitly free a value early      │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  let s1 = String::from("hello");                           │
│  let s2 = s1;          // s1 MOVED to s2                   │
│  println!("{}", s1);   // ❌ s1 is gone                    │
│  println!("{}", s2);   // ✅ s2 owns it now                │
│                                                             │
│  let s3 = s2.clone();  // explicit deep copy               │
│  println!("{} {}", s2, s3); // ✅ both alive               │
│                                                             │
│  let x = 5;                                                 │
│  let y = x;            // COPIED — x is still valid        │
│  println!("{} {}", x, y); // ✅ integers are Copy          │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  HOT POTATO 🥔 — only one person holds it at a time.       │
│  Pass it on → you let go. Clone → you make a new potato.   │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Passing a String to a function, then using it after.      │
│  Fix: pass &String instead, or return it back from fn.     │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 4 — Borrowing & References

> **Core idea:** Lend without giving up ownership. Many readers or one writer — never both.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 4: BORROWING & REFERENCES                             │
│  "Lend the book. Keep owning it."                           │
├───────────────────────┬─────────────────────────────────────┤
│  &T                   │  Immutable reference — read only    │
│  &mut T               │  Mutable reference — read & write   │
│  Many &T at once      │  ✅ Allowed                         │
│  One &mut T at a time │  ✅ Allowed (exclusive)             │
│  &T + &mut T together │  ❌ Forbidden                       │
│  Two &mut T together  │  ❌ Forbidden                       │
│  *r                   │  Dereference — access the value     │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  fn read(s: &String) {          // borrows, doesn't own    │
│      println!("{}", s);         // can read                 │
│  }                              // s NOT dropped here       │
│                                                             │
│  fn edit(s: &mut String) {      // mutable borrow          │
│      s.push_str("!!!");         // can modify               │
│  }                              // s NOT dropped here       │
│                                                             │
│  let mut text = String::from("hello");                      │
│  read(&text);           // ✅ lend immutably               │
│  edit(&mut text);       // ✅ lend mutably                 │
│  println!("{}", text);  // ✅ still our value              │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  LIBRARY READING ROOM 📚                                    │
│  Many people can READ the same book simultaneously.        │
│  Only ONE person can WRITE in it — and no one reads then.  │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Creating a &mut ref and a & ref to the same value.        │
│  Fix: finish all reads before creating a mutable borrow.   │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 5 — Lifetimes

> **Core idea:** A reference cannot outlive the data it points to. The compiler tracks this for you.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 5: LIFETIMES                                          │
│  "References expire when their data does"                   │
├───────────────────────┬─────────────────────────────────────┤
│  Lifetime             │  How long a reference stays valid   │
│  'a                   │  Lifetime annotation (a label)      │
│  fn f<'a>(x: &'a T)   │  "x lives at least as long as 'a"  │
│  Dangling pointer     │  Reference to dropped data — BANNED │
│  Lifetime elision     │  Compiler infers lifetimes for you  │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  // Compiler infers — no annotation needed (most cases):   │
│  fn first_word(s: &str) -> &str {                          │
│      &s[..s.find(' ').unwrap_or(s.len())]                  │
│  }                                                          │
│                                                             │
│  // Explicit annotation — only needed when ambiguous:      │
│  fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {      │
│      if x.len() > y.len() { x } else { y }                 │
│  }                                                          │
│                                                             │
│  // What lifetimes PREVENT:                                 │
│  let r;                                                     │
│  {                                                          │
│      let x = 5;                                             │
│      r = &x;   // ❌ x dropped at }, r would dangle        │
│  }                                                          │
│  println!("{}", r); // compiler stops this                  │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  RENTAL AGREEMENT 📄 — the borrowed car must be returned   │
│  before the owner moves away. If the owner disappears,     │
│  the reference becomes invalid — Rust prevents this.       │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Trying to return a reference to a local variable.         │
│  Fix: return the owned value (String, Vec, etc.) instead.  │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 6 — Control Flow

> **Core idea:** `if` and `match` return values. `match` must be exhaustive.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 6: CONTROL FLOW                                       │
│  "`match` is a contract. `if` is an expression."           │
├───────────────────────┬─────────────────────────────────────┤
│  if / else if / else  │  Standard branching                 │
│  if as expression     │  let x = if cond { a } else { b }  │
│  match                │  Exhaustive pattern matching        │
│  _                    │  Wildcard — catches all remaining   │
│  loop                 │  Loop forever; break with value     │
│  while cond           │  Loop while condition is true       │
│  for x in iter        │  Iterate over a collection          │
│  1..5                 │  Range: 1, 2, 3, 4 (exclusive end) │
│  1..=5                │  Range: 1, 2, 3, 4, 5 (inclusive)  │
│  continue             │  Skip to next loop iteration        │
│  break value          │  Exit loop, return a value          │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  // if as expression                                        │
│  let label = if score >= 90 { "A" } else { "B" };          │
│                                                             │
│  // match — must handle ALL cases                           │
│  match grade {                                              │
│      'A' => println!("Excellent"),                         │
│      'B' | 'C' => println!("Good"),                        │
│      'D' => println!("Needs work"),                        │
│      _ => println!("Invalid"),   // wildcard               │
│  }                                                          │
│                                                             │
│  // loop returning a value                                  │
│  let found = loop {                                         │
│      if condition { break 42; }  // returns 42             │
│  };                                                         │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  MATCH = VENDING MACHINE 🎰 — every button must be labeled.│
│  _ is the "anything else" button. Without it,              │
│  the compiler refuses to sell you anything.                │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Forgetting _ in match → "non-exhaustive patterns" error.  │
│  Also: mismatched types in if-else branches.               │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 7 — Functions

> **Core idea:** The last expression in a function body is its return value. No semicolon needed.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 7: FUNCTIONS                                          │
│  "No semicolon = return value. Semicolon = statement."     │
├───────────────────────┬─────────────────────────────────────┤
│  fn name(p: T) -> R   │  Function signature                 │
│  { expr }             │  Implicit return (no semicolon)     │
│  return expr;         │  Explicit early return              │
│  -> ()                │  Returns nothing (unit type)        │
│  fn f<T>(x: T)        │  Generic function (any type T)      │
│  Block expression     │  { let x = 1; x + 2 } → value 3    │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  fn square(n: i32) -> i32 {                                │
│      n * n   // implicit return — NO semicolon             │
│  }                                                          │
│                                                             │
│  fn safe_div(a: f64, b: f64) -> f64 {                      │
│      if b == 0.0 { return 0.0; } // early return           │
│      a / b                        // implicit return        │
│  }                                                          │
│                                                             │
│  fn stats(nums: &[i32]) -> (i32, i32) { // return tuple    │
│      (*nums.iter().min().unwrap(),                          │
│       *nums.iter().max().unwrap())                          │
│  }                                                          │
│  let (lo, hi) = stats(&[3, 1, 4, 1, 5]); // destructure   │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  SEMICOLONS ARE SILENT 🤐 — a line ending in ; gives       │
│  nothing back. Remove the semicolon and the line speaks.   │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Adding ; to the last expression in a function body.       │
│  Error: "expected R, found ()" — remove the semicolon.     │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 8 — Structs

> **Core idea:** Group related data into a named type. Add behaviour with `impl`.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 8: STRUCTS                                            │
│  "A blueprint for your own data type"                       │
├───────────────────────┬─────────────────────────────────────┤
│  struct Name { }      │  Define a struct                    │
│  impl Name { }        │  Add methods                        │
│  fn new() -> Self     │  Constructor convention             │
│  &self                │  Read-only method (borrows self)    │
│  &mut self            │  Mutating method                    │
│  Self                 │  Alias for the struct type          │
│  #[derive(Debug)]     │  Auto-generate {:?} printing        │
│  #[derive(Clone)]     │  Auto-generate .clone()             │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  #[derive(Debug, Clone)]                                    │
│  struct Player {                                            │
│      name: String,                                         │
│      score: u32,                                           │
│      active: bool,                                         │
│  }                                                          │
│                                                             │
│  impl Player {                                              │
│      fn new(name: &str) -> Self {                          │
│          Self { name: name.to_string(), score: 0,          │
│                 active: true }                              │
│      }                                                      │
│      fn add_score(&mut self, pts: u32) {                   │
│          self.score += pts;                                 │
│      }                                                      │
│      fn is_winning(&self, other: &Player) -> bool {        │
│          self.score > other.score                           │
│      }                                                      │
│  }                                                          │
│                                                             │
│  let mut p = Player::new("Ramyesh");                        │
│  p.add_score(100);                                          │
│  println!("{:?}", p);   // requires #[derive(Debug)]        │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  STRUCT = FORM 📋 — defines the fields.                     │
│  IMPL = INSTRUCTOR 🎓 — teaches the struct what to do.     │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Forgetting #[derive(Debug)] then being unable to print.   │
│  Forgetting `mut` on the instance when using &mut self.    │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 9 — Enums

> **Core idea:** A value that can be one of several variants — each variant can carry data.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 9: ENUMS                                              │
│  "A value that knows which kind it is"                      │
├───────────────────────┬─────────────────────────────────────┤
│  enum Name { }        │  Define an enum                     │
│  Variant              │  A possible state/value of the enum │
│  Variant(T)           │  Variant carrying data              │
│  Variant { x: T }     │  Variant with named fields          │
│  Option<T>            │  Built-in: Some(value) or None      │
│  Result<T, E>         │  Built-in: Ok(value) or Err(error)  │
│  if let Some(x) = opt │  Pattern match shorthand            │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  enum Status {                                              │
│      Loading,                   // no data                  │
│      Ready(String),             // carries a message       │
│      Error { code: u32, msg: String }, // named fields     │
│  }                                                          │
│                                                             │
│  fn describe(s: &Status) {                                  │
│      match s {                                              │
│          Status::Loading         => println!("Loading…"),  │
│          Status::Ready(msg)      => println!("OK: {}", msg)│
│          Status::Error { code, msg }                        │
│              => println!("Error {}: {}", code, msg),       │
│      }                                                      │
│  }                                                          │
│                                                             │
│  // Option — the safe replacement for null                  │
│  let name: Option<&str> = Some("Ferris");                   │
│  if let Some(n) = name {                                    │
│      println!("Hello, {}!", n);                             │
│  }                                                          │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  ENUM = TRAFFIC LIGHT 🚦 — it can only be ONE colour at a  │
│  time. Each colour (variant) can carry extra info.         │
│  match forces you to handle every light state.             │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Calling .unwrap() on Option/Result without checking.      │
│  Fix: use match, if let, .unwrap_or(), or the ? operator.  │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 10 — Error Handling

> **Core idea:** Functions that can fail return `Result`. You are always forced to deal with failure.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 10: ERROR HANDLING                                    │
│  "No exceptions. No surprises. Just Ok or Err."            │
├───────────────────────┬─────────────────────────────────────┤
│  Result<T, E>         │  Ok(value) or Err(error)            │
│  Option<T>            │  Some(value) or None                │
│  ?                    │  Propagate error upward if Err/None │
│  .unwrap()            │  Get value or PANIC — use carefully │
│  .expect("msg")       │  Like unwrap but with context       │
│  .unwrap_or(default)  │  Get value or fall back to default  │
│  .unwrap_or_else(fn)  │  Get value or run a closure         │
│  .is_ok() / .is_err() │  Check without consuming            │
│  .ok()                │  Convert Result<T,E> → Option<T>   │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  use std::num::ParseIntError;                               │
│                                                             │
│  fn parse_score(s: &str) -> Result<u32, ParseIntError> {   │
│      let n: u32 = s.trim().parse()?;  // ? propagates      │
│      Ok(n)                            // wrap in Ok        │
│  }                                                          │
│                                                             │
│  // Handling the result                                     │
│  match parse_score("42") {                                  │
│      Ok(n)  => println!("Score: {}", n),                   │
│      Err(e) => println!("Bad input: {}", e),               │
│  }                                                          │
│                                                             │
│  // Shorthand options                                       │
│  let s = parse_score("99").unwrap_or(0);   // 99           │
│  let s = parse_score("abc").unwrap_or(0);  // 0            │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  RESULT = A SEALED ENVELOPE 📬 — you don't know if it's    │
│  good news (Ok) or bad news (Err) until you open it.       │
│  Rust forces you to open every envelope before moving on.  │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Using ? in main() — it only works in functions returning  │
│  Result. Fix: use `fn main() -> Result<(), Box<dyn Error>>`│
└─────────────────────────────────────────────────────────────┘
```

---

## Card 11 — String Types

> **Core idea:** `&str` is a view. `String` is the real thing. Know when to use each.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 11: STRINGS                                           │
│  "&str borrows. String owns."                               │
├───────────────────────┬─────────────────────────────────────┤
│  &str                 │  Borrowed slice — usually a literal │
│  String               │  Owned heap string — can grow       │
│  String::from("x")    │  Create owned String from literal   │
│  "x".to_string()      │  Same — alternate syntax            │
│  s.push_str("more")   │  Append a &str to a String          │
│  s.push('!')          │  Append a single char               │
│  format!("{} {}", a,b)│  Build new String from parts        │
│  s.len()              │  Byte length (not char count)       │
│  s.contains("x")      │  Check substring presence           │
│  s.starts_with("x")   │  Check prefix                       │
│  s.trim()             │  Remove leading/trailing whitespace │
│  s.replace("a","b")   │  Replace all occurrences            │
│  s.to_lowercase()     │  Convert case                       │
│  s.split(' ')         │  Iterator over substrings           │
│  &s[0..3]             │  Slice bytes 0–2 (careful: UTF-8!) │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  let greeting: &str = "Hello";     // literal, borrowed    │
│  let mut s = String::from("World"); // owned               │
│  s.push_str("!!!");                 // mutate              │
│                                                             │
│  let full = format!("{}, {}!", greeting, s); // "Hello, World!!!!"
│                                                             │
│  // Iterating characters safely                             │
│  for ch in full.chars() {                                   │
│      print!("{} ", ch);                                     │
│  }                                                          │
│                                                             │
│  // Common conversions                                      │
│  let n: i32 = "42".parse().unwrap();    // &str → i32      │
│  let s: String = 42.to_string();        // i32 → String    │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  &str = PHOTOGRAPH 📷 — a snapshot of a string, read-only. │
│  String = WHITEBOARD 🖊️ — you own it, you can erase/add.  │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Indexing a String with s[0] — Rust forbids it (UTF-8).   │
│  Fix: s.chars().nth(0) or s.as_bytes()[0] for ASCII.       │
└─────────────────────────────────────────────────────────────┘
```

---

## Card 12 — Collections (Vec & HashMap)

> **Core idea:** Vec is a growable list. HashMap is a key-value store. Both own their data.

```
┌─────────────────────────────────────────────────────────────┐
│  CARD 12: COLLECTIONS                                       │
│  "Vec = ordered list. HashMap = labeled drawer."            │
├───────────────────────┬─────────────────────────────────────┤
│  Vec<T>               │  Growable array of T                │
│  vec![1,2,3]          │  Literal shorthand                  │
│  v.push(x)            │  Append to end                      │
│  v.pop()              │  Remove from end → Option<T>        │
│  v.len()              │  Number of elements                 │
│  v[i]                 │  Access (panics if out of bounds)   │
│  v.get(i)             │  Safe access → Option<&T>           │
│  v.iter()             │  Iterate references                 │
│  v.contains(&x)       │  Check if value exists              │
│  v.sort()             │  Sort in place (needs mut)          │
│  v.dedup()            │  Remove consecutive duplicates      │
│  HashMap<K, V>        │  Key-value storage                  │
│  map.insert(k, v)     │  Add/overwrite entry                │
│  map.get(&k)          │  Lookup → Option<&V>                │
│  map.contains_key(&k) │  Check key existence                │
│  map.entry(k).or_insert│  Insert if not present             │
├───────────────────────┴─────────────────────────────────────┤
│  CODE SNAPSHOT                                              │
│                                                             │
│  // Vec                                                     │
│  let mut scores: Vec<i32> = vec![10, 20, 30];              │
│  scores.push(40);                                           │
│  println!("{}", scores[0]);         // 10                   │
│  println!("{:?}", scores);          // [10, 20, 30, 40]    │
│                                                             │
│  // HashMap                                                 │
│  use std::collections::HashMap;                             │
│  let mut map: HashMap<&str, u32> = HashMap::new();         │
│  map.insert("Alice", 95);                                   │
│  map.insert("Bob", 87);                                     │
│  if let Some(s) = map.get("Alice") {                       │
│      println!("Alice scored {}", s);                        │
│  }                                                          │
├─────────────────────────────────────────────────────────────┤
│  🧠 MEMORY HOOK                                             │
│  Vec = NUMBERED LOCKERS 🔢 — access by position.           │
│  HashMap = NAMED DRAWERS 🗂️ — access by label/name.        │
│                                                             │
│  ⚠️  COMMON MISTAKE                                         │
│  Accessing v[i] when i might be out of range → panic.      │
│  Fix: use v.get(i) which returns Option — handle safely.   │
└─────────────────────────────────────────────────────────────┘
```

---

## The Grand Summary Card — Rust in One Page

> Tear this out. Pin it up. Review every morning.

```
╔═════════════════════════════════════════════════════════════╗
║           RUST CORE CONCEPTS — MASTER SUMMARY              ║
╠══════════════════╦══════════════════════════════════════════╣
║  OWNERSHIP       ║  One owner. Owner gone → value gone.    ║
║                  ║  Move transfers ownership.              ║
║                  ║  Clone copies. Primitives auto-copy.    ║
╠══════════════════╬══════════════════════════════════════════╣
║  BORROWING       ║  &T = many readers. &mut T = one writer ║
║                  ║  Never mix &T and &mut T at same time.  ║
╠══════════════════╬══════════════════════════════════════════╣
║  LIFETIMES       ║  Reference can't outlive its data.      ║
║                  ║  Usually inferred. 'a when ambiguous.   ║
╠══════════════════╬══════════════════════════════════════════╣
║  TYPES           ║  i32 (int), f64 (float), bool, char,   ║
║                  ║  &str (view), String (owned),           ║
║                  ║  Vec<T> (list), HashMap<K,V> (map)     ║
╠══════════════════╬══════════════════════════════════════════╣
║  CONTROL FLOW    ║  if/else/match return values.           ║
║                  ║  match must be exhaustive.              ║
║                  ║  loop returns a value via break.        ║
╠══════════════════╬══════════════════════════════════════════╣
║  FUNCTIONS       ║  Last expression without ; = return.   ║
║                  ║  return expr; for early exit.           ║
╠══════════════════╬══════════════════════════════════════════╣
║  STRUCTS         ║  struct = data. impl = behaviour.       ║
║                  ║  #[derive(Debug,Clone)] for free tools. ║
╠══════════════════╬══════════════════════════════════════════╣
║  ENUMS           ║  Variants can carry data.               ║
║                  ║  Option<T> = Some/None. No null.        ║
║                  ║  Result<T,E> = Ok/Err. No exceptions.  ║
╠══════════════════╬══════════════════════════════════════════╣
║  ERROR HANDLING  ║  ? propagates errors up.                ║
║                  ║  .unwrap_or(default) for safe fallback. ║
╠══════════════════╬══════════════════════════════════════════╣
║  MEMORY HOOKS    ║  Ice cube (mut) · Hot potato (ownership)║
║                  ║  Reading room (borrow) · Rental (lifetime)
║                  ║  Vending machine (match) · Envelope (Result)
╠══════════════════╬══════════════════════════════════════════╣
║  TOP MISTAKES    ║  Using after move → use & instead       ║
║                  ║  Forgot mut → add mut to let            ║
║                  ║  ; on return line → remove it           ║
║                  ║  Non-exhaustive match → add _           ║
║                  ║  unwrap on None/Err → use match or ?    ║
╚══════════════════╩══════════════════════════════════════════╝
```

---

## Self-Quiz — Cover the Right, Recall the Left

Test yourself without peeking:

| Term | Meaning (cover this → recall) |
|---|---|
| `let mut` | Mutable variable — can be changed |
| `&T` | Immutable reference — borrow without ownership |
| `&mut T` | Mutable reference — borrow and modify |
| `move` | Transfer ownership — original can no longer be used |
| `.clone()` | Explicit deep copy — both copies exist independently |
| `match` | Exhaustive pattern matching — every case must be handled |
| `_` | Wildcard — catch all remaining patterns |
| `Option<T>` | `Some(value)` or `None` — safe replacement for null |
| `Result<T,E>` | `Ok(value)` or `Err(error)` — explicit error handling |
| `?` | Propagate error or None upward — early return on failure |
| `#[derive(Debug)]` | Auto-generate `{:?}` printing for structs/enums |
| `impl` | Block where you add methods to a struct or enum |
| `'a` | Lifetime annotation — describes how long a reference lives |
| `Vec<T>` | Owned growable list |
| `HashMap<K,V>` | Owned key-value map |
| `String` | Owned heap string — can be modified |
| `&str` | Borrowed string slice — read-only view |
| `fn f() -> T` | Function returning an owned value of type T |
| `{ expr }` | Block expression — evaluates to `expr` |
| `drop(x)` | Explicitly free `x` before end of scope |

---

## Spaced Repetition Schedule

> The science: reviewing at increasing intervals locks memory permanently.

```
Day 1   → Read all 12 cards in full
Day 2   → Self-quiz (cover right column)
Day 4   → Review cards where you hesitated
Day 7   → Self-quiz all 12 again
Day 14  → Quick scan — focus on weak spots
Day 30  → One final pass
After 30 days → You won't need the cards anymore
```

---

*Next: [Mini-Projects — Build Real Things](05_mini_projects.md)*
*Previous: [Playground Examples](03_playground_examples.md)*
