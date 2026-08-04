#!/usr/bin/env python3
"""A linter for the lecture sources.

Every check here exists because the mistake it catches reached a built
page at least once. The lectures go through two different renderers -
kramdown for the website, pandoc for the book - and a construction that
is fine for one can be silently wrong for the other. Silently is the
problem: a bare pipe inside inline maths does not fail the build, it
turns the paragraph into a table, and nobody notices until a reader
does.

Run it over everything with `make check`, or a file at a time:

    python3 py/lint_lectures.py lectures/l06_adc.md
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


@dataclass
class Finding:
    rule: str
    line: int
    message: str


# A pan_doc/pan_skip/pan_latex block, and inline maths.
_BLOCK = re.compile(r"<!--\s*pan_(doc|skip|latex|title|author)\s*:")
_INLINE_MATH = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)")
_DISPLAY = re.compile(r"\$\$")


def _mask_skipped(lines: list[str]) -> list[bool]:
    """Which lines are slide-only.

    A `<!--pan_skip: -->` marker means everything up to the next slide
    break is deck material: it never reaches the website or the book, so
    a bare `##` used as a slide header there is not an artifact.
    """
    inside, out = False, []
    for line in lines:
        if re.match(r"<!--\s*pan_skip", line):
            inside = True
        elif line.strip() == "---":
            inside = False
        out.append(inside)
    return out


def _mask_code(lines: list[str]) -> list[bool]:
    """Which lines are inside a fenced code block, where none of the
    prose rules apply."""
    inside, out = False, []
    for line in lines:
        if line.lstrip().startswith("```"):
            inside = not inside
            out.append(True)
            continue
        out.append(inside)
    return out


def check_math(lines: list[str], code: list[bool]) -> list[Finding]:
    """The two ways maths breaks a renderer without failing a build.

    Matched over the whole file rather than line by line, because inline
    maths is allowed to wrap: `$p_n =` on one line and `\\frac{a}{b}$` on
    the next is one span, and pairing per line would call both halves
    broken.
    """
    out = []
    text = "\n".join(
        "" if masked else line for line, masked in zip(lines, code))
    # An escaped \$ is a dollar sign, and a $ inside `code` is a shell
    # variable. Neither opens maths.
    text = re.sub(r"\\\$", "\x00", text)
    text = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), text)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line) + 1)

    def line_of(offset: int) -> int:
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if starts[mid] <= offset:
                lo = mid + 1
            else:
                hi = mid
        return lo

    text = _DISPLAY.sub(lambda m: "\x01\x01", text)
    for m in re.finditer(r"(?<!\x01)\$([^$\n]*(?:\n[^$\n]*)?)\$(?!\x01)", text):
        body, i = m.group(1), line_of(m.start())
        if "|" in body:
            out.append(Finding(
                "math-pipe", i,
                "a bare | inside $...$ makes kramdown parse the whole "
                "paragraph as a table; write \\vert or \\parallel"))
        if body[:1] in (" ", "\t") or body[-1:] in (" ", "\t"):
            out.append(Finding(
                "math-space", i,
                "pandoc only reads $...$ as maths when there is no space "
                "just inside the delimiters, so the book build fails on "
                "this one"))
    return out


def check_comments(lines: list[str]) -> list[Finding]:
    """A --> with nothing open renders as literal text on the page, and
    a block that never closes swallows the rest of the chapter."""
    out, open_at = [], None
    for i, line in enumerate(lines, start=1):
        for m in re.finditer(r"<!--|-->", line):
            if m.group(0) == "<!--":
                open_at = open_at or i
            elif open_at is None:
                out.append(Finding(
                    "orphan-comment-close", i,
                    "a --> with no comment open: it renders as literal text"))
            else:
                open_at = None
    if open_at:
        out.append(Finding("unclosed-comment", open_at,
                           "this comment block is never closed"))
    return out


def check_headings(lines: list[str], code: list[bool]) -> list[Finding]:
    """Heading levels that skip, and the stray # left by an edit."""
    out, previous = [], 0
    for i, line in enumerate(lines, start=1):
        if code[i - 1]:
            continue
        m = re.match(r"^(#{1,6})\s+\S", line)
        if not m:
            if re.match(r"^#{1,6}\s*$", line) or re.match(r"^#{1,6}-", line):
                out.append(Finding(
                    "heading-artifact", i,
                    f"a bare {line.strip()[:12]!r} - the remains of an edit, "
                    f"not a heading"))
            continue
        level = len(m.group(1))
        if previous and level > previous + 1:
            out.append(Finding(
                "heading-skip", i,
                f"jumps from level {previous} to {level}, so the chapter's "
                f"structure is missing a rung"))
        previous = level
    return out


