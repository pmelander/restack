#!/usr/bin/env python3
"""The impact matrix's arithmetic: margins, reading aids, iteration comparison, residual claims.

The architect scores the matrix; this script never does. It does the parts a
person or a model gets wrong by hand over a 150-row matrix: the row and column
totals, the comparison between iterations against the right stressor set, and
whether every cell a residual claims to clear was a 1 to begin with (ADR-025).

    python matrix.py totals MATRIX [--write]
        margins checked (or filled with --write), unknown cells, reading aids
    python matrix.py compare BEFORE AFTER
        per-actor before/after, cells cleared and added, both totals
    python matrix.py claims RESIDUALS BEFORE [--after AFTER]
        each residual's claimed cells checked against the matrix

Reads any layout the toolkit has produced: `| Stressor | Lens | A | B | Σ |`,
`| # | Stressor | A | B | TOTAL |`, dots or zeros for empty cells. A cell is
0, 1, `1?` or `?` (unknown, which counts as 1: unknown exposure is exposure).
Anything above 1 is reported, never summed silently: scoring is binary.

Standard library only, no network. Exit status: 0 nothing to report,
1 something to look at, 2 usage error.
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

LABEL_HEADERS = {"#", "id", "stressor", "lens", "class", "category", "type", "description",
                 "source", "tags", "notes", "stressor description", "tag"}
TOTAL_HEADER = re.compile(r"^(σ|sum|total|impact|= ?)$", re.IGNORECASE)
MARGIN_ROW = re.compile(r"^(total|σ|vulnerab|actor vulnerab)", re.IGNORECASE)
STRESSOR_ID = re.compile(r"\bS-\d+[a-z]?\b")


class UsageError(Exception):
    pass


def strip_md(text: str) -> str:
    return re.sub(r"\*+|`|(?<!\w)_+|_+(?!\w)", "", text).strip()


def split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|")]


def score(cell: str) -> tuple[int, bool] | None:
    """(value, unknown) for a matrix cell, or None if it is not a score."""
    text = strip_md(cell)
    if text in ("", "·", ".", "-", "–", "0"):
        return 0, False
    if text == "?":
        return 1, True
    m = re.fullmatch(r"(\d+)(\?)?", text)
    if m:
        return int(m.group(1)), bool(m.group(2))
    return None


class Matrix:
    """The first table in a file with a total column and binary-looking actor columns."""

    def __init__(self, path: Path):
        self.path = path
        self.lines = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").split("\n")
        self.header_line = None
        for start, block in self._tables():
            header = [strip_md(c) for c in split_row(block[0][1])]
            totals = [k for k, h in enumerate(header) if TOTAL_HEADER.match(h)]
            if not totals:
                continue
            body = [(i, split_row(l)) for i, l in block[1:] if len(split_row(l)) == len(header)]
            data = [(i, c) for i, c in body if not MARGIN_ROW.match(strip_md(c[0]))]
            cols = []
            for k in range(totals[-1]):
                if header[k].lower() in LABEL_HEADERS or not data:
                    continue
                if sum(score(c[k]) is not None for _, c in data) / len(data) >= 0.8:
                    cols.append(k)
            if not cols:
                continue
            self.header_line, self.header, self.total_col = start, header, totals[-1]
            self.cols = cols
            self.actors = [header[k] for k in cols]
            self.label_cols = [k for k in range(totals[-1]) if k not in cols]
            self.rows = data
            self.margins = [(i, c) for i, c in body if MARGIN_ROW.match(strip_md(c[0]))]
            break
        if self.header_line is None:
            raise UsageError(f"{path}: no impact matrix found (a table with actor columns and a "
                             f"Σ / Total column)")

    def _tables(self):
        block, start = [], None
        for i, line in enumerate(self.lines):
            if line.strip().startswith("|"):
                if start is None:
                    start = i
                if not re.fullmatch(r"\|?[\s:|-]+\|?", line.strip()):
                    block.append((i, line))
            elif block:
                yield start, block
                block, start = [], None
        if block:
            yield start, block

    def key(self, cells: list[str]) -> str:
        """A row's stressor ID (S-12), or its first label cell's text."""
        for k in self.label_cols:
            m = STRESSOR_ID.search(strip_md(cells[k]))
            if m:
                return m.group(0)
        return strip_md(cells[self.label_cols[0]]) if self.label_cols else strip_md(cells[0])

    def cells(self) -> dict[str, dict[str, tuple[int, bool] | None]]:
        return {self.key(c): {self.header[k]: score(c[k]) for k in self.cols} for _, c in self.rows}


# --------------------------------------------------------------------------
# totals


def totals(path: Path, do_write: bool) -> tuple[list[str], bool]:
    m = Matrix(path)
    out, problems = [], 0
    grid = m.cells()
    col_sum = collections.Counter()
    unknown, severity, wrong = [], [], []
    row_sums = {}
    for i, c in m.rows:
        key = m.key(c)
        got = 0
        for k in m.cols:
            v = score(c[k])
            if v is None:
                severity.append(f"line {i + 1}: {key} × {m.header[k]} = '{strip_md(c[k])}' is not a score")
                continue
            value, unk = v
            if value > 1:
                severity.append(f"line {i + 1}: {key} × {m.header[k]} = {value}")
            if unk:
                unknown.append(f"{key} × {m.header[k]}")
            got += value
            col_sum[m.header[k]] += value
        row_sums[i] = got
        stated = re.search(r"\d+", strip_md(c[m.total_col]))
        if stated and int(stated.group()) != got:
            wrong.append(f"line {i + 1}: {key} cells sum to {got}, the row says {stated.group()}")
        elif not stated:
            wrong.append(f"line {i + 1}: {key} has no row total (cells sum to {got})")
    total = sum(col_sum.values())
    for i, c in m.margins:
        for k in m.cols:
            stated = re.search(r"\d+", strip_md(c[k]))
            if stated and int(stated.group()) != col_sum[m.header[k]]:
                wrong.append(f"line {i + 1}: column {m.header[k]} sums to {col_sum[m.header[k]]}, "
                             f"the totals row says {stated.group()}")
        stated = re.search(r"\d+", strip_md(c[m.total_col]))
        if stated and int(stated.group()) != total:
            wrong.append(f"line {i + 1}: the matrix sums to {total}, the totals row says {stated.group()}")
    if not m.margins:
        wrong.append("no totals row: the matrix without its margins is a table, not a diagnosis")

    out.append(f"{path.name}: {len(m.rows)} stressors × {len(m.actors)} actors, total system impact "
               f"{total}{f' ({len(unknown)} unknown cells counted as 1)' if unknown else ''}")
    if severity:
        problems += len(severity)
        out.append(f"\nNot binary ({len(severity)}): scoring is 0 or 1; a severity scale lets a "
                   f"stressor be argued down. Counted as written in the totals above:")
        out += [f"  - {s}" for s in severity[:12]]
    if wrong:
        problems += len(wrong)
        out.append(f"\nMargins ({len(wrong)}):")
        out += [f"  - {w}" for w in wrong[:12]]
    if unknown:
        out.append(f"\nUnknown cells ({len(unknown)}), each to be registered as an assumption: "
                   + ", ".join(unknown[:20]) + (" ..." if len(unknown) > 20 else ""))

    out += reading_aids(m, grid, col_sum, total)

    if do_write:
        if severity:
            out.append("\nNot written: fix the non-binary cells first; the margins of a matrix "
                       "that is not binary mean nothing.")
            return out, True
        write_margins(m, row_sums, col_sum, total)
        out.append(f"\nWritten: row totals and the totals row in {path.name}. No score was changed.")
        return out, bool(severity)
    return out, bool(problems)


def reading_aids(m: Matrix, grid: dict, col_sum: collections.Counter, total: int) -> list[str]:
    """The four checks of "Reading the matrix", as numbers. The diagnosis stays with the reader."""
    out = ["\nReading aids (the method's four checks; naming the mechanism is yours):"]
    if not total:
        return out + ["  - the matrix is empty"]
    ranked = sorted(m.actors, key=lambda a: -col_sum[a])
    top = ranked[:3]
    share = sum(col_sum[a] for a in top) / total
    out.append("  1. Concentration: " + ", ".join(f"{a} {col_sum[a]}" for a in top)
               + f" carry {share:.0%} of the total")
    sets: dict[frozenset, list[str]] = collections.defaultdict(list)
    for key, row in grid.items():
        hit = frozenset(a for a, v in row.items() if v and v[0] >= 1)
        if len(hit) >= 2:
            sets[hit].append(key)
    clusters = sorted(((ks, a) for a, ks in sets.items() if len(ks) >= 2), key=lambda x: -len(x[0]))
    if clusters:
        out.append("  2. Clusters (stressors hitting the identical actor set):")
        for keys, actors in clusters[:6]:
            out.append(f"     - {', '.join(keys[:8])}{' ...' if len(keys) > 8 else ''} "
                       f"→ {', '.join(sorted(actors))}")
    else:
        out.append("  2. Clusters: no two stressors hit the identical actor set; look for near matches")
    mean = total / len(m.actors)
    spread = (sum((col_sum[a] - mean) ** 2 for a in m.actors) / len(m.actors)) ** 0.5
    cv = spread / mean if mean else 0
    out.append(f"  3. Flatness: column totals vary by {cv:.2f} of their mean"
               + (" (flat: the stressors may be too generic)" if cv < 0.25 else ""))
    zeros = [a for a in m.actors if col_sum[a] == 0]
    out.append("  4. Zero columns: " + (", ".join(zeros) + " (stateless, or not understood?)"
                                        if zeros else "none"))
    return out


def write_margins(m: Matrix, row_sums: dict, col_sum: collections.Counter, total: int) -> None:
    lines = list(m.lines)

    def bold(cell: str, value: int) -> str:
        return f"**{value}**" if cell.startswith("**") or not cell else str(value)

    for i, c in m.rows:
        c = list(c)
        c[m.total_col] = bold(c[m.total_col], row_sums[i])
        lines[i] = "| " + " | ".join(c) + " |"
    margin = ["" for _ in m.header]
    margin[0] = "**Total**"
    for k in m.cols:
        margin[k] = f"**{col_sum[m.header[k]]}**"
    margin[m.total_col] = f"**{total}**"
    row = "| " + " | ".join(margin) + " |"
    if m.margins:
        lines[m.margins[0][0]] = row
    else:
        last = max(i for i, _ in m.rows)
        lines.insert(last + 1, row)
    text = "\n".join(lines)
    m.path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8", newline="\n")


# --------------------------------------------------------------------------
# compare


def compare(before: Path, after: Path) -> tuple[list[str], bool]:
    a, b = Matrix(before), Matrix(after)
    ga, gb = a.cells(), b.cells()
    common = [k for k in ga if k in gb]
    added_rows = [k for k in gb if k not in ga]
    removed_rows = [k for k in ga if k not in gb]
    actors = list(dict.fromkeys(a.actors + b.actors))
    added_cols = [x for x in b.actors if x not in a.actors]
    removed_cols = [x for x in a.actors if x not in b.actors]

    def val(grid, row, actor):
        v = grid.get(row, {}).get(actor)
        return v[0] if v else 0

    out = [f"{before.name} → {after.name}"]
    out.append(f"\nStressor set: {len(common)} shared"
               + (f", {len(added_rows)} added ({', '.join(added_rows[:8])}{' ...' if len(added_rows) > 8 else ''})"
                  if added_rows else "")
               + (f", {len(removed_rows)} removed ({', '.join(removed_rows[:8])})" if removed_rows else ""))
    if added_cols or removed_cols:
        out.append("Actor set: " + (f"added {', '.join(added_cols)}" if added_cols else "")
                   + ("; " if added_cols and removed_cols else "")
                   + (f"removed {', '.join(removed_cols)}" if removed_cols else ""))
    total_a = sum(val(ga, r, x) for r in common for x in actors)
    total_b = sum(val(gb, r, x) for r in common for x in actors)
    total_b_all = sum(val(gb, r, x) for r in gb for x in actors)
    out.append(f"\nTotal against the shared stressor set: {total_a} → {total_b} ({total_b - total_a:+d})")
    gone = sum(val(ga, r, x) for r in common for x in removed_cols)
    new = sum(val(gb, r, x) for r in common for x in added_cols)
    if gone or new:
        out.append(f"  of which {gone} left with removed actors and {new} arrived with added ones; "
                   f"on the actors in both, {total_a - gone} → {total_b - new} "
                   f"({(total_b - new) - (total_a - gone):+d})")
    if added_rows:
        out.append(f"Total against the expanded set: {total_b_all} "
                   f"(the {len(added_rows)} added stressors carry {total_b_all - total_b}). "
                   f"Comparing {sum(val(ga, r, x) for r in ga for x in actors)} with {total_b_all} "
                   f"would mix two stressor sets.")

    out.append("\n| Actor | Before | After | Delta | Residual applied |")
    out.append("|---|---|---|---|---|")
    for x in actors:
        before_x = sum(val(ga, r, x) for r in common)
        after_x = sum(val(gb, r, x) for r in common)
        note = " (added)" if x in added_cols else " (removed)" if x in removed_cols else ""
        out.append(f"| {x}{note} | {before_x if x in a.actors else '—'} | "
                   f"{after_x if x in b.actors else '—'} | {after_x - before_x:+d} |  |")
    out.append(f"| **Total** | **{total_a}** | **{total_b}** | **{total_b - total_a:+d}** |  |")
    out.append("\nThe last column is yours: which residual removed which cells.")

    both = [x for x in actors if x in a.actors and x in b.actors]
    cleared = [f"{r} × {x}" for r in common for x in both if val(ga, r, x) and not val(gb, r, x)]
    raised = [f"{r} × {x}" for r in common for x in both if not val(ga, r, x) and val(gb, r, x)]
    dropped = sum(val(ga, r, x) for r in common for x in removed_cols)
    out.append(f"\nCells cleared on shared stressors and actors ({len(cleared)}): "
               + (", ".join(cleared[:30]) + (" ..." if len(cleared) > 30 else "") if cleared else "none"))
    if dropped:
        out.append(f"Cells that left with a removed actor ({dropped}): not cleared, the column is gone "
                   f"({', '.join(removed_cols)}).")
    if raised:
        out.append(f"Cells that became 1 on shared stressors ({len(raised)}), worth a look: "
                   + ", ".join(raised[:30]))
    return out, bool(raised)


# --------------------------------------------------------------------------
# claims


RESIDUAL_HEADING = re.compile(r"^#{2,4}\s+(R-?[\w.]+)\b(.*)$")
CLAIM_LINE = re.compile(r"(S-\d+[a-z]?)\s*(?::\s*|\(\s*)([A-Za-z][\w/]*(?:\s*,\s*[A-Za-z][\w/]*)*)")


def parse_claims(path: Path, actors: list[str]) -> dict[str, dict]:
    """Residual -> {stated: N or None, cells: [(S, actor)], outside: [(S, actor)]}."""
    known = set(actors)
    out: dict[str, dict] = {}
    current = None
    in_clears = False
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        h = RESIDUAL_HEADING.match(line)
        if h:
            current = h.group(1)
            title = strip_md(h.group(2)).lstrip(":—–- ").strip()
            out[current] = {"stated": None, "cells": [], "outside": [],
                            "title": (title[:60] + "…") if len(title) > 60 else title}
            in_clears = False
            continue
        if current is None:
            continue
        m = re.search(r"\*\*Clears (\d+) cells?", line, re.IGNORECASE)
        if m:
            out[current]["stated"] = int(m.group(1))
            in_clears = True
            continue
        if in_clears and line.startswith("**") and not re.search(r"outside", line, re.I):
            in_clears = False
        if not in_clears or not line.strip().startswith(("-", "*")):
            if in_clears and line.strip() and not line.strip().startswith(("-", "*")):
                in_clears = False
            continue
        outside = bool(re.search(r"outside the cluster", line, re.IGNORECASE))
        for s, cols in CLAIM_LINE.findall(line):
            for col in (c.strip() for c in cols.split(",")):
                if col in known:
                    out[current]["outside" if outside else "cells"].append((s, col))
    return {k: v for k, v in out.items() if v["stated"] is not None or v["cells"] or v["outside"]}


def claims(residuals: Path, before: Path, after: Path | None) -> tuple[list[str], bool]:
    a = Matrix(before)
    ga = a.cells()
    b = Matrix(after) if after else None
    gb = b.cells() if b else None
    parsed = parse_claims(residuals, a.actors)
    if not parsed:
        raise UsageError(f"{residuals}: no residual with a `**Clears N cells:**` list was found")
    out = [f"{residuals.name} against {before.name}" + (f" and {after.name}" if after else "")]
    flagged = False
    owner: dict[tuple, list[str]] = collections.defaultdict(list)
    for name, r in parsed.items():
        cells = r["cells"] + r["outside"]
        for c in cells:
            owner[c].append(name)
        not_one = [f"{s} × {x}" for s, x in cells
                   if not (ga.get(s, {}).get(x) or (0, False))[0]]
        missing_row = sorted({s for s, _ in cells if s not in ga})
        listed = len(cells)
        line = f"\n{name}{' (' + r['title'] + ')' if r['title'] else ''}: claims {listed} cell(s)"
        line += f" ({len(r['outside'])} outside the cluster)" if r["outside"] else ""
        if r["stated"] is not None and r["stated"] != listed:
            line += f"; the text says {r['stated']}, the list has {listed}"
            flagged = True
        out.append(line)
        if missing_row:
            flagged = True
            out.append(f"  - stressors not in {before.name}: {', '.join(missing_row)}")
        if [c for c in not_one if c.split(' × ')[0] not in missing_row]:
            flagged = True
            out.append("  - claimed but not 1 before the residual (nothing to clear): "
                       + ", ".join(c for c in not_one if c.split(' × ')[0] not in missing_row))
        if gb is not None:
            gone = [f"{s} × {x}" for s, x in cells if x not in b.actors]
            still = [f"{s} × {x}" for s, x in cells
                     if x in b.actors and (gb.get(s, {}).get(x) or (0, False))[0]]
            if still:
                flagged = True
                out.append(f"  - still 1 in {after.name}: {', '.join(still)}")
            else:
                out.append(f"  - every claimed cell is 0 in {after.name}"
                           + (f", except {len(gone)} whose actor was removed: {', '.join(gone)}"
                              if gone else ""))
    shared = {c: n for c, n in owner.items() if len(n) > 1}
    distinct = len(owner)
    out.append(f"\nDistinct cells claimed across residuals: {distinct}"
               + (f" ({sum(len(v['cells']) + len(v['outside']) for v in parsed.values())} listed, "
                  f"{len(shared)} claimed by more than one)" if shared else ""))
    for (s, x), names in sorted(shared.items()):
        out.append(f"  - {s} × {x}: {', '.join(names)}")
    out.append("A compound forecast counts each cell once: " + str(distinct) + ".")
    if gb is not None:
        # Cleared between the iterations, on stressors in both, by nothing claimed:
        # either a residual's effect nobody wrote down, or a re-score to explain.
        unclaimed = [f"{s} × {x}" for s, row in ga.items() if s in gb
                     for x, v in row.items()
                     if v and v[0] and x in b.actors
                     and not (gb[s].get(x) or (0, False))[0] and (s, x) not in owner]
        if unclaimed:
            flagged = True
            out.append(f"\nCleared with no residual claiming them ({len(unclaimed)}): "
                       + ", ".join(unclaimed) + ". Name what cleared each one: an effect no "
                       "residual recorded, or a re-score that needs its reason.")
    return out, flagged


# --------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(prog="matrix.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("totals")
    p.add_argument("matrix")
    p.add_argument("--write", action="store_true")
    p = sub.add_parser("compare")
    p.add_argument("before")
    p.add_argument("after")
    p = sub.add_parser("claims")
    p.add_argument("residuals")
    p.add_argument("before")
    p.add_argument("--after")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2
    try:
        for name in ("matrix", "before", "after", "residuals"):
            value = getattr(args, name, None)
            if value and not Path(value).is_file():
                raise UsageError(f"no such file: {value}")
        if args.command == "totals":
            out, flagged = totals(Path(args.matrix), args.write)
        elif args.command == "compare":
            out, flagged = compare(Path(args.before), Path(args.after))
        else:
            out, flagged = claims(Path(args.residuals), Path(args.before),
                                  Path(args.after) if args.after else None)
    except UsageError as exc:
        print(f"matrix: {exc}", file=sys.stderr)
        return 2
    print("\n".join(out))
    return 1 if flagged else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
