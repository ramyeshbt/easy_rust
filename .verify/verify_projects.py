#!/usr/bin/env python3
"""Assemble each mini-project's BUILD steps into one complete program and compile it.
This removes the per-block isolation noise (Step 2 needs Step 1's types)."""
import os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "05_mini_projects.md")
RUSTC = os.path.expanduser(r"~\.cargo\bin\rustc.exe")
WORK = os.path.join(ROOT, ".verify", "proj")
os.makedirs(WORK, exist_ok=True)

with open(SRC, encoding="utf-8") as f:
    text = f.read()
lines = text.splitlines()

def find_main(code):
    """Return (start_idx, end_idx) of `fn main() { ... }` in code, or None."""
    m = re.search(r"\bfn\s+main\s*\(\s*\)", code)
    if not m:
        return None
    # find the opening brace after the signature
    i = code.index("{", m.end())
    depth = 0
    for j in range(i, len(code)):
        if code[j] == "{":
            depth += 1
        elif code[j] == "}":
            depth -= 1
            if depth == 0:
                return (m.start(), j + 1)
    return None

def strip_main(code):
    span = find_main(code)
    if not span:
        return code, None
    main_code = code[span[0]:span[1]]
    rest = (code[:span[0]] + code[span[1]:]).strip()
    return rest, main_code

# Split into projects by "# Project" headers
proj_spans = [(m.start(), m.group(1)) for m in re.finditer(r"^# Project (\d+)", text, re.M)]
proj_spans.append((len(text), None))

def blocks_between(segment):
    """rust code blocks that appear under '## 🔨 Build' before '## 🔍 Deep Dive'."""
    # restrict to the Build region
    bstart = segment.find("## 🔨 Build")
    dstart = segment.find("## 🔍 Deep Dive")
    if bstart == -1:
        return []
    region = segment[bstart: dstart if dstart != -1 else len(segment)]
    return re.findall(r"```rust\n(.*?)```", region, re.S)

results = []
for k in range(len(proj_spans) - 1):
    start, num = proj_spans[k]
    end = proj_spans[k + 1][0]
    segment = text[start:end]
    blks = blocks_between(segment)
    if not blks:
        continue
    items = []
    seen_use = set()
    last_main = None
    for b in blks:
        rest, main_code = strip_main(b)
        if main_code:
            last_main = main_code  # keep the final step's main
        for ln in rest.splitlines():
            if ln.strip().startswith("use ") and ln.strip() in seen_use:
                continue
            if ln.strip().startswith("use "):
                seen_use.add(ln.strip())
            items.append(ln)
    program = "\n".join(items) + "\n\n" + (last_main or "fn main() {}") + "\n"
    src = os.path.join(WORK, f"project{num}.rs")
    with open(src, "w", encoding="utf-8") as f:
        f.write(program)
    out = os.path.join(WORK, f"project{num}.meta")
    cmd = [RUSTC, "--edition", "2021", "--emit=metadata", "-o", out, src]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    errs = [l for l in p.stderr.splitlines() if l.startswith("error")]
    warns = [l for l in p.stderr.splitlines() if l.startswith("warning:")]
    results.append((num, p.returncode, errs, warns, src))

print("=== FULL MINI-PROJECT COMPILE (assembled build steps) ===\n")
for num, rc, errs, warns, src in results:
    status = "✅ COMPILES" if rc == 0 else "❌ ERRORS"
    print(f"Project {num}: {status}  ({len(warns)} warning(s))")
    for e in errs[:8]:
        print("    " + e)
    if rc != 0:
        print(f"    (assembled source: {src})")
    print()
