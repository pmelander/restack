#!/usr/bin/env python3
"""Trace the documents a ReStack journey produces, and list where they drift.

Reads a project's docs/ tree - ADRs, the journey files, impact matrices and the
descriptive documents (HLD, LLDs, deployment guide, runbook) - and reports the
inconsistencies a script can find without judgement: an ID cited with no
definition, a register row whose status a later line contradicts, a Knock-on
row claiming a document was updated when it was not, an amendment written as a
footnote, a superseded ADR still cited as current, a matrix scored before a
decision that changed the actor set, a row total that does not add up.

The output is a worklist, not a verdict (ADR-021). Every item is a place to
look; the reader confirms it by opening the document, and decides what it
means. Silence is not consistency either: the script sees only patterns that
the toolkit's formats define, and most drift is semantic.

Read-only. Standard library only, no network. Dates come from git when the
docs are in a work tree, otherwise from file modification times, and the
report says which.

Usage:
    python trace.py [scan] [DOCS]            all checks (default DOCS: docs)
    python trace.py scan DOCS --only KO,AM   some checks
    python trace.py terms TERM... [--docs DOCS] [--in FILE...]
                                             unmarked passages that still use
                                             a replaced mechanism's terms
    python trace.py refs ID [--docs DOCS]    every citation of ID (ADR-12, D7, A-31)
    add --json to any command for machine-readable output

Exit status: 0 nothing found, 1 items found, 2 usage error.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CHECKS = {
    "REF": "references with no definition",
    "REG": "assumptions register drift",
    "KO": "knock-on changes unfinished",
    "AM": "amendments written as footnotes",
    "SUP": "superseded decisions still cited",
    "BASE": "matrices scored before an actor-set change",
    "MX": "matrix arithmetic and scoring",
    "ALERT": "runbook alerts defined nowhere else",
    "PH": "placeholders left in documents",
    "PDF": "exports older than their source",
}
LABELS = {**CHECKS, "TERM": "passages still using a replaced term", "CITE": "citations"}

# Directories that are a record of what happened, not a description of the
# system. They cite superseded decisions legitimately, and they are never
# rewritten when a decision changes.
HISTORY_DIRS = {"journey", "reviews", "stressor-analysis", "discovery"}

# A line carrying one of these is already telling the reader that what it
# cites is no longer current.
MARKER = re.compile(
    r"supersed|deprecat|withdrawn|replac|retired|formerly|historic|no longer|"
    r"amended|~~|\bwas\b|\bold\b",
    re.IGNORECASE,
)

ADR_ID = re.compile(r"\bADR-(\d{1,5})\b")
D_ID = re.compile(r"\bD(\d{1,3})\b")
A_ID = re.compile(r"\bA-(\d{1,4})\b")
DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

STATUS_VOCAB = re.compile(
    r"^(Open|Partly resolved|Resolved by design \(test pending\)|Resolved|Withdrawn|"
    r"Superseded by D\d+)(?![\w-])",
    re.IGNORECASE,
)
CLOSE_WORDS = re.compile(r"FALSIFIED|resolved|withdrawn|closed|superseded|confirmed", re.IGNORECASE)


def skill_version() -> str:
    """The version in this skill's SKILL.md frontmatter, the one place it is set.

    Printed in every report header, so two runs over unchanged documents can be
    told apart by the script that produced them.
    """
    try:
        text = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return "unknown"
    m = re.search(r"^version:\s*(\S+)", text, re.MULTILINE)
    return m.group(1) if m else "unknown"


VERSION = skill_version()


class UsageError(Exception):
    """Bad arguments: reported on stderr with exit status 2."""


@dataclass
class Finding:
    check: str
    path: str
    line: int | None
    message: str
    detail: list[str] = field(default_factory=list)
    heuristic: bool = False


@dataclass
class Doc:
    path: Path
    rel: str
    kind: str                   # adr | register | log | matrix | history | descriptive
    lines: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def body_start(self) -> int:
        """Index of the first level-2 heading: everything above it is the header."""
        for i, line in enumerate(self.lines):
            if line.startswith("## "):
                return i
        return min(len(self.lines), 5)          # no sections: treat the title block as header

    @property
    def stem(self) -> str:
        return self.path.stem


@dataclass
class Adr:
    doc: Doc
    number: int
    status: str
    date: dt.date | None

    @property
    def retired(self) -> bool:
        return bool(re.match(r"\W*(superseded|deprecated)", self.status, re.IGNORECASE))

    @property
    def label(self) -> str:
        return f"ADR-{self.number:04d}" if self.number < 10000 else f"ADR-{self.number}"


# --------------------------------------------------------------------------
# Loading


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig", errors="replace").splitlines()


def classify(rel: str) -> str:
    parts = rel.split("/")
    name = parts[-1]
    if "archive" in parts[:-1]:
        return "history"
    if parts[0] == "adr" and re.match(r"ADR-\d", name, re.IGNORECASE):
        return "adr"
    if rel == "journey/assumptions-register.md":
        return "register"
    if rel == "journey/decisions-log.md":
        return "log"
    if parts[0] == "stressor-analysis" and name.startswith("matrix"):
        return "matrix"
    if parts[0] in HISTORY_DIRS:
        return "history"
    return "descriptive"


def load(root: Path) -> list[Doc]:
    docs = []
    for path in sorted(root.rglob("*.md")):
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        docs.append(Doc(path, rel, classify(rel), read_lines(path)))
    return docs


def parse_adr(doc: Doc) -> Adr | None:
    match = re.match(r"ADR-(\d+)", doc.path.name, re.IGNORECASE)
    if not match:
        return None
    status, date = "", None
    for line in doc.lines[: max(doc.body_start, 1) + 5]:
        m = re.match(r"\s*\*\*Status:?\*\*:?\s*(.+)", line)
        if m and not status:
            status = m.group(1).strip()
        m = re.match(r"\s*\*\*Date:?\*\*:?\s*(\d{4}-\d{2}-\d{2})", line)
        if m and date is None:
            date = to_date(m.group(1))
    return Adr(doc, int(match.group(1)), status, date)


def to_date(text: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(text)
    except ValueError:
        return None


class Dates:
    """When each file last changed: git commit time in a work tree, else mtime.

    A file with uncommitted changes in a work tree uses its mtime, because the
    commit date would say it has not changed when it has.
    """

    def __init__(self, root: Path, mode: str = "auto"):
        self.root = root
        self.source = "mtime"
        self.committed: dict[str, float] = {}
        self.dirty: set[str] = set()
        self.top: Path | None = None
        if mode in ("auto", "git"):
            self._from_git()
        if mode == "git" and self.source != "git":
            raise UsageError("trace: --dates git, but DOCS is not inside a git work tree")

    def _git(self, *args: str) -> str | None:
        try:
            done = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True,
                                  timeout=20, check=False)
        except (OSError, subprocess.SubprocessError):
            return None
        if done.returncode != 0:
            return None
        return done.stdout.decode("utf-8", errors="replace")

    def _from_git(self) -> None:
        top = self._git("rev-parse", "--show-toplevel")
        if not top:
            return
        self.top = Path(top.strip()).resolve()
        log = self._git("log", "--format=@%ct", "--name-only", "--no-renames", "--", ".")
        if log is None:
            return
        stamp = None
        for line in log.splitlines():
            if line.startswith("@"):
                stamp = float(line[1:])
            elif line and stamp is not None:
                self.committed.setdefault(line, stamp)      # newest first
        status = self._git("status", "--porcelain", "--untracked-files=all", "--", ".") or ""
        for line in status.splitlines():
            name = line[3:].strip().strip('"')
            if " -> " in name:
                name = name.split(" -> ", 1)[1]
            self.dirty.add(name)
        self.source = "git"

    def stamp(self, path: Path) -> float:
        if self.source == "git" and self.top is not None:
            try:
                key = path.resolve().relative_to(self.top).as_posix()
            except ValueError:
                key = None
            if key and key not in self.dirty and key in self.committed:
                return self.committed[key]
        return path.stat().st_mtime

    def day(self, path: Path) -> dt.date:
        return dt.datetime.fromtimestamp(self.stamp(path)).date()


# --------------------------------------------------------------------------
# Markdown helpers


def strip_md(cell: str) -> str:
    """Drop emphasis and code marks, keeping underscores inside identifiers."""
    return re.sub(r"\*+|`|(?<!\w)_+|_+(?!\w)", "", cell).strip()


def table_rows(lines: list[str], start: int = 0, end: int | None = None):
    """Yield (line_index, cells) for each table, grouped: a list per table."""
    end = len(lines) if end is None else end
    table: list[tuple[int, list[str]]] = []
    for i in range(start, end):
        line = lines[i].strip()
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue                                    # separator row
            table.append((i, cells))
        elif table:
            yield table
            table = []
    if table:
        yield table


def section(lines: list[str], heading: re.Pattern) -> tuple[int, int] | None:
    for i, line in enumerate(lines):
        m = re.match(r"(#{1,6})\s", line)
        if m and heading.search(line):
            level = len(m.group(1))
            for j in range(i + 1, len(lines)):
                n = re.match(r"(#{1,6})\s", lines[j])
                if n and len(n.group(1)) <= level:
                    return i, j
            return i, len(lines)
    return None


def outside_fences(lines: list[str]):
    fenced = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield i, line


def placeholder(cell: str) -> bool:
    text = strip_md(cell)
    return not text or (text.startswith("[") and text.endswith("]"))


# --------------------------------------------------------------------------
# Checks


class Corpus:
    def __init__(self, root: Path, dates: Dates):
        self.root = root
        self.dates = dates
        self.docs = load(root)
        self.adrs: dict[int, Adr] = {}
        for doc in self.docs:
            if doc.kind == "adr":
                adr = parse_adr(doc)
                if adr:
                    self.adrs[adr.number] = adr
        self.register = next((d for d in self.docs if d.kind == "register"), None)
        self.log = next((d for d in self.docs if d.kind == "log"), None)
        self.decisions = self._decisions()
        self.assumptions = self._assumption_rows()

    def by_kind(self, *kinds: str) -> list[Doc]:
        return [d for d in self.docs if d.kind in kinds]

    def _decisions(self) -> dict[int, dict]:
        out: dict[int, dict] = {}
        if not self.log:
            return out
        current = None
        for i, line in enumerate(self.log.lines):
            if line.startswith("## "):
                m = D_ID.search(line)
                current = int(m.group(1)) if m else None
                if current is not None and current not in out:
                    out[current] = {"line": i + 1, "actors": None}
                continue
            m = re.search(r"\*\*Changes the actor set:?\*\*:?\s*(\w+)", line, re.IGNORECASE)
            if m and current is not None:
                out[current]["actors"] = m.group(1).lower() == "yes"
        return out

    def _assumption_rows(self) -> dict[int, dict]:
        """Register rows keyed by number, so A-09 and A-9 are one assumption.

        Tolerates the shapes a long journey leaves behind: several tables, rows
        that a scripted append landed outside any table (`orphan`), and
        assumptions introduced as `**A-n (new):**` bullets (status unknown).
        """
        rows: dict[int, dict] = {}
        self.register_tables: list[int] = []
        self.orphan_rows: list[int] = []
        if not self.register:
            return rows
        for table in table_rows(self.register.lines):
            header = [strip_md(c).lower() for c in table[0][1]]
            if header and header[0] == "id":
                if "status" in header:
                    self.register_tables.append(table[0][0] + 1)
                col = header.index("status") if "status" in header else None
                body = table[1:]
            elif re.fullmatch(r"A-\d+", strip_md(table[0][1][0])):
                self.orphan_rows.extend(i + 1 for i, _ in table)
                col, body = None, table
            else:
                continue
            for i, cells in body:
                key = strip_md(cells[0])
                if not re.fullmatch(r"A-\d+", key):
                    continue
                k = col
                if k is None:                       # no header: status is the last cell
                    k = len(cells) - 2 if DATE.fullmatch(strip_md(cells[-1])) else len(cells) - 1
                status = strip_md(cells[k]) if k < len(cells) else ""
                rows.setdefault(int(key[2:]), {"id": key, "line": i + 1, "status": status,
                                               "dupes": []})["dupes"].append(i + 1)
        for i, line in enumerate(self.register.lines):
            m = re.search(r"\*\*(A-(\d+))\s*\(new", line)
            if m and int(m.group(2)) not in rows:
                rows[int(m.group(2))] = {"id": m.group(1), "line": i + 1, "status": None,
                                         "dupes": [i + 1]}
        return rows


def check_ref(c: Corpus) -> list[Finding]:
    out: list[Finding] = []
    sites: dict[str, list[str]] = {}

    def note(key: str, doc: Doc, i: int) -> None:
        sites.setdefault(key, []).append(f"{doc.rel}:{i + 1}")

    max_d = max(c.decisions, default=0)
    for doc in c.docs:
        for i, line in outside_fences(doc.lines):
            if c.adrs:
                for m in ADR_ID.finditer(line):
                    if int(m.group(1)) not in c.adrs:
                        note(f"ADR-{int(m.group(1)):04d}", doc, i)
            if c.decisions and doc.kind != "log":
                for m in D_ID.finditer(line):
                    n = int(m.group(1))
                    # Ids far past the log are something else (a product
                    # name, a part number), not a decision.
                    if n not in c.decisions and 0 < n <= max_d + 20:
                        note(f"D{n}", doc, i)
            if c.assumptions and doc.kind != "register":
                for m in A_ID.finditer(line):
                    if int(m.group(1)) not in c.assumptions:
                        note(f"A-{int(m.group(1))}", doc, i)

    for key, where in sorted(sites.items(), key=lambda kv: (kv[0].rstrip('0123456789'), int(re.sub(r'\D', '', kv[0])))):
        if key.startswith("ADR"):
            what = "has no file in adr/"
        elif key.startswith("D"):
            what = ("has no entry in journey/decisions-log.md: an unanswered brief, or a "
                    "decision that was never logged")
        else:
            what = "has no row in journey/assumptions-register.md"
        first = where[0].rsplit(":", 1)
        out.append(Finding("REF", first[0], int(first[1]),
                           f"{key} is cited {len(where)} time(s) but {what}", where[:6]))
    return out


def check_reg(c: Corpus) -> list[Finding]:
    reg = c.register
    if not reg:
        return []
    out: list[Finding] = []
    if len(c.register_tables) > 1:
        out.append(Finding("REG", reg.rel, c.register_tables[1],
                           f"{len(c.register_tables)} register tables; the canonical register "
                           f"has one, so an appended row has no right place to land",
                           [f"table at line {n}" for n in c.register_tables][:6]))
    if c.orphan_rows:
        out.append(Finding("REG", reg.rel, c.orphan_rows[0],
                           f"{len(c.orphan_rows)} row(s) sit outside any table, below a line "
                           f"that broke the table off; a renderer shows them as plain text",
                           [f"line {n}" for n in c.orphan_rows][:8]))
    updates = [i + 1 for i, line in enumerate(reg.lines) if re.match(r"#+\s*updates?\b", line, re.I)]
    if updates:
        out.append(Finding("REG", reg.rel, updates[0],
                           f"{len(updates)} 'Update' heading(s); the canonical form records a "
                           f"status change as a status line under the table",
                           [f"line {n}" for n in updates][:6]))

    off_vocab: dict[str, list[str]] = {}
    for row in c.assumptions.values():
        if len(row["dupes"]) > 1:
            out.append(Finding("REG", reg.rel, row["dupes"][1],
                               f"{row['id']} has {len(row['dupes'])} rows",
                               [f"line {n}" for n in row["dupes"]]))
        if row["status"] is not None and not STATUS_VOCAB.match(row["status"]):
            off_vocab.setdefault(row["status"][:40] or "(empty)", []).append(row["id"])
    if off_vocab:
        detail = [f"'{s}': {', '.join(ids[:5])}{' ...' if len(ids) > 5 else ''}"
                  for s, ids in sorted(off_vocab.items(), key=lambda kv: -len(kv[1]))]
        out.append(Finding("REG", reg.rel, None,
                           f"{sum(map(len, off_vocab.values()))} row(s) use a status outside the "
                           f"vocabulary (Open, Partly resolved, Resolved, Resolved by design "
                           f"(test pending), Withdrawn, Superseded by D<n>)", detail[:8]))

    # Canonical status lines: the last one for an id is its current status.
    # Legacy update bullets (`- **A-n: FALSIFIED ...**`) are read the same way,
    # less strictly, and reported as heuristic.
    last: dict[int, tuple[int, str]] = {}
    legacy: dict[int, tuple[int, str]] = {}
    for i, line in enumerate(reg.lines):
        m = re.match(r"\s*-\s*A-(\d+)\s*·\s*([^·]+?)\s*·\s*\d{4}-\d{2}-\d{2}", line)
        if m:
            last[int(m.group(1))] = (i + 1, m.group(2).strip())
            continue
        m = re.match(r"\s*-\s*\*\*A-(\d+)\b(.*)", line)
        if m and CLOSE_WORDS.search(m.group(2)):
            legacy[int(m.group(1))] = (i + 1, strip_md(m.group(2)).lstrip(":( ")[:90])
    for key, (n, status) in sorted(last.items()):
        row = c.assumptions.get(key)
        if not row or row["status"] is None or n < row["line"]:
            continue
        current = STATUS_VOCAB.match(row["status"])
        if not current or current.group(1).lower() != status.lower():
            out.append(Finding("REG", reg.rel, row["line"],
                               f"{row['id']} row says '{row['status'][:40]}', but its last "
                               f"status line (line {n}) says '{status}'"))
    # A migrated register keeps its old updates verbatim in an "Earlier notes"
    # section above the table (journey.py migrate, ADR-023). They are later
    # than the rows they talk about whatever their position in the file.
    earlier = section(reg.lines, re.compile(r"earlier notes", re.IGNORECASE))
    for key, (n, text) in sorted(legacy.items()):
        row = c.assumptions.get(key)
        in_earlier = earlier is not None and earlier[0] < n - 1 < earlier[1]
        if (not row or row["status"] is None
                or (not in_earlier and (key in last or n < row["line"]))
                or not row["status"].lower().startswith("open")):
            continue
        out.append(Finding("REG", reg.rel, row["line"],
                           f"{row['id']} row says '{row['status'][:40]}', but a later update "
                           f"(line {n}) reads: {text}", heuristic=True))
    return out


def check_ko(c: Corpus) -> list[Finding]:
    out: list[Finding] = []
    heading = re.compile(r"knock-on", re.IGNORECASE)
    with_field = []
    for adr in sorted(c.adrs.values(), key=lambda a: a.number):
        span = section(adr.doc.lines, heading)
        if span is None:
            continue
        with_field.append(adr)
        start, end = span
        rows = [r for t in table_rows(adr.doc.lines, start + 1, end) for r in t[1:]]
        rows = [(i, cells) for i, cells in rows if not all(placeholder(x) for x in cells)]
        prose = " ".join(adr.doc.lines[start + 1:end])
        if not rows:
            if not re.search(r"\bnone\b", prose, re.IGNORECASE):
                out.append(Finding("KO", adr.doc.rel, start + 1,
                                   f"{adr.label}: Knock-on changes is empty"))
            continue
        for i, cells in rows:
            target_text, outcome = cells[0], strip_md(cells[-1]).lower()
            ref = f"{adr.doc.rel}:{i + 1}"
            if len(cells) < 2 or placeholder(cells[-1]):
                out.append(Finding("KO", adr.doc.rel, i + 1,
                                   f"{adr.label}: no outcome recorded for "
                                   f"'{strip_md(target_text)[:50]}'"))
                continue
            if re.search(r"\b(todo|pending|not done|later|tbd)\b", untracked(outcome, c)):
                out.append(Finding("KO", adr.doc.rel, i + 1,
                                   f"{adr.label}: '{strip_md(target_text)[:50]}' is recorded as "
                                   f"'{outcome[:70]}'; knock-on changes are made in the same step"))
                continue
            if "ticket" in outcome:
                continue
            target, named = resolve_target(c, adr.doc, target_text)
            if target is None:
                if named:                           # an ID-shaped name that does not exist
                    out.append(Finding("KO", adr.doc.rel, i + 1,
                                       f"{adr.label}: names {named}, and no document by that "
                                       f"name exists", heuristic=True))
                continue
            if target is adr.doc:
                continue
            if "banner" in outcome and not re.search(r"updat|amend|rewr|mark|edit", outcome):
                head = "\n".join(target.lines[: max(target.body_start, 40)])
                if not mentions(head, adr.number):
                    out.append(Finding("KO", adr.doc.rel, i + 1,
                                       f"{adr.label}: says {target.rel} was bannered, but nothing "
                                       f"above its body cites {adr.label}", [ref]))
                continue
            if adr.date:
                changed = c.dates.day(target.path)
                if changed < adr.date:
                    out.append(Finding(
                        "KO", adr.doc.rel, i + 1,
                        f"{adr.label} ({adr.date}): says {target.rel} was '{outcome[:30]}', but "
                        f"it last changed {changed} ({c.dates.source})", [ref]))

    # The field is mandatory from the point a project adopted it: the first ADR
    # number from which at least 80% carry it. Earlier ADRs are not flagged, even
    # when some of them gained the field in a later amendment; flagging every
    # pre-adoption ADR would bury the real items.
    numbered = sorted(c.adrs.values(), key=lambda a: a.number)
    has = [a in with_field for a in numbered]
    adopted = next((k for k in range(len(numbered)) if has[k]
                    and sum(has[k:]) >= 0.8 * (len(numbered) - k)), None)
    if adopted is not None:
        missing = [a for a in numbered[adopted:] if a not in with_field and not a.retired]
        if missing:
            out.append(Finding("KO", "adr/", None,
                               f"{len(missing)} ADR(s) from {numbered[adopted].label} on, where "
                               f"the Knock-on field became routine, have none",
                               [a.doc.rel for a in missing][:12]))
    return out


def mentions(text: str, number: int) -> bool:
    return any(int(m.group(1)) == number for m in ADR_ID.finditer(text))


DOC_ALIASES = (
    ("deployment guide", "deployment"), ("deployment", "deployment"), ("runbook", "runbook"),
    ("configuration manifest", "configuration-manifest"),
    ("config manifest", "configuration-manifest"), ("test strategy", "test-strategy"),
    ("assumptions", "assumptions-register"), ("stressor history", "stressor-iteration-history"),
    ("decisions log", "decisions-log"), ("journey state", "journey-state"), ("hld", "hld"),
)


def resolve_target(c: Corpus, adr_doc: Doc, cell: str) -> tuple[Doc | None, str | None]:
    """The document a Knock-on row names, and the name if it is ID-shaped but unknown.

    Searches the whole cell, not only its start: rows are written as
    "LLD-11 §3", "[2026-10-02] LLD-11 §3a" or "`DEPLOYMENT.md` §2.2".
    """
    live = [d for d in c.docs if "archive" not in d.rel.split("/")[:-1]]
    for link in re.findall(r"\]\(([^)#\s]+)", cell):
        path = (adr_doc.path.parent / link).resolve()
        hit = next((d for d in live if d.path.resolve() == path), None)
        if hit:
            return hit, None
    text = strip_md(re.sub(r"\[([^\]]*)\]\([^)]*\)", r"", cell))
    for name in re.findall(r"[\w./-]+\.md\b", text):
        base = Path(name).name.lower()
        hit = next((d for d in live if d.path.name.lower() == base), None)
        return (hit, None) if hit else (None, Path(name).name)
    m = ADR_ID.search(text)
    if m and m.start() < 3:
        adr = c.adrs.get(int(m.group(1)))
        return (adr.doc, None) if adr else (None, m.group(0))
    for m in re.finditer(r"\b([A-Z]{2,}(?:-[A-Z]+)*-\d+)\b", text):
        token = m.group(1)
        hits = [d for d in live if d.stem.upper() == token or d.stem.upper().startswith(token + "-")]
        if hits:
            return hits[0], None
        if token.split("-")[0] in {"LLD", "HLD", "DECISION"}:
            return None, token
    lowered = text.lower()
    for alias, stem in DOC_ALIASES:
        if re.search(r"\b" + re.escape(alias) + r"\b", lowered):
            hits = [d for d in live if d.stem.lower() == stem or d.stem.lower().startswith(stem + "-")]
            if len(hits) == 1 or (hits and hits[0].stem.lower() == stem):
                return hits[0], None
    for word in re.findall(r"\b[A-Z][A-Z-]{2,}\b", text):
        hits = [d for d in live if d.stem.upper() == word]
        if len(hits) == 1:
            return hits[0], None
    return None, None


AMEND_HEADING = re.compile(r"^#{1,6}\s.*\bamend(?:ed|ment)s?\b", re.IGNORECASE)
# A banner says the body has changed, in whatever words the project uses:
# "AMENDED", "UPDATED", "Current state", "Revised". Only above the body. The
# wider wording counts only in a blockquote, so a `**Updated:** <date>`
# metadata line is not mistaken for one.
AMEND_BANNER = re.compile(
    r"^\s*>\s*\**\s*(?:amended|updated|revised|current state|changed)\b"
    r"|^\s*\**\s*(?:amended|current state)\b", re.IGNORECASE)


def check_am(c: Corpus) -> list[Finding]:
    """Amendments appended after the body with no banner at the top covering them.

    Only a heading that *is* an amendment counts ("## Amendment (date)"). A
    content heading marked inline ("### Retry (amended 2026-05-26)") is the
    fix this check asks for, not the defect. Retired ADRs are skipped: a note
    at the end of a superseded ADR is how it points at its successor.
    """
    out: list[Finding] = []
    retired = {a.doc.rel for a in c.adrs.values() if a.retired}
    for doc in c.by_kind("adr", "descriptive"):
        if doc.rel in retired:
            continue
        top = doc.body_start
        banners = [i for i, line in enumerate(doc.lines[:top]) if AMEND_BANNER.search(line)]
        banner_dates = [to_date(d) for i in banners for d in DATE.findall(doc.lines[i])]
        undated_banner = any(not DATE.search(doc.lines[i]) for i in banners)
        newest_banner = max((d for d in banner_dates if d), default=None)
        footnotes = []
        for i in range(top, len(doc.lines)):
            line = doc.lines[i]
            title = strip_md(line.lstrip("#"))
            if (not AMEND_HEADING.search(line) or not re.match(r"\W*amend", title, re.IGNORECASE)
                    or re.search(r"supersed", line, re.IGNORECASE)):
                continue
            when = to_date(DATE.findall(line)[0]) if DATE.search(line) else None
            if banners and (undated_banner or when is None
                            or (newest_banner and when <= newest_banner)):
                continue                                    # a banner at the top covers it
            footnotes.append((i + 1, title[:70]))
        if footnotes:
            reason = ("no banner at the top" if not banners
                      else f"the newest banner at the top is dated {newest_banner}")
            out.append(Finding(
                "AM", doc.rel, footnotes[0][0],
                f"{len(footnotes)} amendment(s) after the body, and {reason}. Check the body "
                f"for passages that still specify what each one replaces",
                [f"line {n}: {t}" for n, t in footnotes][:8]))
    return out


def check_sup(c: Corpus) -> list[Finding]:
    retired = {n: a for n, a in c.adrs.items() if a.retired}
    out: list[Finding] = []
    for adr in sorted(retired.values(), key=lambda a: a.number):
        if re.match(r"\W*superseded", adr.status, re.IGNORECASE) and not ADR_ID.search(adr.status):
            out.append(Finding("SUP", adr.doc.rel, None,
                               f"{adr.label} is Superseded but its Status names no successor"))
    for doc in c.by_kind("descriptive"):
        head = "\n".join(doc.lines[: doc.body_start])
        if re.search(r"supersed|archived|\bstale\b|historical", head, re.IGNORECASE):
            continue                                    # the document says it is not current
        hits: dict[int, list[int]] = {}
        for i, line in outside_fences(doc.lines):
            if MARKER.search(line):
                continue
            for m in ADR_ID.finditer(line):
                n = int(m.group(1))
                if n in retired:
                    hits.setdefault(n, []).append(i + 1)
        for n, where in sorted(hits.items()):
            adr = retired[n]
            out.append(Finding("SUP", doc.rel, where[0],
                               f"cites {adr.label} ({adr.status[:40]}) on {len(where)} line(s) "
                               f"with nothing marking it as retired",
                               [f"line {w}" for w in where][:8]))
    return out


def check_base(c: Corpus) -> list[Finding]:
    changes = sorted(n for n, d in c.decisions.items() if d["actors"])
    if not changes:
        return []
    out: list[Finding] = []
    stale: dict[str, list[int]] = {}
    unbased = []
    for doc in c.by_kind("matrix"):
        text = doc.text
        m = re.search(r"scoring baseline:?\**\s*:?\s*\**\s*D(\d+)", text, re.IGNORECASE)
        if not m:
            unbased.append(doc.rel)
            continue
        base = int(m.group(1))
        marked = {int(x) for x in re.findall(r"scored pre-D(\d+)", text, re.IGNORECASE)}
        later = [n for n in changes if n > base and n not in marked]
        if later:
            stale[doc.path.name] = later
            out.append(Finding("BASE", doc.rel, text[: m.start()].count("\n") + 1,
                               f"scored at D{base}; " + ", ".join(f"D{n}" for n in later) +
                               f" changed the actor set since, and the matrix is not marked "
                               f"`scored pre-D{later[0]}`"))
    if unbased:
        out.append(Finding("BASE", "stressor-analysis/", None,
                           f"{len(unbased)} matrix file(s) declare no scoring baseline, and the "
                           f"decisions log records actor-set changes", unbased[:8]))
    for doc in c.by_kind("descriptive"):
        for i, line in outside_fences(doc.lines):
            for name, later in stale.items():
                if name in line and "scored pre-" not in line:
                    out.append(Finding("BASE", doc.rel, i + 1,
                                       f"quotes {name}, scored before D{later[0]}, without "
                                       f"the `scored pre-D{later[0]}` qualifier"))
    return out


LABEL_HEADERS = {"#", "id", "stressor", "lens", "class", "category", "type", "description",
                 "source", "tags", "notes", "stressor description"}
TOTAL_HEADER = re.compile(r"^(σ|Σ|sum|total|impact)$", re.IGNORECASE)


def score(cell: str) -> tuple[int, bool] | None:
    """(value, uncertain) for a matrix cell, or None if it is not a score."""
    text = strip_md(cell)
    if text in ("", "·", ".", "-", "–", "0"):
        return 0, False
    if text == "?":
        return 0, True
    m = re.fullmatch(r"(\d+)(\?)?", text)
    if m:
        return int(m.group(1)), bool(m.group(2))
    return None


def check_mx(c: Corpus) -> list[Finding]:
    out: list[Finding] = []
    for doc in c.by_kind("matrix"):
        for table in table_rows(doc.lines):
            header = [strip_md(x) for x in table[0][1]]
            totals = [k for k, h in enumerate(header) if TOTAL_HEADER.match(h)]
            if not totals or len(table) < 2:
                continue
            tcol = totals[-1]
            data = [(i, cells) for i, cells in table[1:] if len(cells) == len(header)]
            body = [(i, cells) for i, cells in data
                    if not re.match(r"(total|σ|Σ|vulnerab)", strip_md(cells[0]), re.IGNORECASE)]
            margin = [(i, cells) for i, cells in data if (i, cells) not in body]
            cols = []
            for k in range(tcol):
                if header[k].lower() in LABEL_HEADERS or not body:
                    continue
                parsed = sum(score(cells[k]) is not None for _, cells in body)
                if parsed / len(body) >= 0.8:
                    cols.append(k)
            if not cols:
                continue
            wrong, severity = [], []
            col_sum = {k: 0 for k in cols}
            for i, cells in body:
                vals = {k: score(cells[k]) for k in cols}
                for k, v in vals.items():
                    if v and v[0] > 1:
                        severity.append(f"line {i + 1}: {strip_md(cells[0])} × {header[k]} = {v[0]}")
                    col_sum[k] += v[0] if v else 0
                total = re.search(r"\d+", strip_md(cells[tcol]))
                got = sum(v[0] for v in vals.values() if v)
                if total and int(total.group()) != got:
                    wrong.append(f"line {i + 1}: {strip_md(cells[0])} cells sum to {got}, "
                                 f"row total says {total.group()}")
            for i, cells in margin:
                for k in cols:
                    stated = re.search(r"\d+", strip_md(cells[k]))
                    if stated and int(stated.group()) != col_sum[k]:
                        wrong.append(f"line {i + 1}: column {header[k]} sums to {col_sum[k]}, "
                                     f"totals row says {stated.group()}")
            if wrong:
                out.append(Finding("MX", doc.rel, table[0][0] + 1,
                                   f"{len(wrong)} total(s) that do not match their cells", wrong[:8]))
            if severity:
                out.append(Finding("MX", doc.rel, table[0][0] + 1,
                                   f"{len(severity)} cell(s) scored above 1; matrix scoring is "
                                   f"binary, and a severity scale lets a stressor be argued down",
                                   severity[:8]))
    return out


ALERT_NAME = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b")
ID_LIKE = re.compile(r"^[A-Z]{1,8}-\d+$")


def check_alert(c: Corpus) -> list[Finding]:
    out: list[Finding] = []
    runbooks = [d for d in c.by_kind("descriptive") if "runbook" in d.stem.lower()]
    defining = "\n".join(d.text for d in c.by_kind("adr", "descriptive")
                         if "runbook" not in d.stem.lower()).lower()
    for doc in runbooks:
        names: dict[str, int] = {}
        for table in table_rows(doc.lines):
            if "alert" not in strip_md(table[0][1][0]).lower():
                continue
            for i, cells in table[1:]:
                cell = strip_md(cells[0])
                coded = [t for t in ALERT_NAME.findall(cell) if not ID_LIKE.match(t)]
                name = coded[0] if coded else cell.split(":")[0].strip()
                if name and len(name) <= 60:
                    names.setdefault(name, i + 1)
        for name, line in names.items():
            if name.lower() not in defining:
                out.append(Finding("ALERT", doc.rel, line,
                                   f"alert '{name}' appears in no ADR or design document; nothing "
                                   f"guarantees it gets built", heuristic=True))
    return out


PLACEHOLDER = re.compile(r"\bTBD\b|\bTODO\b|\bFIXME\b|YYYY-MM-DD|\bXXX\b")
TRACKED = re.compile(r"\b(?:tbd|todo|pending|open)\b[^.;|]{0,25}?\bA-(\d+)\b\)?", re.IGNORECASE)


def untracked(text: str, c: Corpus) -> str:
    """`text` without the gaps it hands to a registered assumption.

    "TBD (A-137)" is an acknowledged gap with an owner in the register, which
    is what check 5 asks for. A bare "TBD" is not.
    """
    return TRACKED.sub(lambda m: "" if int(m.group(1)) in c.assumptions else m.group(0), text)


def check_ph(c: Corpus) -> list[Finding]:
    out: list[Finding] = []
    for doc in c.by_kind("adr", "descriptive"):
        where = [i + 1 for i, line in outside_fences(doc.lines)
                 if PLACEHOLDER.search(untracked(line, c))]
        if where:
            out.append(Finding("PH", doc.rel, where[0],
                               f"{len(where)} line(s) with TBD, TODO or a template placeholder",
                               [f"line {n}" for n in where][:8]))
    return out


def check_pdf(c: Corpus) -> list[Finding]:
    out: list[Finding] = []
    for pdf in sorted(c.root.rglob("*.pdf")):
        if "archive" in pdf.relative_to(c.root).parts:
            continue
        md, inferred = pdf.with_suffix(".md"), False
        if not md.exists():
            # An export renamed on the way out: HLD.md -> HLD-high-level-design.pdf.
            stem = pdf.stem.lower()
            hits = [m for m in pdf.parent.glob("*.md") if stem.startswith(m.stem.lower() + "-")]
            if len(hits) != 1:
                continue
            md, inferred = hits[0], True
        if c.dates.stamp(md) > c.dates.stamp(pdf) + 60:
            rel = pdf.relative_to(c.root).as_posix()
            out.append(Finding("PDF", rel, None,
                               f"older than {md.name} (source {c.dates.day(md)}, export "
                               f"{c.dates.day(pdf)}); whoever is sent the PDF reads the old version",
                               heuristic=inferred))
    return out


RUNNERS = {"REF": check_ref, "REG": check_reg, "KO": check_ko, "AM": check_am,
           "SUP": check_sup, "BASE": check_base, "MX": check_mx, "ALERT": check_alert,
           "PH": check_ph, "PDF": check_pdf}


# --------------------------------------------------------------------------
# Commands


def scan(root: Path, only: list[str], dates: Dates) -> tuple[Corpus, list[Finding]]:
    corpus = Corpus(root, dates)
    findings: list[Finding] = []
    for code in only:
        findings.extend(RUNNERS[code](corpus))
    return corpus, findings


def terms(root: Path, words: list[str], paths: list[Path]) -> list[Finding]:
    """Passages still using a replaced mechanism's terms, with nothing marking them."""
    pattern = re.compile("|".join(re.escape(w) for w in words), re.IGNORECASE)
    if paths:
        docs = [Doc(p, p.as_posix(), "descriptive", read_lines(p)) for p in paths]
    else:
        docs = [d for d in load(root) if d.kind in ("adr", "descriptive")]
    out = []
    for doc in docs:
        top = doc.body_start
        in_amendment = False
        for i, line in outside_fences(doc.lines):
            if line.startswith("#"):
                # An amendment is where the replaced term is meant to appear.
                in_amendment = bool(re.match(r"#+\s+\W*amend", line, re.IGNORECASE))
            if i < top or in_amendment or line.lstrip().startswith(">"):
                continue                                    # header, banners, amendments
            if not pattern.search(line):
                continue
            unmarked = [m.group(0) for m in pattern.finditer(line)
                        if not struck(line, m.start(), m.end())]
            if not unmarked or re.search(r"amended|superseded|\[v\d", line, re.IGNORECASE):
                continue
            out.append(Finding("TERM", doc.rel, i + 1,
                               f"'{unmarked[0]}' with no inline mark: {line.strip()[:110]}"))
    return out


