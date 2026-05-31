# 🦀 Easy Rust — Learn Rust by Analogy

> A beginner-friendly Rust course that makes ownership, borrowing, and lifetimes *click* — using everyday analogies, runnable examples, and a peek beneath the language at how memory and the OS really work.

[![Verify course examples](https://github.com/ramyeshbt/easy_rust/actions/workflows/verify.yml/badge.svg)](https://github.com/ramyeshbt/easy_rust/actions/workflows/verify.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Rust Edition](https://img.shields.io/badge/Rust-2021-orange.svg)](https://doc.rust-lang.org/edition-guide/)
[![Runs in Playground](https://img.shields.io/badge/Try%20it-Rust%20Playground-brightgreen.svg)](https://play.rust-lang.org)

---

## What is this?

Rust has a reputation for being hard. It isn't — it just asks you to think about things other languages hide. **Easy Rust** is a self-contained course that teaches the language the way it actually clicks for people: through analogies you already understand.

- **Ownership** → a library book (one borrower at a time)
- **Borrowing** → lending your car (access without giving up ownership)
- **Lifetimes** → a loan period (the borrowed thing must be returned before the lender disappears)

Every concept comes with **runnable code**, **"break it on purpose" examples** with the exact compiler errors explained, **memorization cheat cards**, and **hands-on projects**. Where it matters, we go one level deeper and show what your code is doing in **memory, the stack/heap, and even the OS kernel** — so you build genuine intuition, not just syntax recall.

## Who is it for?

- Developers new to Rust (some programming experience helps, but no C/C++ required)
- People who bounced off Rust before and want the *why* behind the borrow checker
- Anyone who learns best by **doing** — every example runs in the browser, no install needed

## You don't need to install anything

Every example runs in the **[Rust Playground](https://play.rust-lang.org)** — paste, hit Run, experiment. When you're ready to build locally, the course shows you how with Cargo.

---

## 📚 Course Contents

Work through these in order. Each builds on the last.

| # | Chapter | What you'll learn |
|---|---------|-------------------|
| 1 | [**Why Rust? The Hook**](content/01_hook.md) | What makes Rust special, who uses it, a first taste of code, and honest expectations |
| 2 | [**Foundations — Ownership, Borrowing & Lifetimes**](content/02_foundations_analogy.md) | The heart of Rust, via analogy — with stack/heap diagrams and a C-vs-Rust bug comparison |
| 3 | [**Playground Examples**](content/03_playground_examples.md) | 9 hands-on sections: variables, types, control flow, functions, structs, enums, error handling |
| 4 | [**Cheat Cards**](content/04_cheat_cards.md) | 12 one-page visual summaries + a self-quiz and spaced-repetition schedule |
| 5 | [**Mini-Projects**](content/05_mini_projects.md) | 5 themed builds (name card, calculator, grade tracker, memory explorer, todo app) with system-level deep dives |

## How to use this course

1. **Read** a chapter top to bottom.
2. **Run** every code block in the [Playground](https://play.rust-lang.org).
3. **Break things on purpose** — the course shows wrong code and the exact errors. Reproduce them. Reading compiler errors *is* the skill.
4. **Do the "Try Yourself" activities** at the end of each section.
5. **Review the cheat cards** before sleep; the spaced-repetition schedule in Chapter 4 locks it in.

> 💡 The best way to learn Rust is to make the compiler angry, read what it says, and fix it. Every error is a free lesson.

---

## ✅ Verified examples

The code in this course isn't just written — it's **compiler-checked**. A small harness in [`.verify/`](.verify/README.md) extracts every Rust snippet and runs it through `rustc`'s type and borrow checker, and confirms that the errors the course *claims* (E0382, E0502, E0597, E0106, …) are exactly the errors `rustc` actually produces. All five mini-projects compile cleanly.

See [`.verify/README.md`](.verify/README.md) to run it yourself.

---

## 🗺️ After this course

Once the foundations click, these are the natural next steps:

- [The Rust Book](https://doc.rust-lang.org/book/) — the official, complete guide
- [Rustlings](https://github.com/rust-lang/rustlings) — small compile-to-learn exercises
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/) — runnable examples for nearly every feature

Topics to explore next: **traits, generics, closures & iterators, modules & crates, and fearless concurrency.**

## 🤝 Contributing

Found a typo, an unclear explanation, or an example that doesn't compile on current stable Rust? Contributions are welcome:

1. Open an issue describing the problem, or
2. Submit a pull request. If you change any code samples, please run the verification harness (`python .verify/verify.py`) first.

Suggestions for new analogies, exercises, or projects are especially appreciated — clarity for beginners is the whole point.

## 📄 License

Released under the [MIT License](LICENSE). You're free to use, adapt, and share — including for teaching — with attribution.

---

*Made with curiosity, for anyone who was ever told Rust is "too hard." It isn't. 🦀*
