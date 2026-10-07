#!/usr/bin/env python3
"""Tests for skills/restack-journey/scripts/journey.py (ADR-023).

Two synthetic journeys in tests/fixtures/journey/: `canonical`, in the shapes
the templates define, and `legacy`, in the older shapes a long engagement
leaves behind (several register tables, "Update" headings, rows stranded
outside a table, date-first decision headings, a history table mid-file).
Every case runs against a scratch copy.

The writes are tested for where they land and for what they refuse. The
migration is tested for what it converts, what it leaves for judgement, and
above all for losing nothing: a migration that drops a word has changed the
record, and the material check exists to stop exactly that.

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shells import posix_env, posix_shell  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "restack-journey" / "scripts" / "journey.py"
TRACE = ROOT / "skills" / "restack-trace" / "scripts" / "trace.py"
FRAGMENT = ROOT / "scripts" / "preamble" / "journey-files.md"
FIXTURES = ROOT / "tests" / "fixtures" / "journey"
DATE = "2026-04-20"


def run(*args: str, script: Path = SCRIPT) -> tuple[int, str]:
    done = subprocess.run([sys.executable, "-B", str(script), *args], capture_output=True, timeout=60)
    return done.returncode, (done.stdout + done.stderr).decode("utf-8")


def load_module():
    previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec = importlib.util.spec_from_file_location("journey", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


class ModFixtureCase(unittest.TestCase):
    """The `band` and `lived` journeys are what the restack-view mod's tests read
    (ADR-029). `lived` is in the shape a long engagement leaves: a sentence for
    the terrain, a qualified phase label, dated Current Position subsections.

    Each has to be canonical by journey.py's own check, or the mod would be
    tested against a shape journey.py never writes.
    """

    def test_mod_fixtures_are_canonical(self):
        for name in ("band", "lived"):
            with self.subTest(fixture=name):
                code, out = run("check", "--docs", str(FIXTURES / name), "--date", DATE)
                self.assertEqual(code, 0, out)
                self.assertNotIn("not canonical", out)


class JourneyCase(unittest.TestCase):
    fixture = "canonical"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="restack-journey-"))
        self.docs = self.tmp / "docs"
        shutil.copytree(FIXTURES / self.fixture, self.docs)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def j(self, *args: str) -> tuple[int, str]:
        return run(*args, "--docs", str(self.docs), "--date", DATE)

    def text(self, name: str) -> str:
        return (self.docs / "journey" / name).read_text(encoding="utf-8")


class Register(JourneyCase):

    def test_add_takes_the_next_id_and_lands_in_the_table(self):
        code, out = self.j("assume", "add", "Depots open at 06:00", "--source", "depot manager",
                           "--validates", "opening-hours list", "--depends", "ADR-0005")
        self.assertEqual((code, out.strip()), (0, "A-3"))
        reg = self.text("assumptions-register.md")
        lines = reg.splitlines()
        row = lines.index(next(l for l in lines if l.startswith("| A-3 ")))
        self.assertTrue(lines[row - 1].startswith("| A-2 "))          # end of the table
        self.assertTrue(reg.rstrip().endswith("- A-3 · Open · 2026-04-20 · registered"))

    def test_add_follows_zero_padding(self):
        reg = self.docs / "journey" / "assumptions-register.md"
        reg.write_text(reg.read_text(encoding="utf-8").replace("| A-1 ", "| A-01 ")
                       .replace("| A-2 ", "| A-02 "), encoding="utf-8")
        self.assertEqual(self.j("assume", "add", "x", "--source", "s", "--validates", "v",
                                "--depends", "d")[1].strip(), "A-03")

    def test_add_escapes_pipes_and_newlines(self):
        self.j("assume", "add", "a | b\nc", "--source", "s", "--validates", "v", "--depends", "d")
        self.assertIn("| A-3 | a \\| b c |", self.text("assumptions-register.md"))

    def test_add_with_a_taken_id_is_refused(self):
        code, out = self.j("assume", "add", "x", "--source", "s", "--validates", "v",
                           "--depends", "d", "--id", "A-2")
        self.assertEqual(code, 1, out)
        self.assertIn("already has a row", out)

    def test_add_creates_a_missing_register(self):
        (self.docs / "journey" / "assumptions-register.md").unlink()
        self.assertEqual(self.j("assume", "add", "x", "--source", "s", "--validates", "v",
                                "--depends", "d")[1].strip(), "A-1")
        self.assertEqual(self.j("check")[0], 0)

    def test_status_updates_the_row_and_appends_a_line(self):
        code, out = self.j("assume", "status", "A-1", "partly resolved", "--why", "two depots measured")
        self.assertEqual(code, 0, out)
        reg = self.text("assumptions-register.md")
        self.assertIn("| ADR-0002 | Partly resolved | 2026-04-20 |", reg)
        self.assertTrue(reg.rstrip().endswith("- A-1 · Partly resolved · 2026-04-20 · two depots measured"))

    def test_status_outside_the_vocabulary_is_a_usage_error(self):
        self.assertEqual(self.j("assume", "status", "A-1", "FALSIFIED", "--why", "x")[0], 2)

    def test_status_of_an_unknown_id_is_refused(self):
        self.assertEqual(self.j("assume", "status", "A-9", "Resolved", "--why", "x")[0], 1)

    def test_superseded_by_a_decision_is_a_status(self):
        code, out = self.j("assume", "status", "A-2", "superseded by d2", "--why", "reframed")
        self.assertEqual(code, 0, out)
        self.assertIn("· Superseded by D2 ·", self.text("assumptions-register.md"))

    def drift_a1(self):
        """A-1's last status line says Resolved; its row still says Open."""
        reg = self.docs / "journey" / "assumptions-register.md"
        reg.write_text(reg.read_text(encoding="utf-8") + "- A-1 · Resolved · 2026-04-12 · logs\n",
                       encoding="utf-8")

    def test_sync_takes_status_and_date_from_the_last_line(self):
        self.drift_a1()
        before = self.text("assumptions-register.md").count("\n- A-")
        code, out = self.j("assume", "sync", "A-1")
        self.assertEqual((code, out.strip()), (0, "A-1: Open -> Resolved (2026-04-12)"))
        reg = self.text("assumptions-register.md")
        self.assertIn("| ADR-0002 | Resolved | 2026-04-12 |", reg)
        self.assertEqual(reg.count("\n- A-"), before)                 # no new status line

    def test_sync_all_only_touches_drifted_rows(self):
        self.drift_a1()
        code, out = self.j("assume", "sync", "--all")
        self.assertEqual(out.strip(), "A-1: Open -> Resolved (2026-04-12)")
        self.assertEqual(self.j("assume", "sync", "--all")[1].strip(), "already in step")
        code, out = run(str(self.docs), "--only", "REG", script=TRACE)
        self.assertEqual(code, 0, out)

    def test_sync_needs_one_id_or_all(self):
        self.assertEqual(self.j("assume", "sync")[0], 2)
        self.assertEqual(self.j("assume", "sync", "A-1", "--all")[0], 2)

    def test_sync_without_a_status_line_is_refused(self):
        self.j("assume", "add", "x", "--source", "s", "--validates", "v", "--depends", "d")
        reg = self.docs / "journey" / "assumptions-register.md"
        reg.write_text(reg.read_text(encoding="utf-8").replace("- A-3 · Open · 2026-04-20 · registered\n", ""),
                       encoding="utf-8")
        code, out = self.j("assume", "sync", "A-3")
        self.assertEqual(code, 1)
        self.assertIn("no status line", out)

    def test_trace_agrees_the_result_is_consistent(self):
        self.j("assume", "add", "x", "--source", "s", "--validates", "v", "--depends", "d")
        self.j("assume", "status", "A-1", "Resolved", "--why", "logs")
        code, out = run(str(self.docs), "--only", "REG", script=TRACE)
        self.assertEqual(code, 0, out)


