#!/usr/bin/env python3
"""Write a ReStack journey's files in their canonical shape, and migrate old ones.

The journey-state contract (scripts/preamble/journey-state.md) defines one
shape for each of three files so that any agent can append to them in one
line. This script is that line. It owns the bookkeeping the contract asks for:
the next A-<n> and D<n>, where a row or an entry goes, the status vocabulary,
and keeping a register row and its status lines in step.

    journey.py check                         is each file canonical?
    journey.py assume add "<belief>" --source S --validates V --depends D
    journey.py assume status A-12 "Partly resolved" --why "..."
    journey.py decision next                 the number the next brief takes
    journey.py decision open "<question>" [--gate brief]
    journey.py decision answer D7 --answer "..." --rationale "..." --actors no
    journey.py history add --command "/restack-x y" --outcome "..." [--decision D7]
    journey.py migrate [register|log|state|all] [--write]

Every command takes --docs (default: docs) and --date (default: today).

Writes refuse a file that is not canonical, and say why. `migrate` converts it:
structure only, never a status or a decision, and only after checking that
nothing material changed (every word, every ID, every status). It is a dry
run unless --write is given (ADR-023).

Standard library only, no network. Exit status: 0 done, 1 refused, 2 usage.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REGISTER = "journey/assumptions-register.md"
LOG = "journey/decisions-log.md"
STATE = "journey/journey-state.md"

COLUMNS = ["ID", "Assumption", "Source", "Validates it", "Depends on it", "Status", "Status date"]
HEADER = "| " + " | ".join(COLUMNS) + " |"
SEPARATOR = "|" + "---|" * len(COLUMNS)

VOCAB = ["Open", "Partly resolved", "Resolved by design (test pending)", "Resolved", "Withdrawn"]
STATUS_TERM = re.compile(
    r"^(Open|Partly resolved|Resolved by design \(test pending\)|Resolved|Withdrawn|"
    r"Superseded by D\d+)(?![\w-])", re.IGNORECASE)
DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
A_ROW = re.compile(r"^\s*\|\s*\**\s*A-(\d+)\s*\**\s*\|")
STATUS_LINE = re.compile(r"^\s*-\s*A-(\d+)\s*·\s*([^·]+?)\s*·\s*(\d{4}-\d{2}-\d{2}|—)\s*·?\s*(.*)$")
D_HEADING = re.compile(r"^## D(\d+) · (\d{4}-\d{2}-\d{2}) · (.*)$")
LEGACY_D_HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2}):\s*D(\d+)\b\s*[,:]?\s*(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


class Refused(Exception):
    """The file is not in a shape this command can write to (exit 1)."""


class UsageError(Exception):
    """Bad arguments (exit 2)."""


# --------------------------------------------------------------------------
# Files


def read(path: Path) -> tuple[list[str], str]:
    raw = path.read_bytes().decode("utf-8-sig")
    newline = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n").split("\n"), newline


def write(path: Path, lines: list[str], newline: str = "\n") -> None:
    """Atomic: a crash leaves the old file or the new one, never half of each."""
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text.replace("\n", newline))
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def cell(text: str) -> str:
    """User text made safe for one table cell."""
    return " ".join(text.split()).replace("|", "\\|")


def strip_md(text: str) -> str:
    return re.sub(r"\*+|`|(?<!\w)_+|_+(?!\w)", "", text).strip()


def split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def is_separator(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c) and line.strip().startswith("|")


# --------------------------------------------------------------------------
# Assumptions register


def register_shape(lines: list[str]) -> dict:
    """Where the canonical register's parts are, and what is not canonical."""
    tables, orphans, updates = [], [], []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"#+\s*updates?\b", line, re.IGNORECASE):
            updates.append(i)
        if line.strip().startswith("|") and not is_separator(line):
            start = i
            while i < len(lines) and lines[i].strip().startswith("|"):
                i += 1
            header = [strip_md(c).lower() for c in split_row(lines[start])]
            if header and header[0] == "id":
                tables.append((start, i))
            elif A_ROW.match(lines[start]):
                orphans.extend(range(start, i))
            continue
        i += 1
    problems = []
    if len(tables) != 1:
        problems.append(f"{len(tables)} register tables; the canonical register has exactly one")
    elif [strip_md(c) for c in split_row(lines[tables[0][0]])] != COLUMNS:
        problems.append("the register table's columns are not the canonical seven: " + " | ".join(COLUMNS))
    if orphans:
        problems.append(f"{len(orphans)} row(s) outside any table (line {orphans[0] + 1} first)")
    if updates:
        problems.append(f"{len(updates)} 'Update' heading(s) (line {updates[0] + 1} first)")
    if len(tables) == 1:
        end = tables[0][1]
        for j in range(end, len(lines)):
            text = lines[j].strip()
            if text and text != "## Status lines" and not STATUS_LINE.match(lines[j]):
                problems.append(f"line {j + 1} follows the table and is not a status line")
                break
    return {"tables": tables, "problems": problems}


