#!/usr/bin/env python3
"""Restyle a project's ADRs and descriptive documents without changing anything material.

A project written under an older ReStack style keeps it: reflection sections,
capability-transfer framing, metadata shaped by an older template. Restyling
rewords and reshapes such a document to the current style. This script is the
guard that makes that safe (ADR-028): it compares the material content of the
document before and after, refuses a write that changes any of it, lists the
rewordings a script cannot judge for the architect to confirm, and writes the
editorial note itself, so the history says what happened.

Material, compared exactly; a difference refuses the write:
    metadata fields and values, IDs (ADR-12, D7, A-31, S-4, LLD-11), dates,
    figures, code blocks and inline code, link targets, table rows, the
    alternatives considered, struck passages and blockquote banners, and
    earlier editorial notes.
Listed for the architect to confirm; the write waits for --confirmed:
    a changed title, normative words (must, never, not, only, ...) whose count
    changed, names and acronyms lost or added, an ID cited a different number of
    times, a body that shrank by more than 30%.

    restyle.py survey [DOCS]                  what an old style left, per document
    restyle.py compare OLD NEW [--drop H]...  the guard: 0 same, 1 refused, 3 confirm
    restyle.py apply OLD NEW --reshaped "..." [--drop H]... [--confirmed]

`--drop "<heading>"` leaves one section of OLD out of the comparison: a section
the architect agreed to remove. apply names every dropped section in the note.

Standard library only, no network. Exit status: 0 done or nothing to report,
1 refused or items listed, 2 usage error, 3 waiting for the architect.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


def skill_version() -> str:
    """The version in this skill's SKILL.md frontmatter, the one place it is set."""
    try:
        text = (Path(__file__).resolve().parent.parent / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return "unknown"
    m = re.search(r"^version:\s*(\S+)", text, re.MULTILINE)
    return m.group(1) if m else "unknown"


VERSION = skill_version()
SCRATCH = ".restyle"
NOTES_HEADING = "Editorial notes"
SHRINK = 0.7

# Directories that are a record of what happened, or belong to journey.py
# migrate. Restyle leaves them alone.
HISTORY_DIRS = {"journey", "reviews", "stressor-analysis", "discovery"}

ID = re.compile(r"\b([A-Z][A-Z0-9]*)-0*(\d+)([a-z]?)\b")
D_ID = re.compile(r"\bD(\d{1,4})\b")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
FIGURE = re.compile(r"(?<![\d.,])\d+(?:[.,]\d+)*(?:\s?%)?")
LINK = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
URL = re.compile(r"(?<!\()\bhttps?://[^\s)>\]]+")
INLINE_CODE = re.compile(r"`([^`]+)`")
STRUCK = re.compile(r"~~(.+?)~~")
FIELD = re.compile(r"^\s*[-*]?\s*\*\*([^*:\n]{1,40}?):?\*\*:?\s*(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")

NORMATIVE = ("must", "shall", "should", "may", "never", "always", "only", "not", "no",
             "none", "cannot", "required", "mandatory", "forbidden", "prohibited", "except",
             "unless", "without")
CONTRACTIONS = (
    (r"\bcan't\b|\bcan’t\b", "cannot"), (r"\bwon't\b|\bwon’t\b", "will not"),
    (r"\bshan't\b|\bshan’t\b", "shall not"), (r"n't\b|n’t\b", " not"),
)
STRUCTURAL_FIELDS = {"status", "date", "deciders", "technical story", "review date"}

OLD_SECTION = re.compile(
    r"reflection|capability being built|residuality goal|capability transfer|"
    r"learning (?:objectives|outcomes)|questions to (?:ask|consider)|what you(?:'ll| will)? learn",
    re.IGNORECASE)
OLD_PHRASE = re.compile(
    r"capability[- ]transfer|build(?:s|ing)? (?:the |your |their )?capabilit|internali[sz]|"
    r"reflection prompt|you will learn|eventually you (?:do|will)",
    re.IGNORECASE)

ADR_FIELDS = ("Status", "Date", "Deciders", "Reversibility", "Review date")
ADR_SECTIONS = (("Context", r"context"), ("Decision", r"decision\b"),
                ("Consequences", r"consequences"), ("Negative consequences", r"negative"),
                ("Alternatives considered", r"alternativ|options considered|considered options"),
                ("Knock-on changes", r"knock-on"))


class UsageError(Exception):
    """Bad arguments: reported on stderr with exit status 2."""


# --------------------------------------------------------------------------
# Reading


def read(path: Path) -> tuple[list[str], str]:
    raw = path.read_bytes().decode("utf-8-sig", errors="replace")
    newline = "\r\n" if "\r\n" in raw else "\n"
    return raw.splitlines(), newline


def write(path: Path, lines: list[str], newline: str) -> None:
    path.write_bytes((newline.join(lines) + newline).encode("utf-8"))


def strip_md(text: str) -> str:
    """Drop emphasis and code marks, keeping underscores inside identifiers."""
    text = re.sub(r"\*+|`|(?<!\w)_+|_+(?!\w)", "", text)
    return re.sub(r"\s+", " ", text).strip()


def heading_text(text: str) -> str:
    """A heading's words: no emphasis, no leading number, no trailing colon."""
    text = strip_md(text)
    text = re.sub(r"^(?:\d+(?:\.\d+)*\.?|[A-Z]\.)\s+", "", text)
    return text.rstrip(":").strip().lower()


def body_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if line.startswith("## "):
            return i
    return min(len(lines), 5)


def header_end(lines: list[str]) -> int:
    """Where the metadata stops: the first level-2 heading that is not itself a
    metadata field (an older template wrote `## Status` and `## Date` as sections)."""
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m and len(m.group(1)) == 2 and heading_text(m.group(2)) not in STRUCTURAL_FIELDS:
            return i
    return body_start(lines)


def metadata(lines: list[str]) -> dict[str, str]:
    """Field name -> value, from `**Field:** value` lines and field-named sections."""
    fields: dict[str, str] = {}
    current = None
    for line in lines[:header_end(lines)]:
        m = HEADING.match(line)
        if m:
            name = heading_text(m.group(2))
            current = name if len(m.group(1)) == 2 and name in STRUCTURAL_FIELDS else None
            continue
        m = FIELD.match(line)
        if m:
            fields[m.group(1).strip().lower()] = strip_md(m.group(2))
        elif current and line.strip():
            value = strip_md(line)
            fields[current] = f"{fields[current]} {value}" if current in fields else value
    return fields


def sections(lines: list[str]) -> list[tuple[int, int, int, str]]:
    """(start, end, level, text) for every heading outside a code fence."""
    heads, fenced = [], False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else HEADING.match(line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    out = []
    for k, (i, level, text) in enumerate(heads):
        end = next((j for j, lv, _ in heads[k + 1:] if lv <= level), len(lines))
        out.append((i, end, level, text))
    return out


def find_section(lines: list[str], wanted: str) -> tuple[int, int] | None:
    key = heading_text(wanted)
    for start, end, _, text in sections(lines):
        if heading_text(text) == key:
            return start, end
    return None


def without(lines: list[str], spans: list[tuple[int, int]]) -> list[str]:
    drop = set()
    for start, end in spans:
        drop.update(range(start, end))
    return [line for i, line in enumerate(lines) if i not in drop]


# --------------------------------------------------------------------------
# The material fingerprint


@dataclass
class Print:
    title: str = ""
    fields: dict[str, str] = field(default_factory=dict)
    ids: collections.Counter = field(default_factory=collections.Counter)
    dates: set[str] = field(default_factory=set)
    figures: set[str] = field(default_factory=set)
    code: collections.Counter = field(default_factory=collections.Counter)
    links: set[str] = field(default_factory=set)
    rows: collections.Counter = field(default_factory=collections.Counter)
    alternatives: set[str] = field(default_factory=set)
    marks: collections.Counter = field(default_factory=collections.Counter)
    notes: list[str] = field(default_factory=list)
    normative: collections.Counter = field(default_factory=collections.Counter)
    sentences: dict[str, list[str]] = field(default_factory=dict)
    terms: set[str] = field(default_factory=set)
    vocab: set[str] = field(default_factory=set)
    headings: dict[str, set[str]] = field(default_factory=dict)
    words: int = 0


COMMON = {"because", "before", "between", "should", "through", "without", "within", "rather",
          "during", "against", "already", "another", "anything", "around", "become", "becomes",
          "behind", "beyond", "cannot", "different", "either", "enough", "everything", "further",
          "however", "itself", "little", "neither", "nothing", "others", "perhaps", "really",
          "something", "therefore", "though", "together", "towards", "whether", "whichever",
          "whose", "yourself", "always", "almost", "across", "after", "where", "which", "while"}


def content_words(text: str) -> set[str]:
    """Distinct long words, lower case: what a reword keeps if it keeps the meaning."""
    text = INLINE_CODE.sub(" ", LINK.sub("]", text))
    return {w for w in (x.lower() for x in re.findall(r"[A-Za-z][A-Za-z-]{5,}", text))
            if w not in COMMON}


def expand(text: str) -> str:
    for pattern, repl in CONTRACTIONS:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text


def fingerprint(lines: list[str]) -> Print:
    p = Print()
    notes = find_section(lines, NOTES_HEADING)
    if notes:
        p.notes = [line.strip() for line in lines[notes[0] + 1:notes[1]] if line.strip()]
        lines = without(lines, [notes])

    p.title = next((strip_md(t) for _, _, lv, t in sections(lines) if lv == 1), "")
    p.fields = metadata(lines)

    alt = next(((s, e) for s, e, lv, t in sections(lines)
                if lv <= 3 and re.search(ADR_SECTIONS[4][1], heading_text(t))), None)
    if alt:
        for s, e, lv, t in sections(lines[alt[0]:alt[1]]):
            if s > 0:
                p.alternatives.add(heading_text(t))

    prose, fenced, block = [], False, []
    for line in lines:
        if line.lstrip().startswith("```"):
            if fenced:
                p.code["\n".join(block)] += 1
                block = []
            fenced = not fenced
            continue
        if fenced:
            block.append(line.rstrip())
            continue
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [strip_md(c) for c in stripped.strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                p.rows[" | ".join(cells)] += 1
        if stripped.startswith(">") and strip_md(stripped.lstrip("> ")):
            p.marks["> " + strip_md(stripped.lstrip("> "))] += 1
        for m in STRUCK.finditer(line):
            p.marks["~~" + strip_md(m.group(1))] += 1
        for m in INLINE_CODE.finditer(line):
            p.code["`" + m.group(1)] += 1
        prose.append(line)
    if block:
        p.code["\n".join(block)] += 1

    text = "\n".join(prose)
    p.links = set(LINK.findall(text)) | set(URL.findall(text))
    text = URL.sub(" ", LINK.sub("]", INLINE_CODE.sub(" ", text)))
    for m in ID.finditer(text):
        p.ids[f"{m.group(1)}-{int(m.group(2))}{m.group(3)}"] += 1
    for m in D_ID.finditer(text):
        p.ids[f"D{int(m.group(1))}"] += 1
    p.dates = set(DATE.findall(text))
    bare = DATE.sub(" ", D_ID.sub(" ", ID.sub(" ", text)))
    bare = "\n".join(re.sub(r"^\s*#{1,6}\s+\d+(?:\.\d+)*[.)]?\s+|^\s*(?:[-*]\s+)?\d+[.)]\s+", "", x)
                     for x in bare.splitlines())       # list and heading numbering
    p.figures = {re.sub(r"\s", "", m.group(0)).replace(",", "") for m in FIGURE.finditer(bare)}

    words_only = expand(strip_md(re.sub(r"^#+\s|^\s*>|\|", " ", text, flags=re.MULTILINE)))
    tokens = re.findall(r"[A-Za-z][A-Za-z'’-]*", words_only)
    p.words = len(tokens)
    for sentence in re.split(r"(?<=[.!?:;])\s+|\n\s*\n", expand(text)):
        found = {w.lower() for w in re.findall(r"[A-Za-z]+", sentence)} & set(NORMATIVE)
        for w in found:
            p.normative[w] += len(re.findall(rf"\b{w}\b", sentence, re.IGNORECASE))
            p.sentences.setdefault(w, []).append(strip_md(sentence)[:160])
    p.vocab = content_words(text)
    # Per section, the words found nowhere else in the document: if they reach
    # NEW, the section moved; if they do not, it went.
    for start, end, level, heading in sections(lines):
        if level >= 2 and heading_text(heading) not in STRUCTURAL_FIELDS:
            rest = content_words("\n".join(lines[:start] + lines[end:]))
            p.headings[heading_text(heading)] = content_words("\n".join(lines[start + 1:end])) - rest
    p.terms = set()
    for line in text.splitlines():
        if HEADING.match(line):
            continue                                    # heading case is style
        p.terms |= names(strip_md(re.sub(r"^\s*(?:#+|>|[-*]|\d+[.)])\s*", "", line)))
    return p


STOP_CAPS = {"I", "A", "An", "The", "This", "That", "These", "Those", "It", "We", "Our",
             "If", "When", "Where", "Which", "What", "Who", "Why", "How", "For", "In", "On",
             "At", "By", "To", "And", "But", "Or", "Not", "No", "Yes", "All", "Any", "Each",
             "Every", "Some", "One", "Two", "Three", "There", "Then", "So", "As", "Also", "See"}


def names(text: str) -> set[str]:
    """The names a reword must keep: acronyms, CamelCase, snake_case, code-ish
    words, and capitalised words that do not start a sentence."""
    out = set()
    for m in re.finditer(r"[A-Za-z][\w’'-]*", text):
        word = m.group(0).strip("'’-")
        if len(word) < 2:
            continue
        before = text[:m.start()].rstrip()            # one line: its start is a sentence start
        sentence_start = not before or before[-1] in ".!?:;|>-*#(\"“"
        if (re.fullmatch(r"[A-Z]{2,}[A-Z0-9]*s?", word) or re.search(r"[a-z][A-Z]", word)
                or "_" in word or re.search(r"\d", word)):
            out.add(word)
        elif word[0].isupper() and not sentence_start and word not in STOP_CAPS:
            out.add(word)
    return out


# --------------------------------------------------------------------------
# Compare


@dataclass
class Verdict:
    refused: list[str] = field(default_factory=list)
    confirm: list[str] = field(default_factory=list)

    @property
    def status(self) -> int:
        return 1 if self.refused else 3 if self.confirm else 0


def show(items, limit: int = 6) -> str:
    items = sorted(items)
    text = ", ".join(f"'{x}'" if " " in x or not x else x for x in items[:limit])
    return text + (f" (+{len(items) - limit} more)" if len(items) > limit else "")


def counter_diff(label: str, old: collections.Counter, new: collections.Counter, out: list[str]):
    lost, added = old - new, new - old
    if lost:
        out.append(f"{label} missing from NEW: {show(lost.elements(), 4)}")
    if added:
        out.append(f"{label} not in OLD: {show(added.elements(), 4)}")


def compare(old_lines: list[str], new_lines: list[str], drops: list[str]) -> Verdict:
    v = Verdict()
    spans = []
    for name in drops:
        span = find_section(old_lines, name)
        if span is None:
            raise UsageError(f"restyle: --drop '{name}': OLD has no heading by that name")
        spans.append(span)
    old, new = fingerprint(without(old_lines, spans)), fingerprint(new_lines)

    # Refusals: anything a reader acts on.
    for key in sorted(old.fields.keys() | new.fields.keys()):
        a, b = old.fields.get(key), new.fields.get(key)
        if a is None:
            v.refused.append(f"field '{key}' added ('{b[:60]}'): a missing field is a gap for "
                             f"/restack-adr update, never filled by a restyle")
        elif b is None:
            v.refused.append(f"field '{key}' ('{a[:60]}') is missing from NEW")
        elif a != b:
            v.refused.append(f"field '{key}' changed: '{a[:60]}' -> '{b[:60]}'")
    for label, a, b in (("ID", set(old.ids), set(new.ids)), ("date", old.dates, new.dates),
                        ("figure", old.figures, new.figures), ("link", old.links, new.links),
                        ("alternative", old.alternatives, new.alternatives)):
        if a - b:
            v.refused.append(f"{label}(s) missing from NEW: {show(a - b)}")
        if b - a:
            v.refused.append(f"{label}(s) not in OLD: {show(b - a)}")
    counter_diff("code", old.code, new.code, v.refused)
    counter_diff("table row(s)", old.rows, new.rows, v.refused)
    counter_diff("struck passage(s) or banner(s)", old.marks, new.marks, v.refused)
    if new.notes[:len(old.notes)] != old.notes:
        v.refused.append("an earlier editorial note was changed or removed")
    elif len(new.notes) > len(old.notes):
        v.refused.append("NEW already has a new editorial note; apply writes it, with --reshaped")

    # A section gone from NEW without --drop: removed if the words only it used
    # went with it, renamed or merged if they are still there.
    for heading, own in old.headings.items():
        if heading in new.headings:
            continue
        if not own:
            v.confirm.append(f"section '{heading}' has no heading of that name in NEW, and no "
                             f"words of its own to tell renamed from removed")
            continue
        kept = len(own & new.vocab) / len(own)
        if kept < 0.5:
            v.refused.append(f"section '{heading}' is not in NEW, nor are {len(own - new.vocab)} "
                             f"of the {len(own)} words only it used; a section is removed only "
                             f"when the architect names it with --drop")
        else:
            v.confirm.append(f"section '{heading}' has no heading of that name in NEW "
                             f"(renamed or merged: {len(own & new.vocab)} of the {len(own)} words "
                             f"only it used are in NEW)")

    # Confirmations: rewordings a script cannot judge.
    if old.title != new.title:
        v.confirm.append(f"title: '{old.title}' -> '{new.title}'")
    for key in sorted(set(old.ids) & set(new.ids)):
        if old.ids[key] != new.ids[key]:
            v.confirm.append(f"{key} cited {old.ids[key]} time(s) in OLD, {new.ids[key]} in NEW")
    for word in NORMATIVE:
        a, b = old.normative[word], new.normative[word]
        if a == b:
            continue
        gone = [s for s in old.sentences.get(word, []) if s not in new.sentences.get(word, [])]
        came = [s for s in new.sentences.get(word, []) if s not in old.sentences.get(word, [])]
        item = f"'{word}' {a} -> {b}"
        item += "".join(f"\n      OLD: {s}" for s in gone[:3])
        item += "".join(f"\n      NEW: {s}" for s in came[:3])
        v.confirm.append(item)
    if old.terms - new.terms:
        v.confirm.append(f"name(s) no longer in NEW: {show(old.terms - new.terms, 10)}")
    if new.terms - old.terms:
        v.confirm.append(f"name(s) new in NEW: {show(new.terms - old.terms, 10)}")
    if old.vocab - new.vocab:
        v.confirm.append(f"word(s) no longer in NEW: {show(old.vocab - new.vocab, 12)}")
    if old.words and new.words < SHRINK * old.words:
        v.confirm.append(f"body shrank from {old.words} to {new.words} words "
                         f"({100 - round(100 * new.words / old.words)}%); check nothing was dropped "
                         f"that was not named with --drop")
    return v


def render_verdict(old: Path, new: Path, drops: list[str], v: Verdict) -> list[str]:
    out = [f"restyle {VERSION} compare: {old.as_posix()} -> {new.as_posix()}"]
    if drops:
        out.append("dropped from the comparison: " + "; ".join(f"'{d}'" for d in drops))
    for r in v.refused:
        out.append(f"  REFUSED: {r}")
    for c in v.confirm:
        out.append(f"  CONFIRM: {c}")
    if v.refused:
        out.append("Material content differs: nothing may be written. Restore it in NEW, or "
                   "take the change to /restack-adr update as a decision.")
    elif v.confirm:
        out.append("Material content unchanged. Each CONFIRM is the architect's call: apply "
                   "waits for --confirmed.")
    else:
        out.append("Material content unchanged, nothing to confirm.")
    return out


# --------------------------------------------------------------------------
# Apply


def in_clean_git(path: Path) -> bool:
    try:
        done = subprocess.run(["git", "-C", str(path.parent), "status", "--porcelain", "--",
                               path.name], capture_output=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0 and not done.stdout.strip()


def with_note(lines: list[str], note: str) -> list[str]:
    lines = list(lines)
    while lines and not lines[-1].strip():
        lines.pop()
    span = find_section(lines, NOTES_HEADING)
    if span:
        at = span[1]
        while at > span[0] + 1 and not lines[at - 1].strip():
            at -= 1
        return lines[:at] + [note] + lines[at:]
    return lines + ["", f"## {NOTES_HEADING}", "", note]


def apply(old: Path, new: Path, drops: list[str], reshaped: str, confirmed: bool,
          today: str) -> tuple[list[str], int]:
    old_lines, newline = read(old)
    new_lines, _ = read(new)
    v = compare(old_lines, new_lines, drops)
    report = render_verdict(old, new, drops, v)
    if v.refused:
        return report + ["Not written."], 1
    if v.confirm and not confirmed:
        return report + ["Not written: put each CONFIRM to the architect, then rerun with "
                         "--confirmed."], 3
    dropped = "; ".join(f'"{d}"' for d in drops) if drops else "nothing"
    note = (f"- {today} · restyled, wording only · reshaped: {reshaped.strip()} · "
            f"dropped: {dropped} · checked by restyle.py {VERSION}")
    if not in_clean_git(old):
        backup = old.parent / SCRATCH / f"{old.stem}.pre-restyle-{today}{old.suffix}"
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(old, backup)
        report.append(f"backup: {backup.as_posix()}")
    write(old, with_note(new_lines, note), newline)
    report.append(f"written: {old.as_posix()}")
    report.append(f"note: {note}")
    if new.resolve().parent.name == SCRATCH or SCRATCH in new.resolve().parts:
        new.unlink()
        try:
            new.parent.rmdir()                      # only if empty
        except OSError:
            pass
    return report, 0


# --------------------------------------------------------------------------
# Survey


def classify(rel: str) -> str | None:
    parts = rel.split("/")
    if any(p.startswith(".") for p in parts) or "archive" in parts[:-1]:
        return None
    if parts[0] in HISTORY_DIRS:
        return None
    if parts[0] == "adr" and re.match(r"ADR-\d", parts[-1], re.IGNORECASE):
        return "adr"
    return "descriptive"


def survey_doc(path: Path, rel: str, kind: str) -> dict:
    lines, _ = read(path)
    top = header_end(lines)
    item = {"path": rel, "kind": kind, "restyled": None, "retired": False,
            "sections": [], "phrases": [], "gaps": [], "elsewhere": []}
    notes = find_section(lines, NOTES_HEADING)
    if notes:
        done = [DATE.search(x) for x in lines[notes[0]:notes[1]] if "restyled, wording only" in x]
        if done and done[-1]:
            item["restyled"] = done[-1].group(0)
    fields = metadata(lines)
    status = fields.get("status", "")
    item["retired"] = kind == "adr" and bool(re.match(r"\W*(superseded|deprecated)", status, re.I))

    heads = sections(lines)
    for start, _, _, text in heads:
        if OLD_SECTION.search(text):
            item["sections"].append(f"line {start + 1}: {strip_md(text)}")
    fenced = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and not HEADING.match(line) and OLD_PHRASE.search(line):
            item["phrases"].append(f"line {i + 1}: {strip_md(line)[:100]}")

    if kind == "adr" and not item["retired"]:
        for name in ADR_FIELDS:
            if name.lower() not in fields:
                item["gaps"].append(f"field {name}")
        titles = [heading_text(t) for _, _, _, t in heads]
        for name, pattern in ADR_SECTIONS:
            if not any(re.search(pattern, t) for t in titles):
                item["gaps"].append(f"section {name}")
    for start, _, _, text in heads:
        if start > top and re.match(r"\W*amend", strip_md(text), re.IGNORECASE):
            banner = any(re.match(r"\s*>\s*\**\s*(amended|updated|revised|current state)",
                                  x, re.IGNORECASE) for x in lines[:top])
            if not banner:
                item["elsewhere"].append(f"line {start + 1}: amendment after the body with no "
                                         f"banner at the top")
    return item


def survey(root: Path) -> list[dict]:
    out = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        kind = classify(rel)
        if kind:
            out.append(survey_doc(path, rel, kind))
    return out


def render_survey(root: Path, items: list[dict]) -> tuple[list[str], int]:
    adrs = [i for i in items if i["kind"] == "adr"]
    lines = [f"restyle {VERSION} survey: {root.as_posix()}  {len(adrs)} ADRs, "
             f"{len(items) - len(adrs)} descriptive documents (journey, reviews, discovery, "
             f"stressor analysis and archives are out of scope)"]
    listed = 0
    for i in items:
        if not (i["sections"] or i["phrases"] or i["gaps"] or i["elsewhere"]):
            continue
        listed += 1
        tags = []
        if i["retired"]:
            tags.append("retired: history, restyled only if named")
        if i["restyled"]:
            tags.append(f"restyled {i['restyled']}")
        lines.append(f"\n{i['path']}" + (f"  [{'; '.join(tags)}]" if tags else ""))
        for s in i["sections"]:
            lines.append(f"    old-style section   {s}")
        for s in i["phrases"][:5]:
            lines.append(f"    old-style wording   {s}")
        if len(i["phrases"]) > 5:
            lines.append(f"    old-style wording   (+{len(i['phrases']) - 5} more lines)")
        if i["gaps"]:
            lines.append(f"    gap, not restyle's  {', '.join(i['gaps'])}: /restack-adr update")
        for s in i["elsewhere"]:
            lines.append(f"    not restyle's       {s}: the owning skill's update")
    if not listed:
        lines.append("\nNothing an old style left that this script recognises. It sees section "
                     "names and phrases, not tone: read a sample before calling the set current.")
    else:
        lines.append(f"\n{listed} document(s) listed. Old-style sections and wording are what "
                     f"restyle reshapes; gaps and amendments belong to the owning skill.")
    return lines, 1 if listed else 0


# --------------------------------------------------------------------------
# CLI


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")    # cp1252 consoles
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    parser = argparse.ArgumentParser(prog="restyle.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p_survey = sub.add_parser("survey", help="what an old style left, per document")
    p_survey.add_argument("docs", nargs="?", default="docs")
    p_cmp = sub.add_parser("compare", help="the guard: is the material content unchanged?")
    p_apply = sub.add_parser("apply", help="compare, then write NEW over OLD with the note")
    for p in (p_cmp, p_apply):
        p.add_argument("old")
        p.add_argument("new")
        p.add_argument("--drop", action="append", default=[], metavar="HEADING")
    p_apply.add_argument("--reshaped", required=True, help="what was reshaped, for the note")
    p_apply.add_argument("--confirmed", action="store_true")
    p_apply.add_argument("--date", default=dt.date.today().isoformat())
    for p in (p_survey, p_cmp):
        p.add_argument("--json", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2

    try:
        if args.command == "survey":
            root = Path(args.docs)
            if not root.is_dir():
                raise UsageError(f"restyle: {root} is not a directory (pass the project's docs folder)")
            items = survey(root)
            lines, code = render_survey(root, items)
            print(json.dumps(items, indent=2, ensure_ascii=False) if args.json else "\n".join(lines))
            return code
        old, new = Path(args.old), Path(args.new)
        for p in (old, new):
            if not p.is_file():
                raise UsageError(f"restyle: no such file: {p}")
        if old.resolve() == new.resolve():
            raise UsageError("restyle: OLD and NEW are the same file; write the draft elsewhere")
        if args.command == "compare":
            v = compare(read(old)[0], read(new)[0], args.drop)
            if args.json:
                print(json.dumps({"refused": v.refused, "confirm": v.confirm}, indent=2,
                                 ensure_ascii=False))
            else:
                print("\n".join(render_verdict(old, new, args.drop, v)))
            return v.status
        if not args.reshaped.strip():
            raise UsageError("restyle: --reshaped says what was reshaped, for the editorial note")
        if not DATE.fullmatch(args.date):
            raise UsageError(f"restyle: --date {args.date} is not YYYY-MM-DD")
        report, code = apply(old, new, args.drop, args.reshaped, args.confirmed, args.date)
        print("\n".join(report))
        return code
    except UsageError as exc:
        print(exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