class Decisions(JourneyCase):

    def test_next_is_past_every_number_in_any_heading(self):
        self.assertEqual(self.j("decision", "next")[1].strip(), "D3")

    def test_open_then_answer(self):
        code, out = self.j("decision", "open", "Shard the event store by depot?", "--gate", "approach")
        self.assertEqual((code, out.strip()), (0, "D3"))
        log = self.text("decisions-log.md")
        self.assertIn("## D3 · 2026-04-20 · Shard the event store by depot?", log)
        self.assertIn("- **Answer:** (open)", log)
        code, out = self.j("decision", "answer", "D3", "--answer", "B: one store",
                           "--rationale", "depots share couriers", "--actors", "yes: added the shard router",
                           "--assumptions", "none")
        self.assertEqual(code, 0, out)
        log = self.text("decisions-log.md")
        self.assertIn("- **Answer:** B: one store", log)
        self.assertIn("- **Changes the actor set:** yes: added the shard router. Matrices scored "
                      "before this are `scored pre-D3`", log)
        self.assertNotIn("(open)", log)

    def test_an_open_brief_keeps_its_number(self):
        self.j("decision", "open", "first question")
        self.assertEqual(self.j("decision", "open", "second question")[1].strip(), "D4")

    def test_answering_twice_is_refused(self):
        code, out = self.j("decision", "answer", "D2", "--answer", "x", "--rationale", "y", "--actors", "no",
                           "--assumptions", "none")
        self.assertEqual(code, 1)
        self.assertIn("already answered", out)

    def test_answering_an_unopened_decision_is_refused(self):
        code, out = self.j("decision", "answer", "D9", "--answer", "x", "--rationale", "y", "--actors", "no",
                           "--assumptions", "none")
        self.assertEqual(code, 1)
        self.assertIn("decision open", out)

    def test_actors_yes_needs_the_change(self):
        self.j("decision", "open", "q")
        self.assertEqual(self.j("decision", "answer", "D3", "--answer", "x", "--rationale", "y",
                                "--actors", "yes", "--assumptions", "none")[0], 2)

    def test_note_records_a_missing_actor_set_as_recorded_later(self):
        log = self.docs / "journey" / "decisions-log.md"
        log.write_text(log.read_text(encoding="utf-8").replace(
            "- **Changes the actor set:** no\n- **Supersedes:** —\n\n## 2026-03-15", "- **Supersedes:** —\n\n## 2026-03-15"),
            encoding="utf-8")
        code, out = self.j("decision", "note", "D1", "--actors", "yes: added the depot gateway")
        self.assertEqual(code, 0, out)
        entry = self.text("decisions-log.md").split("## 2026-03-15")[0]
        self.assertIn("- **Changes the actor set:** yes: added the depot gateway. Matrices scored before "
                      "this are `scored pre-D1` *(recorded 2026-04-20; not stated when decided)*", entry)

    def test_note_refuses_when_already_recorded(self):
        code, out = self.j("decision", "note", "D2", "--actors", "yes: x")
        self.assertEqual(code, 1)
        self.assertIn("already records changes the actor set", out)

    def test_note_refuses_an_open_decision(self):
        self.j("decision", "open", "q")
        code, out = self.j("decision", "note", "D3", "--actors", "no")
        self.assertEqual(code, 1)
        self.assertIn("still open", out)

    def test_open_creates_a_missing_log(self):
        (self.docs / "journey" / "decisions-log.md").unlink()
        self.assertEqual(self.j("decision", "open", "q")[1].strip(), "D1")