def struck(line: str, start: int, end: int) -> bool:
    for m in re.finditer(r"~~.+?~~", line):
        if m.start() <= start and end <= m.end():
            return True
    return False


def refs(root: Path, ident: str) -> list[Finding]:
    m = re.fullmatch(r"(ADR-|D|A-)(\d+)", ident.strip(), re.IGNORECASE)
    if not m:
        raise UsageError(f"trace: '{ident}' is not an ID (ADR-12, D7 or A-31)")
    prefix, number = m.group(1).upper(), int(m.group(2))
    pattern = {"ADR-": ADR_ID, "D": D_ID, "A-": A_ID}[prefix]
    out = []
    for doc in load(root):
        for i, line in outside_fences(doc.lines):
            if any(int(x.group(1)) == number for x in pattern.finditer(line)):
                marked = "marked" if MARKER.search(line) else "unmarked"
                out.append(Finding("CITE", doc.rel, i + 1,
                                   f"[{doc.kind}, {marked}] {line.strip()[:110]}"))
    return out


# --------------------------------------------------------------------------
# Output


def render(findings: list[Finding], header: list[str], as_json: bool) -> str:
    if as_json:
        return json.dumps({"header": header, "findings": [f.__dict__ for f in findings]},
                          indent=2, ensure_ascii=False)
    lines = list(header)
    if not findings:
        lines.append("\nNothing found. That covers only what trace can see: the formats "
                     "ReStack defines, not whether the documents say the right thing.")
        return "\n".join(lines)
    groups: dict[str, list[Finding]] = {}
    for f in findings:
        groups.setdefault(f.check, []).append(f)
    for code, items in groups.items():
        lines.append(f"\n## {code}: {LABELS.get(code, code.lower())} ({len(items)})")
        for n, f in enumerate(items, 1):
            where = f"{f.path}:{f.line}" if f.line else f.path
            tag = "  [heuristic]" if f.heuristic else ""
            lines.append(f"{code}-{n}  {where}{tag}")
            lines.append(f"        {f.message}")
            for d in f.detail:
                lines.append(f"          - {d}")
    lines.append(f"\n{len(findings)} item(s). A worklist, not a verdict: open each document "
                 f"and confirm before reporting anything.")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")    # cp1252 consoles
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if not argv or argv[0] not in ("scan", "terms", "refs", "-h", "--help"):
        argv = ["scan", *argv]

    parser = argparse.ArgumentParser(prog="trace.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_scan = sub.add_parser("scan", help="run the checks")
    p_scan.add_argument("docs", nargs="?", default="docs")
    p_scan.add_argument("--only", help="comma-separated: " + ",".join(CHECKS))
    p_scan.add_argument("--dates", choices=("auto", "git", "mtime"), default="auto")
    p_terms = sub.add_parser("terms", help="unmarked uses of replaced terms")
    p_terms.add_argument("words", nargs="+")
    p_terms.add_argument("--docs", default="docs")
    p_terms.add_argument("--in", dest="paths", nargs="+", default=[])
    p_refs = sub.add_parser("refs", help="every citation of an ID")
    p_refs.add_argument("ident")
    p_refs.add_argument("--docs", default="docs")
    for p in (p_scan, p_terms, p_refs):
        p.add_argument("--json", action="store_true")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2

    root = Path(args.docs)
    paths = [Path(p) for p in getattr(args, "paths", [])]
    if not paths and not root.is_dir():
        print(f"trace: {root} is not a directory (pass the project's docs folder)", file=sys.stderr)
        return 2
    missing = [p for p in paths if not p.is_file()]
    if missing:
        print(f"trace: no such file: {missing[0]}", file=sys.stderr)
        return 2

    if args.command == "scan":
        only = [x.strip().upper() for x in args.only.split(",")] if args.only else list(CHECKS)
        unknown = [x for x in only if x not in CHECKS]
        if unknown:
            print(f"trace: unknown check {unknown[0]}; choose from {', '.join(CHECKS)}",
                  file=sys.stderr)
            return 2
        try:
            dates = Dates(root, args.dates)
        except UsageError as exc:
            print(exc, file=sys.stderr)
            return 2
        corpus, findings = scan(root, only, dates)
        header = [f"trace {VERSION}: {root.as_posix()}  {len(corpus.adrs)} ADRs, "
                  f"{len(corpus.assumptions)} assumptions, {len(corpus.decisions)} decisions, "
                  f"{len(corpus.by_kind('matrix'))} matrices, "
                  f"{len(corpus.by_kind('descriptive'))} descriptive documents",
                  f"dates: {'git commit times' if corpus.dates.source == 'git' else 'file modification times (not a git work tree)'}"]
    elif args.command == "terms":
        findings = terms(root, args.words, paths)
        header = [f"trace {VERSION} terms: {', '.join(args.words)}"]
    else:
        try:
            findings = refs(root, args.ident)
        except UsageError as exc:
            print(exc, file=sys.stderr)
            return 2
        header = [f"trace {VERSION} refs: {args.ident}"]

    print(render(findings, header, args.json))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
