#!/usr/bin/env python3
"""Extract ```rust blocks from the course, compile each with rustc --emit=metadata
(type+borrow check, no linker), and report actual vs course-claimed outcomes."""
import os, re, subprocess, sys, tempfile, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "content")
RUSTC = os.path.expanduser(r"~\.cargo\bin\rustc.exe")
WORK = os.path.join(ROOT, ".verify", "blocks")
os.makedirs(WORK, exist_ok=True)

FENCE = re.compile(r"^```(\w+)?\s*$")

def extract_blocks(path):
    """Yield (lang, start_line, code, following_text) for each fenced block."""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    blocks = []
    i = 0
    while i < len(lines):
        m = FENCE.match(lines[i].rstrip("\n"))
        if m:
            lang = (m.group(1) or "").lower()
            start = i + 1
            body = []
            i += 1
            while i < len(lines) and not FENCE.match(lines[i].rstrip("\n")):
                body.append(lines[i])
                i += 1
            # capture up to 12 lines after the closing fence (to find claimed errors)
            after = "".join(lines[i+1:i+13]) if i+1 < len(lines) else ""
            blocks.append((lang, start, "".join(body), after))
        i += 1
    return blocks

ERRCODE = re.compile(r"error\[(E\d{4})\]")
ACTIVE_ERR_MARKER = re.compile(r"^(?!\s*//).*//.*(❌|ERROR|won't compile|will NOT compile|does not compile)")

def classify(code):
    has_main = re.search(r"\bfn\s+main\s*\(", code) is not None
    has_fn = re.search(r"^\s*(pub\s+)?fn\s+\w+", code, re.M) is not None
    has_item = re.search(r"^\s*(struct|enum|impl|trait|use|const|static|mod)\b", code, re.M) is not None
    return has_main, has_fn, has_item

def wrap(code):
    has_main, has_fn, has_item = classify(code)
    if has_main:
        return code, "bin"
    if has_fn or has_item:
        return code, "lib"          # free items, no main needed
    # bare statements -> wrap in main
    return "fn main() {\n" + code + "\n}\n", "bin"

def claimed_codes(code, after):
    codes = set(ERRCODE.findall(code)) | set(ERRCODE.findall(after))
    return sorted(codes)

def expected_to_fail(code):
    # active (non-commented) line carrying a failure marker
    for ln in code.splitlines():
        if ACTIVE_ERR_MARKER.match(ln):
            return True
    return False

def compile_block(code, crate_type):
    src = os.path.join(WORK, "snippet.rs")
    with open(src, "w", encoding="utf-8") as f:
        f.write(code)
    out = os.path.join(WORK, "out.meta")
    cmd = [RUSTC, "--edition", "2021", "--emit=metadata",
           "--crate-type", crate_type, "-o", out, src]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stderr

def main():
    results = []
    for fname in sorted(os.listdir(CONTENT)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(CONTENT, fname)
        for lang, line, code, after in extract_blocks(path):
            if lang != "rust":
                continue
            wrapped, crate_type = wrap(code)
            rc, stderr = compile_block(wrapped, crate_type)
            actual_codes = sorted(set(ERRCODE.findall(stderr)))
            claims = claimed_codes(code, after)
            exp_fail = expected_to_fail(code)
            results.append({
                "file": fname, "line": line, "crate": crate_type,
                "compiles": rc == 0,
                "actual_codes": actual_codes,
                "claimed_codes": claims,
                "exp_fail_marker": exp_fail,
                "stderr_head": "\n".join(
                    [l for l in stderr.splitlines() if l.startswith("error")][:3]),
            })
    with open(os.path.join(ROOT, ".verify", "report.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # ---- print summary ----
    total = len(results)
    compiled = sum(1 for r in results if r["compiles"])
    print(f"Total rust blocks: {total} | compiled OK: {compiled} | errored: {total-compiled}\n")

    print("=== BLOCKS THAT FAILED TO COMPILE ===")
    for r in results:
        if not r["compiles"]:
            tag = "expected-fail" if (r["exp_fail_marker"] or r["claimed_codes"]) else "UNEXPECTED?"
            print(f"[{tag}] {r['file']}:{r['line']}  actual={r['actual_codes']} claimed={r['claimed_codes']}")
            if r["stderr_head"]:
                for l in r["stderr_head"].splitlines():
                    print("        " + l)
    print()
    print("=== BLOCKS MARKED 'should fail' BUT COMPILED CLEAN (possible doc mismatch) ===")
    for r in results:
        if r["compiles"] and (r["exp_fail_marker"] or r["claimed_codes"]):
            print(f"  {r['file']}:{r['line']}  claimed={r['claimed_codes']} exp_marker={r['exp_fail_marker']}")
    print()
    print("=== CLAIMED-vs-ACTUAL ERROR CODE CHECK ===")
    for r in results:
        if r["claimed_codes"]:
            ok = set(r["claimed_codes"]).issubset(set(r["actual_codes"]))
            status = "MATCH" if ok else "MISMATCH"
            print(f"  [{status}] {r['file']}:{r['line']}  claimed={r['claimed_codes']} actual={r['actual_codes']}")

if __name__ == "__main__":
    main()