class History(JourneyCase):

    def test_add_appends_at_the_end(self):
        code, out = self.j("history", "add", "--command", "/restack-journey iterate",
                           "--outcome", "proceed: impact 2", "--decision", "D3")
        self.assertEqual(code, 0, out)
        self.assertTrue(self.text("journey-state.md").rstrip().endswith(
            "- 2026-04-20 · `/restack-journey iterate` · proceed: impact 2 · D3"))

    def test_msys_rewritten_command_is_put_back(self):
        for given in ("C:/Program Files/Git/restack-journey migrate", "restack-journey migrate",
                      "D:\\tools\\git\\restack-journey migrate"):
            with self.subTest(given=given):
                self.j("history", "add", "--command", given, "--outcome", "o")
                self.assertTrue(self.text("journey-state.md").rstrip().endswith(
                    "- 2026-04-20 · `/restack-journey migrate` · o"))

    def test_missing_state_is_refused(self):
        (self.docs / "journey" / "journey-state.md").unlink()
        code, out = self.j("history", "add", "--command", "/x", "--outcome", "y")
        self.assertEqual(code, 1)
        self.assertIn("/restack-journey start", out)


class Legacy(JourneyCase):
    fixture = "legacy"

    def test_check_names_what_is_not_canonical(self):
        code, out = self.j("check")
        self.assertEqual(code, 1)
        self.assertIn("2 register tables", out)
        self.assertIn("2 row(s) outside any table", out)
        self.assertIn("decision heading in the old shape", out)
        self.assertIn("journey history is a table", out)

    def test_every_write_is_refused_with_the_migration_hint(self):
        for args in (("assume", "add", "x", "--source", "s", "--validates", "v", "--depends", "d"),
                     ("assume", "status", "A-01", "Resolved", "--why", "x"),
                     ("decision", "open", "q"),
                     ("history", "add", "--command", "/x", "--outcome", "y")):
            with self.subTest(command=args[:2]):
                before = {p.name: p.read_bytes() for p in (self.docs / "journey").iterdir()}
                code, out = self.j(*args)
                self.assertEqual(code, 1, out)
                self.assertIn("not canonical", out)
                after = {p.name: p.read_bytes() for p in (self.docs / "journey").iterdir()}
                self.assertEqual(before, after)

    def test_migrate_is_a_dry_run_by_default(self):
        before = {p.name: p.read_bytes() for p in (self.docs / "journey").iterdir()}
        code, out = self.j("migrate")
        self.assertEqual(code, 0, out)
        self.assertIn("dry run: nothing written", out)
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.docs / "journey").iterdir()})

    def test_migrate_write_makes_every_file_canonical_and_loses_nothing(self):
        originals = {n: self.text(n) for n in ("assumptions-register.md", "decisions-log.md",
                                               "journey-state.md")}
        code, out = self.j("migrate", "--write")
        self.assertEqual(code, 0, out)
        self.assertEqual(self.j("check")[0], 0, self.j("check")[1])
        journey = load_module()
        for name, old in originals.items():
            with self.subTest(file=name):
                self.assertEqual(journey.lost_words(old, self.text(name)), [])
                backup = self.docs / "journey" / name.replace(".md", f".pre-migration-{DATE}.md")
                self.assertEqual(backup.read_text(encoding="utf-8"), old)

    def test_migrated_register_shape(self):
        self.j("migrate", "register", "--write")
        reg = self.text("assumptions-register.md")
        rows = [l for l in reg.splitlines() if re.match(r"\| A-\d", l)]
        self.assertEqual([r.split("|")[1].strip() for r in rows], ["A-01", "A-02", "A-04", "A-05", "A-06"])
        self.assertIn("depot manager; Evidence against / for: **Against:** two depots report 45 minutes", reg)
        self.assertIn("- A-01 · Open · — · highest leverage (moved from the row's status cell", reg)
        self.assertIn("- A-04 · Partly resolved · 2026-04-03 · survey covered two of three depots", reg)
        self.assertNotRegex(reg, r"(?m)^#+\s*Updates?\b")       # headings flattened into the notes
        self.assertLess(reg.index("## Earlier notes"), reg.index("## Register"))

    def test_migration_leaves_judgement_to_the_architect(self):
        code, out = self.j("migrate", "register")
        self.assertIn("A-05: 'Recorded'", out)                       # status outside the vocabulary
        self.assertIn("A-02 'FALSIFIED (High).", out)                # a note that reads as a status
        self.assertIn("with no row; give each one with `assume add --id A-<n> ...`: A-03", out)
        self.assertIn("mapped by position; check their Source column: A-06", out)
        self.j("migrate", "register", "--write")
        self.assertIn("| A-02 | Controllers report door state within a second | vendor sheet; "
                      "Evidence against / for: — | a bench test | ADR-0004 | Open |",
                      self.text("assumptions-register.md"))        # status never changed by migration

    def test_migrated_log_and_state(self):
        self.j("migrate", "--write")
        log = self.text("decisions-log.md")
        self.assertIn("## D1 · 2026-03-20 · iterate after iteration 1", log)
        self.assertIn("## 2026-03-01: Terrain gate (reconstructed)", log)   # an event, kept as is
        self.assertEqual(self.j("decision", "next")[1].strip(), "D3")
        state = self.text("journey-state.md")
        self.assertTrue(state.rstrip().endswith("- 2026-03-20 · `/stressor walk courier-fill` · two new actors"))
        self.assertLess(state.index("## Known Gaps"), state.index("## Journey History"))

    def test_writes_work_after_migration(self):
        self.j("migrate", "--write")
        self.assertEqual(self.j("assume", "add", "x", "--source", "s", "--validates", "v",
                                "--depends", "d")[1].strip(), "A-07")
        self.assertEqual(self.j("assume", "add", "Recipients have a phone that receives SMS",
                                "--source", "architect", "--validates", "survey", "--depends", "ADR-0007",
                                "--id", "A-03")[0], 0)
        self.assertEqual(self.j("decision", "open", "q")[1].strip(), "D3")
        self.assertEqual(self.j("history", "add", "--command", "/x", "--outcome", "y")[0], 0)

    def test_trace_still_reads_the_earlier_notes(self):
        # Migration puts the old updates above the table; trace must still
        # treat them as later than the rows (trace 1.0.2).
        self.j("migrate", "--write")
        code, out = run(str(self.docs), "--only", "REG", script=TRACE)
        self.assertIn("A-02 row says 'Open', but a later update", out)
        self.assertNotIn("register tables", out)
        self.assertNotIn("outside any table", out)

    def test_second_migration_is_a_no_op(self):
        self.j("migrate", "--write")
        code, out = self.j("migrate")
        self.assertEqual(code, 0)
        self.assertEqual(out.count("already canonical"), 3, out)

    def test_duplicate_rows_block_the_register_migration(self):
        reg = self.docs / "journey" / "assumptions-register.md"
        reg.write_text(reg.read_text(encoding="utf-8") + "| A-04 | duplicate | x | Open |\n", encoding="utf-8")
        code, out = self.j("migrate", "register", "--write")
        self.assertEqual(code, 1)
        self.assertIn("two rows", out)
        self.assertIn("REFUSED", out)

    def test_material_check_catches_a_lost_word(self):
        journey = load_module()
        old = ["# Register", "| A-1 | the depot floods | x | Open |"]
        new = ["# Register", "| A-1 | the depot | x | Open |"]
        self.assertEqual(journey.material_check("register", old, new),
                         ["1 word(s) would be lost: floods"])
        self.assertTrue(journey.material_check("register", old, ["# Register"]))

    def test_crlf_files_stay_crlf(self):
        reg = self.docs / "journey" / "decisions-log.md"
        reg.write_bytes(reg.read_bytes().replace(b"\n", b"\r\n"))
        self.j("migrate", "log", "--write")
        data = reg.read_bytes()
        self.assertIn(b"\r\n", data)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))