def register_rows(lines: list[str], table: tuple[int, int]) -> dict[int, int]:
    """Row number -> line index, for the one canonical table."""
    return {int(A_ROW.match(lines[k]).group(1)): k
            for k in range(table[0], table[1]) if A_ROW.match(lines[k])}


def new_register(date: str) -> list[str]:
    return [
        "# Assumptions Register",
        "",
        "Beliefs the design relies on that have not been verified. One table for the",
        "whole journey; a status change is a status line under `## Status lines`.",
        f"Created {date} by `journey.py`.",
        "",
        HEADER,
        SEPARATOR,
        "",
        "## Status lines",
        "",
    ]


def id_width(lines: list[str]) -> int:
    """Zero-padding the file already uses (A-01 style), so new IDs match."""
    return 2 if any(re.match(r"^\s*\|\s*\**\s*A-0\d", line) for line in lines) else 1


def assume_add(root: Path, text: str, source: str, validates: str, depends: str,
               date: str, ident: str | None) -> str:
    path = root / REGISTER
    if path.exists():
        lines, newline = read(path)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines, newline = new_register(date), "\n"
    shape = register_shape(lines)
    if shape["problems"]:
        raise Refused(f"{REGISTER} is not canonical: " + "; ".join(shape["problems"]) +
                      ". Run `journey.py migrate register` (a dry run) to see the conversion.")
    table = shape["tables"][0]
    rows = register_rows(lines, table)
    if ident:
        m = re.fullmatch(r"A-(\d+)", ident)
        if not m:
            raise UsageError(f"--id must look like A-12, not {ident}")
        number = int(m.group(1))
        if number in rows:
            raise Refused(f"A-{number} already has a row (line {rows[number] + 1})")
        label = ident
    else:
        number = max(rows, default=0) + 1
        label = f"A-{number:0{id_width(lines)}d}"
    row = "| " + " | ".join([label, cell(text), cell(source), cell(validates), cell(depends),
                             "Open", date]) + " |"
    lines.insert(table[1], row)
    lines = append_status_line(lines, label, "Open", date, "registered")
    write(path, lines, newline)
    return label


def append_status_line(lines: list[str], label: str, status: str, date: str, why: str) -> list[str]:
    while lines and not lines[-1].strip():
        lines.pop()
    if not any(line.strip() == "## Status lines" for line in lines):
        lines += ["", "## Status lines", ""]
    elif lines[-1].strip() == "## Status lines":
        lines.append("")
    lines.append(f"- {label} · {status} · {date} · {' '.join(why.split())}")
    return lines


def assume_status(root: Path, ident: str, status: str, why: str, date: str) -> str:
    path = root / REGISTER
    if not path.exists():
        raise Refused(f"{REGISTER} does not exist")
    term = STATUS_TERM.fullmatch(status.strip())
    if not term:
        raise UsageError(f"'{status}' is not a status. Use one of: " + ", ".join(VOCAB) +
                         ", Superseded by D<n>")
    status = canonical_term(term.group(1))
    if not why.strip():
        raise UsageError("--why is required: a status line records what settled it")
    lines, newline = read(path)
    shape = register_shape(lines)
    if shape["problems"]:
        raise Refused(f"{REGISTER} is not canonical: " + "; ".join(shape["problems"]))
    m = re.fullmatch(r"A-(\d+)", ident.strip())
    if not m:
        raise UsageError(f"'{ident}' is not an assumption ID (A-12)")
    rows = register_rows(lines, shape["tables"][0])
    k = rows.get(int(m.group(1)))
    if k is None:
        raise Refused(f"{ident} has no row in the register")
    cells = split_row(lines[k])
    cells[5], cells[6] = status, date
    lines[k] = "| " + " | ".join(cells) + " |"
    label = strip_md(cells[0])
    lines = append_status_line(lines, label, status, date, why)
    write(path, lines, newline)
    return f"{label} · {status} · {date}"


