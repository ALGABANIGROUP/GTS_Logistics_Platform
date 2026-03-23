import os, re

ROOT = "."
SKIP_DIRS = {".venv", "__pycache__", ".git", "node_modules", "dist", "build"}

block_open_re = re.compile(r"^(?P<ind>[ \t]*)(?P<kw>try|if|for|while|with|def|class|elif|else|except|finally)\b.*:\s*(#.*)?$")

def leading_ws(s: str) -> str:
    return re.match(r"^[ \t]*", s).group(0)

def indent_len(ws: str) -> int:
    # treat tab as 4 spaces
    return sum(4 if ch == "\t" else 1 for ch in ws)

def make_indent(n: int) -> str:
    return " " * n

def is_blank_or_comment(line: str) -> bool:
    stripped = line.strip()
    return stripped == "" or stripped.startswith("#")

def fix_file(path: str) -> bool:
    try:
        lines = open(path, "r", encoding="utf-8").read().splitlines(True)
    except Exception:
        return False

    changed = False
    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        m = block_open_re.match(line)
        if not m:
            out.append(line)
            i += 1
            continue

        ind_ws = m.group("ind")
        kw = m.group("kw")
        base = indent_len(ind_ws)
        out.append(line)
        i += 1

        # find next significant line
        j = i
        while j < n and is_blank_or_comment(lines[j]):
            out.append(lines[j])
            j += 1

        if j >= n:
            # file ended after block opener -> add pass
            out.append(make_indent(base + 4) + "pass\n")
            changed = True
            i = j
            continue

        next_line = lines[j]
        next_ws = leading_ws(next_line)
        next_ind = indent_len(next_ws)

        expected = base + 4

        # 1) Fix unindented import/from right after try/if/except/else/elif/finally/with/for/while/def/class
        # If the next statement is not indented enough, indent it.
        if next_ind < expected:
            stripped = next_line.lstrip("\t ").rstrip("\n")
            # if it's a dedent immediately after def/class => empty body, insert pass instead of indenting next block
            if kw in ("def", "class") and next_ind <= base:
                out.append(make_indent(expected) + "pass\n")
                changed = True
                # do NOT consume next_line here; let outer loop process it normally
                i = j
                continue

            # otherwise, indent the line into the block
            out.append(make_indent(expected) + stripped + ("\n" if next_line.endswith("\n") else ""))
            changed = True
            i = j + 1
            continue

        # default: keep as-is
        i = j

    new_txt = "".join(out)
    old_txt = "".join(lines)
    if new_txt != old_txt:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new_txt)
        return True
    return changed

def main():
    changed_files = 0
    scanned = 0
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            scanned += 1
            if fix_file(path):
                changed_files += 1

    print(f"Scanned: {scanned} .py files")
    print(f"Fixed:   {changed_files} files")

if __name__ == "__main__":
    main()