class Asks(JourneyCase):
    """ADR-026: asks routed in the register's Validates it cell, sends as status lines."""

    fixture = "asks"

    def row(self, ident: str) -> str:
        return next(l for l in self.text("assumptions-register.md").splitlines()
                    if l.startswith(f"| {ident} "))

    def test_fixture_is_canonical(self):
        self.assertEqual(self.j("check")[0], 0)

    def test_asks_lists_open_routed_rows_by_recipient(self):
        code, out = self.j("asks")
        self.assertEqual(code, 0, out)
        self.assertIn("3 open for 3 recipient(s), 1 never asked", out)
        for heading in ("## Depot operations (1)", "## Locker vendor (1)", "## Locker vendor team (1)"):
            self.assertIn(heading, out)
        self.assertIn("need: the opening-hours list per depot", out)    # the prefix is not the need
        self.assertIn("depends on it: ADR-0004, S-12", out)
        for settled in ("A-4 ·", "A-6", "A-7"):           # resolved, inside the design, test pending
            self.assertNotIn(settled, out)

    def test_asks_says_when_each_was_last_asked(self):
        out = self.j("asks")[1]
        self.assertIn("- A-1 · Open · never asked", out)
        self.assertIn("- A-2 · Open · asked Locker vendor 2026-04-02, 18 days ago", out)
        self.assertIn("- A-3 · Partly resolved · asked Locker vendor team 2026-04-15, 5 days ago, 2 times", out)

    def test_asks_lists_unrouted_rows_that_read_like_asks(self):
        out = self.j("asks")[1]
        unrouted = out.split("## Not routed")[1].split("\n## ")[0]
        self.assertIn("- A-5: confirm with the courier partner's integration owner", unrouted)
        self.assertNotIn("A-6", unrouted)

    def test_asks_names_recipients_that_may_be_one_and_does_not_merge_them(self):
        out = self.j("asks")[1]
        self.assertIn("- Locker vendor / Locker vendor team", out)
        self.assertIn("## Locker vendor team (1)", out)

    def test_asks_for_one_recipient_ignores_case(self):
        code, out = self.j("asks", "locker VENDOR")
        self.assertEqual(code, 0, out)
        self.assertIn("## Locker vendor (1)", out)
        self.assertNotIn("Depot operations", out)
        self.assertNotIn("Not routed", out)

    def test_asks_for_an_unknown_recipient_names_the_known_ones(self):
        code, out = self.j("asks", "Finance")
        self.assertEqual(code, 1, out)
        self.assertIn("Depot operations, Locker vendor, Locker vendor team", out)

    def test_asks_writes_nothing(self):
        path = self.docs / "journey" / "assumptions-register.md"
        before = path.read_bytes()
        self.j("asks")
        self.assertEqual(path.read_bytes(), before)

    def test_add_with_ask_writes_the_prefix(self):
        code, out = self.j("assume", "add", "Lockers take parcels up to 20 kg", "--source", "spec",
                           "--validates", "the load rating", "--depends", "ADR-0007",
                           "--ask", " Locker   vendor ")
        self.assertEqual((code, out.strip()), (0, "A-8"))
        self.assertIn("| Ask Locker vendor: the load rating |", self.row("A-8"))
        self.assertIn("- A-8 · Open · never asked", self.j("asks", "Locker vendor")[1])

    def test_add_with_a_conflicting_prefix_is_a_usage_error(self):
        code, out = self.j("assume", "add", "x", "--source", "s", "--validates", "Ask Security: v",
                           "--depends", "d", "--ask", "BI")
        self.assertEqual(code, 2, out)

    def test_a_recipient_name_with_a_colon_is_a_usage_error(self):
        code, _ = self.j("assume", "add", "x", "--source", "s", "--validates", "v",
                         "--depends", "d", "--ask", "BI: data")
        self.assertEqual(code, 2)
        self.assertEqual(self.j("assume", "route", "A-5", "")[0], 2)

    def test_route_changes_only_the_validates_cell(self):
        before = self.text("assumptions-register.md").splitlines()
        code, out = self.j("assume", "route", "A-5", "Courier partner")
        self.assertEqual((code, out.strip()), (0, "A-5 · routed to Courier partner"))
        after = self.text("assumptions-register.md").splitlines()
        changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        self.assertEqual(len(before), len(after))
        self.assertEqual(len(changed), 1)
        old, new = split_cells(before[changed[0]]), split_cells(after[changed[0]])
        self.assertEqual(new[3], "Ask Courier partner: confirm with the courier partner's integration owner")
        self.assertEqual(old[:3] + old[4:], new[:3] + new[4:])     # status and date untouched

    def test_route_merges_a_spelling(self):
        code, out = self.j("assume", "route", "A-3", "Locker vendor")
        self.assertEqual(out.strip(), "A-3 · routed to Locker vendor (was Locker vendor team)")
        self.assertIn("## Locker vendor (2)", self.j("asks")[1])
        self.assertNotIn("may be one recipient", self.j("asks")[1])

    def test_route_to_the_same_recipient_writes_nothing(self):
        path = self.docs / "journey" / "assumptions-register.md"
        before = path.read_bytes()
        self.assertIn("already routed", self.j("assume", "route", "A-1", "Depot operations")[1])
        self.assertEqual(path.read_bytes(), before)

    def test_route_of_an_unknown_id_is_refused(self):
        self.assertEqual(self.j("assume", "route", "A-99", "BI")[0], 1)

    def test_asked_keeps_each_status_and_date(self):
        row3 = self.row("A-3")
        code, out = self.j("assume", "asked", "A-2", "A-3", "--to", "Locker vendor")
        self.assertEqual(code, 1, out)                       # A-3 is routed to the team spelling
        self.assertEqual(self.row("A-3"), row3)
        code, out = self.j("assume", "asked", "A-3", "--to", "locker vendor TEAM")
        self.assertEqual(code, 0, out)
        reg = self.text("assumptions-register.md")
        self.assertTrue(reg.rstrip().endswith(
            "- A-3 · Partly resolved · 2026-04-20 · asked Locker vendor team"))  # the route's spelling
        self.assertEqual(self.row("A-3"), row3)              # row status and date unchanged
        self.assertIn("asked Locker vendor team 2026-04-20, 0 days ago, 3 times", self.j("asks")[1])

    def test_asked_records_several_at_once(self):
        self.j("assume", "route", "A-5", "Depot operations")
        code, out = self.j("assume", "asked", "A-1", "A-5", "--to", "Depot operations")
        self.assertEqual(code, 0, out)
        self.assertEqual(len(out.strip().splitlines()), 2)
        self.assertIn("4 open for 3 recipient(s), 0 never asked", self.j("asks")[1])

    def test_asked_refuses_and_writes_nothing_for_a_bad_row(self):
        path = self.docs / "journey" / "assumptions-register.md"
        before = path.read_bytes()
        for args, why in ((["A-1", "A-5"], "not routed"),          # one good, one unrouted
                          (["A-4"], "nothing left to ask"),         # resolved
                          (["A-1"], "routed to Depot operations")):  # someone else's
            to = "Security" if why.startswith("routed") else "Depot operations"
            code, out = self.j("assume", "asked", *args, "--to", to)
            self.assertEqual(code, 1, out)
            self.assertIn(why, out)
        self.assertEqual(path.read_bytes(), before)

    def test_sync_does_not_take_a_date_from_an_asked_line(self):
        self.j("assume", "asked", "A-1", "--to", "Depot operations")
        self.assertIn("already in step", self.j("assume", "sync", "--all")[1])
        self.assertTrue(self.row("A-1").endswith("| Open | 2026-03-10 |"))

    def test_trace_agrees_after_asks_are_recorded(self):
        self.j("assume", "route", "A-5", "Courier partner")
        self.j("assume", "asked", "A-5", "--to", "Courier partner")
        code, out = run(str(self.docs), "--only", "REG", script=TRACE)
        self.assertEqual(code, 0, out)

    def test_unasked_makes_a_single_send_never_asked(self):
        row2 = self.row("A-2")
        code, out = self.j("assume", "unasked", "A-2", "--why", "the section was held back")
        self.assertEqual((code, out.strip()), (0, "A-2 · Open · 2026-04-20 · unasked Locker vendor"))
        self.assertTrue(self.text("assumptions-register.md").rstrip().endswith(
            "- A-2 · Open · 2026-04-20 · unasked Locker vendor: the section was held back"))
        self.assertEqual(self.row("A-2"), row2)              # row status and date unchanged
        out = self.j("asks")[1]
        self.assertIn("- A-2 · Open · never asked", out)
        self.assertIn("3 open for 3 recipient(s), 2 never asked", out)

    def test_unasked_cancels_only_the_last_send(self):
        code, out = self.j("assume", "unasked", "A-3", "--why", "recorded from the plan, not the send")
        self.assertEqual(code, 0, out)
        self.assertIn("- A-3 · Partly resolved · asked Locker vendor team 2026-03-25, 26 days ago",
                      self.j("asks")[1].splitlines())        # the earlier send stands, once

    def test_unasked_then_asked_again_counts_the_new_send(self):
        self.j("assume", "asked", "A-1", "--to", "Depot operations")
        self.j("assume", "unasked", "A-1", "--why", "not sent")
        self.assertIn("- A-1 · Open · never asked", self.j("asks")[1])
        self.j("assume", "asked", "A-1", "--to", "Depot operations")
        self.assertIn("- A-1 · Open · asked Depot operations 2026-04-20, 0 days ago",
                      self.j("asks")[1].splitlines())

    def test_unasked_refuses_and_writes_nothing_without_a_send(self):
        path = self.docs / "journey" / "assumptions-register.md"
        before = path.read_bytes()
        for args, code, why in ((["A-2", "A-1"], 1, "A-1 has no recorded send"),   # one good, one never sent
                                (["A-99"], 1, "no row"),
                                (["A-2", "--why", " "], 2, "--why is required")):
            argv = ["assume", "unasked", *args] + ([] if "--why" in args else ["--why", "not sent"])
            got, out = self.j(*argv)
            self.assertEqual(got, code, out)
            self.assertIn(why, out)
        self.assertEqual(path.read_bytes(), before)
        self.j("assume", "unasked", "A-2", "--why", "not sent")       # its only send, cancelled
        self.assertIn("A-2 has no recorded send", self.j("assume", "unasked", "A-2", "--why", "again")[1])

    def test_sync_and_trace_ignore_an_unasked_line(self):
        self.j("assume", "unasked", "A-3", "--why", "not sent")
        self.assertIn("already in step", self.j("assume", "sync", "--all")[1])
        self.assertTrue(self.row("A-3").endswith("| Partly resolved | 2026-04-10 |"))
        code, out = run(str(self.docs), "--only", "REG", script=TRACE)
        self.assertEqual(code, 0, out)

    def test_ask_commands_refuse_a_legacy_register(self):
        shutil.rmtree(self.docs)
        shutil.copytree(FIXTURES / "legacy", self.docs)
        for args in (["asks"], ["assume", "route", "A-1", "BI"], ["assume", "asked", "A-1", "--to", "BI"],
                     ["assume", "unasked", "A-1", "--why", "not sent"]):
            code, out = self.j(*args)
            self.assertEqual(code, 1, out)
            self.assertIn("migrate register", out)