def canonical_term(term: str) -> str:
    for word in VOCAB:
        if term.lower() == word.lower():
            return word
    m = re.fullmatch(r"superseded by d(\d+)", term, re.IGNORECASE)
    return f"Superseded by D{m.group(1)}" if m else term


# --------------------------------------------------------------------------
# Decisions log


def new_log() -> list[str]:
    return [
        "# Decisions Log",
        "",
        "Every gate passed and every brief, numbered journey-wide. A brief takes its",
        "number when it is issued (`journey.py decision open`), and its answer is",
        "filled in when it is given. Numbers are never reused. Append-only: a",
        "decision that reverses an earlier one is a new entry naming it.",
        "",
    ]


def log_shape(lines: list[str]) -> dict:
    numbers: dict[int, list[int]] = collections.defaultdict(list)
    problems = []
    for i, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        if LEGACY_D_HEADING.match(line):
            problems.append(f"line {i + 1} is a decision heading in the old shape "
                            f"(`## <date>: D<n>, ...` instead of `## D<n> · <date> · ...`)")
        for m in re.finditer(r"\bD(\d+)\b", line):
            numbers[int(m.group(1))].append(i)
    canonical = {}
    for i, line in enumerate(lines):
        m = D_HEADING.match(line)
        if m:
            n = int(m.group(1))
            if n in canonical:
                problems.append(f"D{n} has two entries (lines {canonical[n] + 1} and {i + 1})")
            canonical.setdefault(n, i)
    return {"problems": problems, "entries": canonical, "mentioned": numbers}


def next_decision(lines: list[str]) -> int:
    """One past every D<n> in any heading, so a number in an event entry is not reused."""
    mentioned = log_shape(lines)["mentioned"]
    return max(mentioned, default=0) + 1


def decision_open(root: Path, question: str, gate: str, date: str) -> str:
    path = root / LOG
    if path.exists():
        lines, newline = read(path)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines, newline = new_log(), "\n"
    shape = log_shape(lines)
    if shape["problems"]:
        raise Refused(f"{LOG} is not canonical: " + "; ".join(shape["problems"][:3]) +
                      ". Run `journey.py migrate log` (a dry run) to see the conversion.")
    n = next_decision(lines)
    while lines and not lines[-1].strip():
        lines.pop()
    lines += ["", f"## D{n} · {date} · {' '.join(question.split())}", "",
              f"- **Gate:** {gate}",
              "- **Answer:** (open)",
              "- **Rationale:** —",
              "- **Changes the actor set:** —",
              "- **Supersedes:** —"]
    write(path, lines, newline)
    return f"D{n}"


