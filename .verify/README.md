# Verification Harness

These scripts compiler-check every Rust example in the course, so the code (and the compiler errors the course claims) stay accurate.

## Why `--emit=metadata`?

The scripts compile with:

```
rustc --edition 2021 --emit=metadata ...
```

`--emit=metadata` runs the **full type checker and borrow checker** — which is what produces every `E0xxx` error — but stops **before code generation and linking**. That means:

- It catches ownership/borrow/lifetime errors (E0382, E0502, E0597, E0106, …) exactly as a normal build would.
- It needs **no linker**, so it works on machines without MSVC Build Tools or MinGW (relevant on Windows, where an MSYS `link.exe` can otherwise shadow the MSVC linker).

## Scripts

### `verify.py`
Extracts every fenced ` ```rust ` block from `content/*.md` and compiles each one in isolation.

- Complete programs (with `fn main`) compile as a binary crate.
- Free items (`fn`, `struct`, `enum`, `impl`, …) compile as a library crate.
- Bare statements are wrapped in a `fn main { … }`.

It then reports:
- which blocks compile vs. error,
- the **actual** error codes `rustc` emits,
- the error codes the course **claims** (scraped from the prose),
- a claimed-vs-actual reconciliation.

> Note: many blocks in the mini-projects are deliberate *fragments* (Step 2 uses a type defined in Step 1) or illustrative snippets using `...` shorthand. Those "fail" in isolation by design — that's what `verify_projects.py` is for.

### `verify_projects.py`
Assembles each mini-project's **build steps** into one complete program (collecting the item definitions from every step and keeping the final `main`), then compiles the whole thing. This confirms the projects actually build end-to-end.

## Running

From the project root:

```bash
# Windows PowerShell (rustc installed via rustup under ~/.cargo/bin)
$env:PYTHONIOENCODING="utf-8"     # so the report's emoji print on cp1252 consoles
python .verify/verify.py
python .verify/verify_projects.py
```

Requirements:
- Python 3.8+
- A Rust toolchain (`rustc`). The scripts look for `~/.cargo/bin/rustc.exe`; adjust the `RUSTC` path at the top of each script if yours lives elsewhere or is already on `PATH`.

## Expected result

- All five mini-projects compile (warnings are intentional teaching artifacts — e.g., the drop-order demo's deliberately-unused variables).
- Every error code the course names is confirmed present.
- The integer-overflow and array-out-of-bounds examples compile cleanly — the course correctly describes those as **runtime** panics, not compile errors.

## Scratch output

Both scripts write temporary `.rs`/`.meta` files under `.verify/blocks/` and `.verify/proj/`, and `verify.py` writes `report.json`. These are git-ignored. Delete them anytime:

```bash
rm -rf .verify/blocks .verify/proj .verify/report.json
```