def split_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split(" | ")]


class Drain(JourneyCase):
    """ADR-031: kinds, the rows a step touches, the register's load, and decisions that say
    what they did to it. The `drain` journey plants one case per worklist: A-3 settled by D3
    and still open, A-4 deferred to an iteration that ran, A-7 resting on a superseded ADR,
    A-8 on a superseded decision, and every kind of row.
    """

    fixture = "drain"

    def row(self, ident: str) -> str:
        return next(l for l in self.text("assumptions-register.md").splitlines()
                    if l.startswith(f"| {ident} "))

    def unchanged(self, *args: str) -> tuple[int, str]:
        files = sorted((self.docs / "journey").iterdir())
        before = [f.read_bytes() for f in files]
        result = self.j(*args)
        self.assertEqual([f.read_bytes() for f in files], before, f"{args[0]} wrote a file")
        return result

    def test_fixture_is_canonical(self):
        self.assertEqual(self.j("check")[0], 0)

    # kinds

    def test_add_with_a_kind_writes_the_prefix(self):
        code, out = self.j("assume", "add", "Bench doors match the field model", "--source", "vendor",
                           "--validates", "compare serials", "--depends", "ADR-0002", "--kind", "Test")
        self.assertEqual((code, out.strip()), (0, "A-11"))
        self.assertIn("| Test: compare serials |", self.row("A-11"))

    def test_add_with_a_kind_and_an_ask_is_a_usage_error(self):
        self.assertEqual(self.unchanged("assume", "add", "x", "--source", "s", "--validates", "v",
                                        "--depends", "d", "--kind", "test", "--ask", "BI")[0], 2)

    def test_add_with_a_conflicting_kind_is_a_usage_error(self):
        for validates, kind in (("Observe: v", "test"), ("Ask BI: v", "decide")):
            with self.subTest(validates=validates):
                self.assertEqual(self.unchanged("assume", "add", "x", "--source", "s", "--validates",
                                                validates, "--depends", "d", "--kind", kind)[0], 2)
        self.assertEqual(self.unchanged("assume", "add", "x", "--source", "s", "--validates",
                                        "Test: v", "--depends", "d", "--ask", "BI")[0], 2)

    def test_ask_is_not_a_kind_to_set(self):
        self.assertEqual(self.unchanged("assume", "kind", "A-3", "ask")[0], 2)

    def test_kind_changes_only_the_validates_cell(self):
        before = self.text("assumptions-register.md").splitlines()
        code, out = self.j("assume", "kind", "A-3", "test")
        self.assertEqual((code, out.strip()), (0, "A-3 · test (was belief)"))
        after = self.text("assumptions-register.md").splitlines()
        changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        self.assertEqual((len(before), len(changed)), (len(after), 1))
        old, new = split_cells(before[changed[0]]), split_cells(after[changed[0]])
        self.assertEqual(new[3], "Test: a week of reservation logs")
        self.assertEqual(old[:3] + old[4:], new[:3] + new[4:])

    def test_kind_replaces_an_ask_and_belief_removes_the_prefix(self):
        self.assertEqual(self.j("assume", "kind", "A-2", "observe")[1].strip(),
                         "A-2 · observe (was Ask Locker vendor)")
        self.assertIn("| Observe: the firmware's reporting interval |", self.row("A-2"))
        self.assertEqual(self.j("assume", "kind", "A-2", "belief")[1].strip(), "A-2 · belief (was observe)")
        self.assertIn("| the firmware's reporting interval |", self.row("A-2"))

    def test_kind_already_set_writes_nothing(self):
        self.assertEqual(self.unchanged("assume", "kind", "A-4", "Decide")[1].strip(), "A-4 is already decide")

    def test_route_replaces_a_kind(self):
        self.assertEqual(self.j("assume", "route", "A-5", "Locker vendor")[1].strip(),
                         "A-5 · routed to Locker vendor (was test)")
        self.assertIn("| Ask Locker vendor: measure on the bench with forty doors |", self.row("A-5"))

    def test_trace_agrees_after_kinds_are_set(self):
        for ident, kind in (("A-1", "test"), ("A-3", "decide")):
            self.j("assume", "kind", ident, kind)
        code, out = run("scan", str(self.docs), "--only", "REG", script=TRACE)
        self.assertNotIn("## REG", out)

    # show and touching

    def test_show_prints_the_row_and_its_own_lines(self):
        code, out = self.unchanged("assume", "show", "A-7", "A-2")
        self.assertEqual(code, 0, out)
        self.assertIn("A-7 · Partly resolved since 2026-04-01 · belief", out)
        self.assertIn("history (the row above is current):", out)
        self.assertIn("- 2026-04-01 · Partly resolved · March volumes fit; April unknown", out)
        self.assertIn("A-2 · Open since 2026-04-05 · ask of Locker vendor", out)
        self.assertIn("- 2026-04-06 · Open · asked Locker vendor", out)
        self.assertNotIn("A-9", out)

    def test_show_of_an_unknown_id_is_refused(self):
        self.assertEqual(self.j("assume", "show", "A-99")[0], 1)

    def test_touching_reads_padding_and_continued_adr_lists(self):
        code, out = self.unchanged("assume", "touching", "ADR-4")
        self.assertEqual(code, 0, out)
        self.assertIn("2 not closed", out)
        self.assertIn("- A-1 · Open since 2026-03-10 · belief · names ADR-4 in depends on it", out)
        self.assertIn("- A-2 ·", out)

    def test_touching_skips_closed_rows_and_keeps_carried_ones(self):
        out = self.j("assume", "touching", "ADR-0003", "ADR-2")[1]
        self.assertIn("- A-7 ·", out)
        self.assertIn("- A-5 · Resolved by design (test pending)", out)
        self.assertNotIn("A-9", out)                                    # resolved

    def test_touching_matches_ids_exactly_and_phrases_by_word(self):
        out = self.j("assume", "touching", "D2", "iteration   2")[1]
        self.assertIn("Rows naming D2, iteration 2", out)
        self.assertIn("- A-8 ·", out)
        self.assertIn("- A-4 · Open since 2026-03-25 · decide · names iteration 2 in validates it", out)
        self.assertNotIn("A-10", out)                                   # withdrawn
        out = self.j("assume", "touching", "D20", "iteration 20")[1]
        self.assertIn(": 0 not closed", out)

    def test_touching_needs_a_reference(self):
        self.assertEqual(self.j("assume", "touching", " ")[0], 2)

    # the register's load

    def test_register_counts_exposure_apart_from_carried(self):
        code, out = self.unchanged("register")
        self.assertEqual(code, 0, out)
        self.assertIn("10 rows, 8 not closed", out)
        self.assertIn("Status: Open 6 · Partly resolved 1 · Resolved by design (test pending) 1 · "
                      "Resolved 1 · Withdrawn 1", out)
        self.assertIn("Exposure: 7 row(s) (belief 4, ask 1, decide 1, observe 1); 5 load-bearing", out)
        self.assertIn("by age of status: 0–6 days 1 · 7–29 days 4 · 30+ days 2; "
                      "6 untouched since registered", out)
        self.assertIn("Carried: 1 row(s) resolved by design, test pending (test 1)", out)

    def worklist(self, out: str, title: str) -> str:
        return out.split(f"## {title}")[1].split("\n## ")[0]

    def test_register_worklists(self):
        out = self.j("register")[1]
        said = self.worklist(out, "Said settled, still open (1)")
        self.assertIn("- A-3 · Open since 2026-03-20 · belief · D3 says it settles this row", said)
        deferred = self.worklist(out, "Deferred to a step that has passed (2)")
        self.assertIn("A-4 · Open since 2026-03-25 · decide · load-bearing · names iteration 2; "
                      "iteration 2 is recorded", deferred)
        self.assertIn("A-8 · Open since 2026-04-02 · belief · load-bearing · validated by D4, answered",
                      deferred)
        stale = self.worklist(out, "Resting on something superseded (2)")
        self.assertIn("A-7 · Partly resolved since 2026-04-01 · belief · load-bearing · rests on ADR-3, "
                      "Superseded by ADR-0006", stale)
        self.assertIn("rests on D2, superseded by D4", stale)
        self.assertNotIn("A-9", stale)                                  # resolved: not a worklist item
        self.assertNotIn("A-10", stale)
        waiting = self.worklist(out, "Decisions waiting for a brief (1)")
        self.assertIn("A-4 ·", waiting)

    def test_register_lists_load_bearing_rows_first(self):
        stale = self.worklist(self.j("register")[1], "Deferred to a step that has passed (2)")
        self.assertLess(stale.index("A-4"), stale.index("A-8"))        # both load-bearing: oldest first

    def test_a_closed_row_leaves_the_worklist(self):
        self.j("assume", "status", "A-3", "Resolved", "--why", "D3: couriers reserve at the depot door")
        self.assertIn("## Said settled, still open (0)\nnone", self.j("register")[1].replace("\r\n", "\n"))

    def test_register_without_an_iteration_says_so(self):
        out = run("register", "--docs", str(FIXTURES / "canonical"), "--date", DATE)[1]
        self.assertIn("No iteration is recorded", out)
        self.assertIn("## Deferred to a step that has passed (0)", out)

    # decisions say what they did to the register

    def test_answer_records_the_register_claim_with_the_register_labels(self):
        code, out = self.j("decision", "answer", "D5", "--answer", "proceed", "--rationale", "r",
                           "--actors", "no", "--assumptions", "settles A-4 A-8")
        self.assertEqual(code, 2, out)                                  # IDs are a comma list
        code, out = self.j("decision", "answer", "D5", "--answer", "proceed", "--rationale", "r",
                           "--actors", "no", "--assumptions", "Settles a-4,A-8 ; raises A-6")
        self.assertEqual(code, 0, out)
        entry = self.text("decisions-log.md").split("## D5")[1]
        # D5 was opened before the field existed: the line goes after the actor set
        self.assertIn("- **Changes the actor set:** no\n- **Assumptions:** settles A-4, A-8; raises A-6\n"
                      "- **Supersedes:** —", entry)
        said = self.worklist(self.j("register")[1], "Said settled, still open (3)")
        self.assertIn("A-4 · Open since 2026-03-25 · decide · load-bearing · D5 says it settles this row", said)

    def test_answer_does_not_change_a_status(self):
        register = (self.docs / "journey" / "assumptions-register.md").read_bytes()
        self.j("decision", "answer", "D5", "--answer", "proceed", "--rationale", "r",
               "--actors", "no", "--assumptions", "settles A-4")
        self.assertEqual((self.docs / "journey" / "assumptions-register.md").read_bytes(), register)

    def test_answer_naming_a_row_that_does_not_exist_is_refused_and_writes_nothing(self):
        code, out = self.unchanged("decision", "answer", "D5", "--answer", "a", "--rationale", "r",
                                   "--actors", "no", "--assumptions", "settles A-4, A-40")
        self.assertEqual(code, 1, out)
        self.assertIn("A-40", out)

    def test_answer_needs_the_field_in_its_grammar(self):
        for bad in ("", "A-4", "settles", "closes A-4", "settles A-4 and A-8"):
            with self.subTest(assumptions=bad):
                self.assertEqual(self.unchanged("decision", "answer", "D5", "--answer", "a",
                                                "--rationale", "r", "--actors", "no",
                                                "--assumptions", bad)[0], 2)

    def test_open_writes_the_field(self):
        self.j("decision", "open", "q")
        self.assertIn("- **Changes the actor set:** —\n- **Assumptions:** —\n- **Supersedes:** —",
                      self.text("decisions-log.md").split("## D6")[1])
        self.j("decision", "answer", "D6", "--answer", "a", "--rationale", "r", "--actors", "no",
               "--assumptions", "none")
        entry = self.text("decisions-log.md").split("## D6")[1]
        self.assertIn("- **Assumptions:** none", entry)
        self.assertEqual(entry.count("**Assumptions:**"), 1)

    def test_note_completes_a_decision_that_never_said(self):
        code, out = run("decision", "note", "D1", "--assumptions", "none", "--docs", str(self.docs),
                        "--date", DATE)
        self.assertEqual(code, 1, out)                                  # D1 already says none
        code, out = self.j("decision", "note", "D4", "--assumptions", "changes A-7")
        self.assertEqual(code, 1, out)                                  # D4 says none: recorded
        log = self.docs / "journey" / "decisions-log.md"
        log.write_text(log.read_text(encoding="utf-8").replace("- **Assumptions:** none\n- **Supersedes:** D2",
                                                               "- **Supersedes:** D2"), encoding="utf-8")
        code, out = self.j("decision", "note", "D4", "--assumptions", "changes A-7; settles A-8")
        self.assertEqual((code, out.strip()), (0, "D4: assumptions: changes A-7; settles A-8"))
        self.assertIn("- **Assumptions:** changes A-7; settles A-8 *(recorded 2026-04-20; not stated "
                      "when decided)*", self.text("decisions-log.md").split("## D4")[1])
        said = self.worklist(self.j("register")[1], "Said settled, still open (2)")
        self.assertIn("D4 says it settles this row", said)

    def test_note_needs_something_to_record(self):
        self.assertEqual(self.j("decision", "note", "D4")[0], 2)

    def test_mod_reads_the_log_with_the_new_field(self):
        # matrix.ts finds the actor-set field by its own name; a new field must not shadow it
        log = self.text("decisions-log.md")
        self.assertEqual(len(re.findall(r"\*\*Changes the actor set:\*\* yes", log)), 2)


