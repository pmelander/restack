#!/usr/bin/env python3
"""Validate a rendered batch of event statements before it enters a matrix.

Four checks, in the order they matter:

  1. walkability   - can each statement be taken to an actor and asked what
                     happens? A category cannot be walked; a scenario can.
  2. coverage      - did every spec render, and did the stratified cells fill?
  3. duplicates    - character n-gram Jaccard over the batch.
  4. leakage       - did system context reach a prompt that should not have
                     had it? This is the silent one, and the only check that
                     can tell you the most valuable rows in the batch were
                     quietly converted into ordinary ones.

Standard library only. Embeddings would read better than n-gram Jaccard and
need API access a Claude Code Team seat does not have; at tens of statements
per batch Jaccard catches the convergence that matters.

Usage:
    validate.py statements.jsonl --specs specs.jsonl
    validate.py statements.jsonl --specs specs.jsonl --forbid "acme,booking,PriceManager"
    validate.py statements.jsonl --specs specs.jsonl --forbid-file context-terms.txt
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

BLIND_TRACKS = ("uncoupled", "adjacent")
MIN_WORDS = 8
NGRAM = 4
DEFAULT_SIMILARITY = 0.45

# A wholly collapsed batch produces hundreds of pairs, and a report nobody
# scrolls to the end of is a report nobody reads. Print the worst offenders
# and say how many more there are.
MAX_REPORTED = 10

TIME_WORDS = (
    "hour", "hours", "day", "days", "week", "weeks", "month", "months",
    "year", "years", "overnight", "morning", "evening", "season", "quarter",
    "notice", "deadline", "immediately",
)


def read_jsonl(path: Path, label: str) -> list[dict]:
    rows = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        sys.exit(f"error: {label} not found: {path}")
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            sys.exit(f"error: {path}:{lineno}: invalid JSON - {exc}")
    if not rows:
        sys.exit(f"error: {label} is empty: {path}")
    return rows


def ngrams(text: str) -> set[str]:
    squashed = re.sub(r"\s+", " ", text.lower().strip())
    if len(squashed) < NGRAM:
        return {squashed}
    return {squashed[i:i + NGRAM] for i in range(len(squashed) - NGRAM + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def has_concrete_anchor(statement: str) -> bool:
    """A walkable scenario usually pins something down: a number, a named
    thing, or a time. Its absence is a signal, not a verdict."""
    if re.search(r"\d", statement):
        return True
    if any(word in statement.lower() for word in TIME_WORDS):
        return True
    # A capitalised word that is not the first word of a sentence.
    return bool(re.search(r"(?<![.!?]\s)(?<!^)\b[A-Z][a-z]{2,}", statement))


def check_walkability(statements: list[dict]) -> list[str]:
    flagged = []
    for row in statements:
        text = (row.get("statement") or "").strip()
        sid = row.get("spec_id", "?")
        if not text:
            flagged.append(f"{sid}: empty statement")
            continue
        words = text.split()
        if len(words) < MIN_WORDS:
            flagged.append(f"{sid}: {len(words)} words - too thin to walk: {text!r}")
        elif not has_concrete_anchor(text):
            flagged.append(f"{sid}: no concrete anchor (no number, name or timeframe): {text!r}")
    return flagged


def check_coverage(statements: list[dict], specs: list[dict]) -> tuple[list[str], dict]:
    problems = []
    rendered = {row.get("spec_id") for row in statements}
    expected = {spec["id"] for spec in specs}

    missing = sorted(expected - rendered)
    if missing:
        problems.append(f"{len(missing)} spec(s) never rendered: {', '.join(missing[:10])}")
    extra = sorted(rendered - expected)
    if extra:
        problems.append(f"{len(extra)} statement(s) reference no spec: {', '.join(extra[:10])}")

    counts: dict = {}
    skip = {"id", "seed", "second"}
    for spec in specs:
        for dim, value in spec.items():
            if dim in skip:
                continue
            counts.setdefault(dim, collections.Counter())[value] += 1
    return problems, counts


def check_duplicates(statements: list[dict], threshold: float) -> list[str]:
    grams = [
        (row.get("spec_id", "?"), row.get("statement", ""), ngrams(row.get("statement", "")))
        for row in statements
        if row.get("statement")
    ]
    pairs = []
    for i in range(len(grams)):
        for j in range(i + 1, len(grams)):
            score = jaccard(grams[i][2], grams[j][2])
            if score >= threshold:
                pairs.append((score, grams[i], grams[j]))

    pairs.sort(key=lambda p: -p[0])
    flagged = [
        f"{a[0]} / {b[0]}: similarity {score:.2f}\n      {a[1]!r}\n      {b[1]!r}"
        for score, a, b in pairs[:MAX_REPORTED]
    ]
    if len(pairs) > MAX_REPORTED:
        flagged.append(
            f"... and {len(pairs) - MAX_REPORTED} more pair(s) above {threshold}. "
            f"At this density the batch has collapsed - look at the taxonomy, not the renders."
        )
    return flagged


def check_leakage(statements: list[dict], specs: list[dict], forbidden: list[str]) -> list[str]:
    if not forbidden:
        return []
    grounding = {spec["id"]: spec.get("grounding") for spec in specs}
    flagged = []
    for row in statements:
        sid = row.get("spec_id")
        track = row.get("grounding") or grounding.get(sid)
        if track not in BLIND_TRACKS:
            continue
        text = (row.get("statement") or "").lower()
        hits = sorted({term for term in forbidden if term.lower() in text})
        if hits:
            flagged.append(
                f"{sid} ({track}): names {', '.join(repr(h) for h in hits)} - "
                f"system context reached a prompt that should not have had it"
            )
    return flagged


def report(title: str, lines: list[str], ok: str) -> None:
    print(f"\n{title}")
    if not lines:
        print(f"  {ok}")
        return
    for line in lines:
        print(f"  - {line}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a rendered batch of event statements.")
    parser.add_argument("statements", type=Path, help="rendered statements JSONL")
    parser.add_argument("--specs", type=Path, required=True, help="the specs the batch was drawn from")
    parser.add_argument("--forbid", default="", help="comma-separated system-context terms")
    parser.add_argument("--forbid-file", type=Path, help="one system-context term per line")
    parser.add_argument("--similarity", type=float, default=DEFAULT_SIMILARITY)
    args = parser.parse_args(argv)

    statements = read_jsonl(args.statements, "statements")
    specs = read_jsonl(args.specs, "specs")

    forbidden = [t.strip() for t in args.forbid.split(",") if t.strip()]
    if args.forbid_file:
        forbidden += [
            line.strip()
            for line in args.forbid_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]

    walkability = check_walkability(statements)
    coverage_problems, counts = check_coverage(statements, specs)
    duplicates = check_duplicates(statements, args.similarity)
    leakage = check_leakage(statements, specs, forbidden)

    print(f"{len(statements)} statement(s) from {len(specs)} spec(s)")

    report(
        "1. Walkability - candidates for your judgement, not verdicts",
        walkability,
        "no statement looks too thin to walk",
    )
    if walkability:
        print(
            "\n  These are heuristics: short, or pinning nothing down. Read them and\n"
            "  decide. A stressor that cannot be taken to an actor and asked what\n"
            "  happens is not finished - rewrite it or drop the spec and redraw."
        )

    report("2. Coverage", coverage_problems, "every spec rendered exactly once")
    for dim in ("grounding", "plausibility"):
        if dim in counts:
            spread = ", ".join(f"{v}={n}" for v, n in sorted(counts[dim].items()))
            print(f"  {dim}: {spread}")
    for dim in sorted(set(counts) - {"grounding", "plausibility"}):
        unused = ""
        if len(counts[dim]) == 1:
            unused = "   <- single value across the whole batch"
        print(f"  {dim}: {len(counts[dim])} distinct value(s){unused}")

    report(
        f"3. Near-duplicates (char {NGRAM}-gram Jaccard >= {args.similarity})",
        duplicates,
        "no pair above threshold",
    )
    if duplicates:
        print(
            "\n  Convergence that isolation did not prevent points at the taxonomy\n"
            "  being too coarse, not at the render stage."
        )

    report(
        "4. Context leakage on the blind tracks",
        leakage,
        "no forbidden term in an uncoupled or adjacent statement"
        if forbidden
        else "not checked - pass --forbid or --forbid-file with your system's terms",
    )

    print(
        "\nNot checked, deliberately: whether a statement is relevant to the system.\n"
        "Uncoupled draws miss often, and a full-zero row in the matrix is a finding\n"
        "about the system's coupling to the world. Filtering on apparent relevance\n"
        "is the architect's prior re-entering by the back door."
    )

    hard = coverage_problems + leakage
    if hard:
        print(f"\n{len(hard)} blocking problem(s)", file=sys.stderr)
        return 1
    soft = len(walkability) + len(duplicates)
    print(f"\nbatch usable; {soft} item(s) for review" if soft else "\nbatch clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
