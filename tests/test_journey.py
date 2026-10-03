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
                           "--rationale", "depots share couriers", "--actors", "yes: added the shard router")
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
        code, out = self.j("decision", "answer", "D2", "--answer", "x", "--rationale", "y", "--actors", "no")
        self.assertEqual(code, 1)
        self.assertIn("already answered", out)

    def test_answering_an_unopened_decision_is_refused(self):
        code, out = self.j("decision", "answer", "D9", "--answer", "x", "--rationale", "y", "--actors", "no")
        self.assertEqual(code, 1)
        self.assertIn("decision open", out)

    def test_actors_yes_needs_the_change(self):
        self.j("decision", "open", "q")
        self.assertEqual(self.j("decision", "answer", "D3", "--answer", "x", "--rationale", "y",
                                "--actors", "yes")[0], 2)

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
        self.assertIn("already records it", out)

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


class Usage(JourneyCase):

    def test_bad_arguments_exit_two(self):
        self.assertEqual(self.j("decision", "answer", "seven", "--answer", "a", "--rationale", "r",
                                "--actors", "no")[0], 2)
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