def decision_answer(root: Path, ident: str, answer: str, rationale: str, actors: str,
                    supersedes: str | None) -> str:
    path = root / LOG
    if not path.exists():
        raise Refused(f"{LOG} does not exist; open the decision first")
    m = re.fullmatch(r"D(\d+)", ident.strip(), re.IGNORECASE)
    if not m:
        raise UsageError(f"'{ident}' is not a decision ID (D7)")
    n = int(m.group(1))
    if not answer.strip() or not rationale.strip():
        raise UsageError("--answer and --rationale are both required")
    actors = actors.strip()
    if actors.lower() == "no":
        actors_text = "no"
    elif re.match(r"yes\b", actors, re.IGNORECASE):
        detail = actors[3:].lstrip(" :").strip()
        if not detail:
            raise UsageError("--actors yes needs the change: --actors \"yes: added <actor>\"")
        actors_text = f"yes: {detail}. Matrices scored before this are `scored pre-D{n}`"
    else:
        raise UsageError("--actors is `no` or `yes: <what changed>`")
    lines, newline = read(path)
    shape = log_shape(lines)
    if shape["problems"]:
        raise Refused(f"{LOG} is not canonical: " + "; ".join(shape["problems"][:3]))
    start = shape["entries"].get(n)
    if start is None:
        raise Refused(f"D{n} has no entry; `decision open` it first so it has its number")
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    fields = {"Answer": " ".join(answer.split()), "Rationale": " ".join(rationale.split()),
              "Changes the actor set": actors_text,
              "Supersedes": supersedes.strip() if supersedes else "—"}
    seen = set()
    for j in range(start + 1, end):
        f = re.match(r"^- \*\*(Answer|Rationale|Changes the actor set|Supersedes):\*\*\s*(.*)$", lines[j])
        if not f:
            continue
        if f.group(1) == "Answer" and f.group(2).strip() != "(open)":
            raise Refused(f"D{n} is already answered ({f.group(2).strip()[:60]}). "
                          f"A decision that changes it is a new entry that supersedes it.")
        lines[j] = f"- **{f.group(1)}:** {fields[f.group(1)]}"
        seen.add(f.group(1))
    if "Answer" not in seen:
        raise Refused(f"D{n}'s entry has no `- **Answer:** (open)` line to fill")
    write(path, lines, newline)
    return f"D{n} answered"


# --------------------------------------------------------------------------
# Journey state


def history_span(lines: list[str]) -> tuple[int, int] | None:
    for i, line in enumerate(lines):
        if re.match(r"^##\s+journey history\b", line, re.IGNORECASE):
            end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
            return i, end
    return None


def state_shape(lines: list[str]) -> dict:
    problems, notes = [], []
    span = history_span(lines)
    if span is None:
        problems.append("no `## Journey History` section")
    else:
        start, end = span
        if end != len(lines):
            problems.append(f"`## Journey History` (line {start + 1}) is not the last section")
        if any(lines[j].strip().startswith("|") for j in range(start, end)):
            problems.append("the journey history is a table; the canonical form is one list line per entry")
    text = "\n".join(lines)
    for field in ("Implementation status", "Design boundary"):
        if not re.search(rf"\*\*{field}:\*\*", text):
            notes.append(f"no `**{field}:**` field (the contract asks for it before any probe)")
    return {"problems": problems, "notes": notes}


def history_add(root: Path, command: str, outcome: str, decision: str | None, date: str) -> str:
    path = root / STATE
    if not path.exists():
        raise Refused(f"{STATE} does not exist. `/restack-journey start` creates it from the template.")
    lines, newline = read(path)
    shape = state_shape(lines)
    if shape["problems"]:
        raise Refused(f"{STATE} is not canonical: " + "; ".join(shape["problems"]) +
                      ". Run `journey.py migrate state` (a dry run) to see the conversion.")
    if decision and not re.fullmatch(r"D\d+(\.\w+)?", decision):
        raise UsageError(f"--decision must look like D7, not {decision}")
    command = command.strip()
    if command.startswith("/") and not command.startswith("`"):
        command = f"`{command}`"
    entry = f"- {date} · {command} · {' '.join(outcome.split())}"
    if decision:
        entry += f" · {decision}"
    while lines and not lines[-1].strip():
        lines.pop()
    lines.append(entry)
    write(path, lines, newline)
    return entry


# --------------------------------------------------------------------------
# Migration


def words(text: str) -> collections.Counter:
    return collections.Counter(re.findall(r"[^\W_]+", text.lower()))


def lost_words(old: str, new: str) -> list[str]:
    """Words the old text has more often than the new one. Empty means nothing was lost."""
    before, after = words(old), words(new)
    return sorted(w for w, n in before.items() if after[w] < n)


def section_date(lines: list[str], index: int) -> str | None:
    for j in range(index, -1, -1):
        if HEADING.match(lines[j]) or lines[j].startswith("**Update"):
            m = DATE.search(lines[j])
            if m:
                return m.group(1)
    return None