def check_citations(lines: list[str], code: list[bool]) -> list[Finding]:
    """Citation and footnote forms the pipeline does not support."""
    out = []
    defined = {m.group(1) for line in lines
               for m in [re.match(r"^\[\^([^\]]+)\]:", line)] if m}
    for i, line in enumerate(lines, start=1):
        if code[i - 1]:
            continue
        for m in re.finditer(r"\[@[^\]]*;[^\]]*\]", line):
            out.append(Finding(
                "multi-key-citation", i,
                f"{m.group(0)[:30]}: split into one [@key] per work, the "
                f"pipeline does not handle a semicolon list"))
        for m in re.finditer(r"\[\^([^\]]+)\](?!:)", line):
            if m.group(1) not in defined:
                out.append(Finding(
                    "orphan-footnote", i,
                    f"footnote [^{m.group(1)}] is used but never defined"))
    return out


def check_figures(path: Path, lines: list[str], code: list[bool]) -> list[Finding]:
    """Images that do not exist, and figure numbers that do not match the
    order the figures appear in."""
    out, seen = [], 0
    for i, line in enumerate(lines, start=1):
        if code[i - 1]:
            continue
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", line):
            src = m.group(1)
            if src.startswith("http"):
                continue
            target = (path.parent / src).resolve()
            if not target.exists():
                #- Generated figures are not committed; a media/<name>_tikz.*
                #  reference is fine as long as its tikz source exists (the
                #  same rule py/check.py applies).
                tm = re.match(r"(?:\.\./)?media/(.+)_tikz\.(?:pdf|svg)$", src)
                if tm and (REPO / "tikz" / f"{tm.group(1)}.tex").exists():
                    continue
                out.append(Finding(
                    "missing-image", i, f"{src} does not exist"))
        m = re.search(r"<sub>Figure\s+(\d+):", line)
        if m:
            seen += 1
            if int(m.group(1)) != seen:
                out.append(Finding(
                    "figure-numbering", i,
                    f"captioned Figure {m.group(1)} but it is the "
                    f"{seen}{'st' if seen % 10 == 1 else 'th'} figure in the "
                    f"chapter"))
    return out


def check_prose(lines: list[str], code: list[bool]) -> list[Finding]:
    """Small things that survive proofreading because the eye skips
    them."""
    out = []
    for i, line in enumerate(lines, start=1):
        if code[i - 1] or line.lstrip().startswith("|"):
            continue
        for m in re.finditer(r"\b([A-Za-z]{3,})\s+\1\b", line):
            if m.group(1).lower() not in ("that", "had", "very"):
                out.append(Finding(
                    "doubled-word", i, f"'{m.group(1)} {m.group(1)}'"))
        if re.search(r"\bWant to (learn|know) more\b", line):
            out.append(Finding(
                "reading-list-heading", i,
                "the reading list heading is 'Would you like to know more?'"))
    return out


RULES_HELP = {
    "math-pipe": "kramdown turns the paragraph into a table",
    "math-space": "pandoc drops the maths and the book build fails",
}


def _excluded() -> set[str]:
    """The chapters `make check` already knows are not built - scratch
    decks and guest lectures whose slides live elsewhere. Their images
    are allowed to be missing."""
    try:
        source = (REPO / "py" / "check.py").read_text()
    except OSError:
        return set()
    block = re.search(r"EXCLUDED\s*=\s*\{(.*?)\}", source, re.S)
    if not block:
        return set()
    return set(re.findall(r'"([^"]+)"', block.group(1)))


def lint(path: Path) -> list[Finding]:
    lines = path.read_text().splitlines()
    code = _mask_code(lines)
    # Slide-only material is masked for the checks about how the page
    # reads, but not for the ones about whether a file exists or a
    # figure is numbered right: those hold everywhere.
    deck = [a or b for a, b in zip(code, _mask_skipped(lines))]
    return (check_math(lines, code)
            + check_comments(lines)
            + check_headings(lines, deck)
            + check_citations(lines, code)
            + check_figures(path, lines, code)
            + check_prose(lines, deck))


def main(argv: list[str]) -> int:
    paths = [Path(a) for a in argv[1:]]
    if not paths:
        # s_ decks are scratch: not in the book, not built, not linted.
        excluded = _excluded()
        paths = [p for p in sorted((REPO / "lectures").glob("*.md"))
                 if p.stem not in excluded]
    total = 0
    for path in paths:
        findings = sorted(lint(path), key=lambda f: f.line)
        if not findings:
            continue
        print(path)
        for f in findings:
            print(f"  {f.line}: [{f.rule}] {f.message}")
        total += len(findings)
    if total:
        print(f"\n{total} finding{'s' if total != 1 else ''}")
        return 1
    print("lectures: no findings")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