class Usage(JourneyCase):

    def test_bad_arguments_exit_two(self):
        self.assertEqual(self.j("decision", "answer", "seven", "--answer", "a", "--rationale", "r",
                                "--actors", "no", "--assumptions", "none")[0], 2)
        self.assertEqual(run("assume", "add", "x", "--docs", str(self.docs), "--date", "tomorrow",
                             "--source", "s", "--validates", "v", "--depends", "d")[0], 2)
        self.assertEqual(self.j("history", "add", "--command", "/x", "--outcome", "y",
                                "--decision", "seven")[0], 2)


class SharedSnippet(JourneyCase):
    """The snippet in scripts/preamble/journey-files.md, run as written, from a project root."""

    def snippet(self) -> str:
        match = re.search(r"```bash\n(.*?)```", FRAGMENT.read_text(encoding="utf-8"), re.DOTALL)
        self.assertIsNotNone(match)
        return match.group(1)

    def run_snippet(self, home: Path) -> tuple[int, str]:
        shell = posix_shell("sh") or posix_shell("bash")
        if not shell:
            self.skipTest("no POSIX shell")
        env = dict(os.environ, HOME=home.as_posix())
        done = subprocess.run([shell, "-c", self.snippet()], cwd=self.tmp, capture_output=True,
                              env=posix_env(shell, env), timeout=60)
        return done.returncode, (done.stdout + done.stderr).decode("utf-8", errors="replace")

    def test_snippet_runs_the_installed_script(self):
        home = self.tmp / "home"
        shutil.copytree(ROOT / "skills" / "restack-journey", home / ".claude" / "skills" / "restack-journey",
                        ignore=shutil.ignore_patterns("__pycache__"))
        code, out = self.run_snippet(home)
        self.assertEqual(code, 0, out)
        self.assertIn("journey/assumptions-register.md: canonical", out)

    def test_snippet_passes_a_slash_command_through_unchanged(self):
        # The case Git Bash broke in the field: an argument starting with `/`.
        home = self.tmp / "home"
        shutil.copytree(ROOT / "skills" / "restack-journey", home / ".claude" / "skills" / "restack-journey",
                        ignore=shutil.ignore_patterns("__pycache__"))
        snippet = self.snippet()
        self.assertIn('"$JY" check;', snippet)
        snippet = snippet.replace(
            '"$JY" check;',
            '"$JY" history add --command "/restack-journey iterate" --outcome "o" --date 2026-04-20;')
        shell = posix_shell("sh") or posix_shell("bash")
        if not shell:
            self.skipTest("no POSIX shell")
        done = subprocess.run([shell, "-c", snippet], cwd=self.tmp, capture_output=True,
                              env=posix_env(shell, dict(os.environ, HOME=home.as_posix())), timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        self.assertTrue(self.text("journey-state.md").rstrip().endswith(
            "- 2026-04-20 · `/restack-journey iterate` · o"))

    def test_snippet_without_the_script_says_so(self):
        code, out = self.run_snippet(self.tmp / "empty-home")
        self.assertEqual((code, out.strip()), (0, "journey helper unavailable: write the journey "
                                                  "files by hand in their canonical shape"))


if __name__ == "__main__":
    unittest.main()