def map_column(header: str) -> str:
    h = strip_md(header).lower()
    if h == "id":
        return "id"
    if "status date" in h:
        return "date"
    if "status" in h:
        return "status"
    if "validat" in h or "settle" in h:
        return "validates"
    if "depend" in h:
        return "depends"
    if h.startswith("source") or "current source" in h:
        return "source"
    if any(w in h for w in ("assumption", "unknown", "question", "gap", "belief", "hazard")):
        return "assumption"
    return "extra"


def migrate_register(lines: list[str], today: str) -> tuple[list[str], list[str], list[str]]:
    """(new lines, what was done, what needs a judgement)."""
    done, judge = [], []
    title_end = 1 if lines and lines[0].startswith("# ") else 0
    first_block = next((i for i in range(title_end, len(lines))
                        if HEADING.match(lines[i]) or lines[i].strip().startswith("|")), len(lines))
    intro = lines[title_end:first_block]
    rows: dict[int, dict] = {}
    order: list[int] = []
    positional: list[str] = []
    off_vocab: list[str] = []
    notes: list[str] = []
    status_lines: list[str] = []
    header_cols: list[str] | None = None
    tables = 0
    i = first_block
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and not is_separator(line):
            start = i
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not is_separator(lines[i]):
                    block.append((i, lines[i]))
                i += 1
            head = [strip_md(c) for c in split_row(block[0][1])]
            if head and head[0].lower() == "id":
                header_cols, body = head, block[1:]
                tables += 1
                label = "Table"
            elif A_ROW.match(block[0][1]):
                body, label = block, "Rows"
            else:
                notes.extend(l for _, l in block)
                continue
            moved = []
            for k, row_line in body:
                cells = split_row(row_line)
                m = A_ROW.match(row_line)
                if not m:
                    notes.append(row_line)
                    continue
                number = int(m.group(1))
                if number in rows:
                    judge.append(f"A-{number} has two rows (lines {rows[number]['line'] + 1} and "
                                 f"{k + 1}); merge them by hand, then migrate")
                    continue
                # Rows without a header of their own take the last one seen,
                # if the column count matches; otherwise they map by position.
                cols = header_cols if header_cols and len(header_cols) == len(cells) else None
                if cols is None and len(cells) == len(COLUMNS):
                    cols = COLUMNS                  # a row already in the canonical shape
                slots = collections.defaultdict(list)
                for c, value in enumerate(cells):
                    if not value.strip():
                        continue
                    if cols:
                        kind = map_column(cols[c])
                    else:
                        kind = ("id" if c == 0 else "status" if c == len(cells) - 1
                                else "assumption" if c == 1 else "extra")
                    if kind == "extra":         # kept, labelled, in Source
                        name = cols[c] if cols else f"Column {c + 1}"
                        slots["source"].append(f"{name}: {value}")
                    else:
                        slots[kind].append(value)
                if not cols and len(cells) > 2:
                    positional.append(strip_md(cells[0]))
                rows[number] = {"line": k, "cells": slots, "date": section_date(lines, k)}
                order.append(number)
                moved.append(strip_md(cells[0]))
            if moved:
                what = (f"{label} moved to the register below"
                        + (f" (columns: {' · '.join(head)})" if label == "Table" else "")
                        + f": {', '.join(moved)}.")
                notes.append(f"*({what})*")
            continue
        sl = STATUS_LINE.match(line)
        if sl:
            status_lines.append(line.rstrip())
        else:
            h = HEADING.match(line)
            notes.append(f"**{h.group(2).strip()}**" if h else line)
        i += 1

    if any("two rows" in j for j in judge):
        return lines, done, judge

    out_rows, made_lines = [], []
    for number in sorted(rows):
        slots = rows[number]["cells"]
        label = (slots["id"] or [f"A-{number}"])[0]
        label = strip_md(label)
        status_text = " ".join(slots["status"]).strip()
        term = STATUS_TERM.match(strip_md(status_text))
        date = (slots["date"] or [None])[0] or rows[number]["date"] or "—"
        if term:
            status = canonical_term(term.group(1))
            rest = strip_md(status_text)[len(term.group(1)):].lstrip(" :,;-–—").strip()
            if rest:
                made_lines.append(f"- {label} · {status} · {date} · {rest} (moved from the row's "
                                  f"status cell by migration {today})")
        else:
            status = status_text or "—"
            off_vocab.append(f"{label}: '{strip_md(status_text)[:50]}'")
        out_rows.append("| " + " | ".join([
            label, cell(" ".join(slots["assumption"])), cell("; ".join(slots["source"])),
            cell(" ".join(slots["validates"])), cell(" ".join(slots["depends"])),
            cell(status), date]) + " |")

    # What the notes say that the rows may not: the last note per ID wins.
    note_status: dict[int, str] = {}
    note_only: dict[int, str] = {}
    for m in re.finditer(r"^\s*-\s*\*\*(A-(\d+))\b(.*)$", "\n".join(notes), re.MULTILINE):
        label, n, text = m.group(1), int(m.group(2)), m.group(3)
        if re.search(r"FALSIFIED|resolved|withdrawn|closed|superseded|confirmed", text, re.I):
            note_status[n] = f"{label} '{strip_md(text).lstrip(':( ')[:60]}'"
        if re.search(r"\(new", text, re.I) and n not in rows:
            note_only[n] = label
    if off_vocab:
        judge.append(f"{len(off_vocab)} status(es) outside the vocabulary; record each with "
                     f"`assume status A-<n> \"<status>\" --why \"...\"`: " + "; ".join(off_vocab))
    if note_status:
        judge.append(f"{len(note_status)} row(s) whose earlier notes read as a status change; "
                     f"if the row is out of date, record it with `assume status`: "
                     + "; ".join(t for _, t in sorted(note_status.items())))
    if note_only:
        judge.append(f"{len(note_only)} assumption(s) defined only in an earlier note, with no "
                     f"row; give each one with `assume add --id A-<n> ...`: "
                     + ", ".join(label for _, label in sorted(note_only.items())))
    if positional:
        judge.append(f"{len(positional)} row(s) had no header and were mapped by position; "
                     f"check their Source column: " + ", ".join(positional))

    new = lines[:title_end] + intro
    while new and not new[-1].strip():
        new.pop()
    new += ["",
            f"> **Migrated {today} by `journey.py migrate`:** {len(rows)} rows from "
            f"{tables} table(s) are in the one register table below. The earlier notes are "
            f"kept verbatim, headings flattened, above it. Nothing was removed.",
            "", "## Earlier notes (verbatim, before migration)", ""]
    new += [n for n in notes]
    while new and not new[-1].strip():
        new.pop()
    new += ["", "## Register", "", HEADER, SEPARATOR] + out_rows + ["", "## Status lines", ""]
    new += made_lines + status_lines
    done.append(f"{len(rows)} rows from {tables} table(s) and "
                f"{sum(1 for n in notes if n.startswith('*(Rows'))} stray row group(s) into one table")
    done.append(f"{len(made_lines)} status cell remainder(s) moved to status lines; "
                f"{len(status_lines)} existing status line(s) moved under `## Status lines`")
    return new, done, judge


def migrate_log(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    done, judge = [], []
    new = list(lines)
    converted = 0
    for i, line in enumerate(new):
        m = LEGACY_D_HEADING.match(line)
        if m:
            date, n, rest = m.groups()
            new[i] = f"## D{n} · {date} · {rest.strip() or 'decision'}"
            converted += 1
    if converted:
        done.append(f"{converted} decision heading(s) put in the `## D<n> · <date> · ...` shape")
    shape = log_shape(new)
    judge += shape["problems"]
    missing = []
    for n, start in sorted(shape["entries"].items()):
        end = next((j for j in range(start + 1, len(new)) if new[j].startswith("## ")), len(new))
        if not any(re.search(r"changes the actor set", new[j], re.I) for j in range(start, end)):
            missing.append(f"D{n}")
    if missing:
        judge.append(f"{len(missing)} decision(s) do not record whether they changed the actor "
                     f"set, which trace's BASE check needs: {', '.join(missing[:12])}"
                     f"{' ...' if len(missing) > 12 else ''}")
    events = sum(1 for line in new if line.startswith("## ") and not D_HEADING.match(line))
    if events:
        done.append(f"{events} entry/entries without a D-number kept as they are (events, not briefs)")
    return new, done, judge


def migrate_state(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    done, judge = [], []
    span = history_span(lines)
    if span is None:
        new = list(lines)
        while new and not new[-1].strip():
            new.pop()
        new += ["", "## Journey History", ""]
        done.append("added an empty `## Journey History` section at the end")
    else:
        start, end = span
        heading, section = lines[start], lines[start + 1:end]
        rest = lines[:start] + lines[end:]
        body, converted, header_seen = [], 0, False
        for line in section:
            text = line.strip()
            if text.startswith("|"):
                if is_separator(line):
                    continue
                cells = split_row(line)
                if not header_seen and converted == 0 and not DATE.search(cells[0]):
                    # The table's header row: kept as a sentence, so its words survive.
                    body.append(f"Moved from a table ({' · '.join(strip_md(c) for c in cells)}).")
                    header_seen = True
                    continue
                body.append("- " + " · ".join(cells))
                converted += 1
            elif text != "---":                  # a rule before the next section
                body.append(line)
        while rest and (not rest[-1].strip() or rest[-1].strip() == "---"):
            rest.pop()
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
        new = rest + ["", heading, ""] + body
        if converted:
            done.append(f"{converted} history table row(s) turned into list lines")
        if end != len(lines):
            done.append("`## Journey History` moved to the end of the file")
    judge += state_shape(new)["notes"]
    return new, done, judge


MIGRATORS = {"register": (REGISTER, migrate_register), "log": (LOG, migrate_log),
             "state": (STATE, migrate_state)}
SHAPES = {"register": register_shape, "log": log_shape, "state": state_shape}


def material_check(kind: str, old: list[str], new: list[str]) -> list[str]:
    """Reasons the migration would change material content. Empty means safe to write."""
    reasons = []
    lost = lost_words("\n".join(old), "\n".join(new))
    if lost:
        reasons.append(f"{len(lost)} word(s) would be lost: {', '.join(lost[:10])}")
    if kind == "register":
        before = {int(m.group(1)) for line in old for m in [A_ROW.match(line)] if m}
        after = {int(m.group(1)) for line in new for m in [A_ROW.match(line)] if m}
        if before - after:
            reasons.append("rows would disappear: " + ", ".join(f"A-{n}" for n in sorted(before - after)))
    if kind == "log":
        before = re.findall(r"\bD\d+\b", "\n".join(old))
        after = re.findall(r"\bD\d+\b", "\n".join(new))
        if collections.Counter(before) - collections.Counter(after):
            reasons.append("decision references would change")
    return reasons


def in_clean_git(path: Path) -> bool:
    try:
        top = subprocess.run(["git", "-C", str(path.parent), "status", "--porcelain", "--", path.name],
                             capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return False
    return top.returncode == 0 and not top.stdout.strip()


def migrate(root: Path, which: str, do_write: bool, today: str) -> tuple[list[str], bool]:
    report, ok = [], True
    kinds = list(MIGRATORS) if which == "all" else [which]
    for kind in kinds:
        rel, fn = MIGRATORS[kind]
        path = root / rel
        if not path.exists():
            report.append(f"{rel}: does not exist, nothing to migrate")
            continue
        lines, newline = read(path)
        shape = SHAPES[kind](lines)
        if not shape["problems"]:
            report.append(f"{rel}: already canonical")
            for note in shape.get("notes", []):
                report.append(f"  judgement: {note}")
            continue
        new, done, judge = fn(lines, today) if kind == "register" else fn(lines)
        reasons = material_check(kind, lines, new)
        blocked = [j for j in judge if "two rows" in j]
        remaining = SHAPES[kind](new)["problems"] if not blocked else []
        report.append(f"{rel}: not canonical ({'; '.join(shape['problems'][:3])})")
        for d in done:
            report.append(f"  will do: {d}")
        for j in judge:
            report.append(f"  judgement: {j}")
        if reasons or blocked or remaining:
            ok = False
            for r in reasons:
                report.append(f"  REFUSED: {r}")
            for r in remaining:
                report.append(f"  REFUSED: the result would still not be canonical: {r}")
            if blocked:
                report.append("  REFUSED: resolve the duplicate rows first")
            continue
        report.append("  material check: every word, ID and status survives")
        if do_write:
            if not in_clean_git(path):
                backup = path.with_name(f"{path.stem}.pre-migration-{today}{path.suffix}")
                shutil.copy2(path, backup)
                report.append(f"  backup: {backup.relative_to(root).as_posix()}")
            write(path, new, newline)
            report.append("  written")
        else:
            report.append("  dry run: nothing written (add --write)")
    return report, ok


def check(root: Path) -> tuple[list[str], bool]:
    report, ok = [], True
    for kind, (rel, _) in MIGRATORS.items():
        path = root / rel
        if not path.exists():
            report.append(f"{rel}: absent")
            continue
        shape = SHAPES[kind](read(path)[0])
        if shape["problems"]:
            ok = False
            report.append(f"{rel}: not canonical")
            report += [f"  - {p}" for p in shape["problems"]]
        else:
            report.append(f"{rel}: canonical")
        report += [f"  note: {n}" for n in shape.get("notes", [])]
    return report, ok


# --------------------------------------------------------------------------
# CLI


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")    # cp1252 consoles
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")    # refusals quote file text
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(prog="journey.py", description=__doc__.split("\n\n")[0])
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--docs", default="docs")
    common.add_argument("--date", default=dt.date.today().isoformat())
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", parents=[common])

    p_assume = sub.add_parser("assume").add_subparsers(dest="action", required=True)
    a_add = p_assume.add_parser("add", parents=[common])
    a_add.add_argument("text")
    a_add.add_argument("--source", required=True)
    a_add.add_argument("--validates", required=True)
    a_add.add_argument("--depends", required=True)
    a_add.add_argument("--id", dest="ident")
    a_status = p_assume.add_parser("status", parents=[common])
    a_status.add_argument("ident")
    a_status.add_argument("status")
    a_status.add_argument("--why", required=True)

    p_dec = sub.add_parser("decision").add_subparsers(dest="action", required=True)
    p_dec.add_parser("next", parents=[common])
    d_open = p_dec.add_parser("open", parents=[common])
    d_open.add_argument("question")
    d_open.add_argument("--gate", default="brief")
    d_ans = p_dec.add_parser("answer", parents=[common])
    d_ans.add_argument("ident")
    d_ans.add_argument("--answer", required=True)
    d_ans.add_argument("--rationale", required=True)
    d_ans.add_argument("--actors", required=True)
    d_ans.add_argument("--supersedes")

    p_hist = sub.add_parser("history").add_subparsers(dest="action", required=True)
    h_add = p_hist.add_parser("add", parents=[common])
    h_add.add_argument("--command", dest="cmd", required=True)
    h_add.add_argument("--outcome", required=True)
    h_add.add_argument("--decision")

    p_mig = sub.add_parser("migrate", parents=[common])
    p_mig.add_argument("which", nargs="?", default="all", choices=["all", *MIGRATORS])
    p_mig.add_argument("--write", action="store_true")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2

    root = Path(args.docs)
    if not DATE.fullmatch(args.date):
        print(f"journey: --date must be YYYY-MM-DD, not {args.date}", file=sys.stderr)
        return 2
    try:
        if args.command == "check":
            report, ok = check(root)
            print("\n".join(report))
            return 0 if ok else 1
        if args.command == "migrate":
            report, ok = migrate(root, args.which, args.write, args.date)
            print("\n".join(report))
            return 0 if ok else 1
        if args.command == "assume" and args.action == "add":
            print(assume_add(root, args.text, args.source, args.validates, args.depends,
                             args.date, args.ident))
        elif args.command == "assume":
            print(assume_status(root, args.ident, args.status, args.why, args.date))
        elif args.command == "decision" and args.action == "next":
            path = root / LOG
            print(f"D{next_decision(read(path)[0]) if path.exists() else 1}")
        elif args.command == "decision" and args.action == "open":
            print(decision_open(root, args.question, args.gate, args.date))
        elif args.command == "decision":
            print(decision_answer(root, args.ident, args.answer, args.rationale, args.actors,
                                  args.supersedes))
        else:
            print(history_add(root, args.cmd, args.outcome, args.decision, args.date))
    except UsageError as exc:
        print(f"journey: {exc}", file=sys.stderr)
        return 2
    except Refused as exc:
        print(f"journey: refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
