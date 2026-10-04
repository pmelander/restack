#!/usr/bin/env python3
"""Tests for skills/restack-restyle/scripts/restyle.py (ADR-028).

The guard is the whole of restyle's safety: a restyle may reword anything, and
the comparison is what proves nothing material moved. So every material class
is tested twice, a planted change that must be refused and the clean restyle
beside it that must pass, and every confirm item once.

Fixtures are tests/fixtures/restyle/: an invented engagement ("Lockerline")
with an old-style ADR, its restyled draft, a retired ADR, a current ADR with an
earlier editorial note, and descriptive documents. Every case runs on a scratch
copy.

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "restack-restyle" / "scripts" / "restyle.py"
FIXTURE = ROOT / "tests" / "fixtures" / "restyle"
ADR1 = "adr/ADR-0001-queue-locker-reservations.md"
DROP = ["--drop", "Reflection prompts"]

GIT = ["git", "-c", "user.name=restack-test", "-c", "user.email=test@example.invalid",
       "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false"]


def run(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
    done = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=cwd, env=env,
                          capture_output=True, timeout=60)
    out = done.stdout.decode("utf-8") + done.stderr.decode("utf-8")
    return done.returncode, out.replace("\r\n", "\n")


class RestyleCase(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="restack-restyle-"))
        shutil.copytree(FIXTURE, self.tmp, dirs_exist_ok=True)
        self.docs = self.tmp / "docs"
        self.old = self.docs / ADR1
        self.draft = self.tmp / "restyled" / Path(ADR1).name

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def variant(self, old: str, new: str, count: int = 1) -> Path:
        """The restyled draft with one planted change."""
        text = self.draft.read_text(encoding="utf-8")
        self.assertIn(old, text, f"fixture no longer contains {old!r}")
        path = self.tmp / "variant.md"
        path.write_text(text.replace(old, new, count), encoding="utf-8")
        return path

    def compare(self, new: Path, *extra: str) -> tuple[int, str]:
        return run("compare", str(self.old), str(new), *DROP, *extra)


class CleanRestyle(RestyleCase):

    def test_the_restyled_draft_passes_with_only_confirmations(self):
        code, out = self.compare(self.draft)
        self.assertEqual(code, 3, out)
        self.assertNotIn("REFUSED", out)
        # the dropped old-style sentence is visible, not silent
        self.assertIn("capability", out)

    def test_metadata_sections_and_bold_fields_are_the_same_fields(self):
        code, out = self.compare(self.draft)
        self.assertNotIn("field", out)

    def test_a_rewrapped_copy_is_identical(self):
        text = self.old.read_text(encoding="utf-8").replace("Locker Controller synchronously, and",
                                                            "Locker Controller\nsynchronously, and")
        path = self.tmp / "rewrap.md"
        path.write_text(text, encoding="utf-8")
        code, out = run("compare", str(self.old), str(path))
        self.assertEqual(code, 0, out)

    def test_heading_case_is_style(self):
        code, out = self.compare(self.draft)
        self.assertNotIn("Considered", out)


class Refusals(RestyleCase):

    def assertRefused(self, new: Path, needle: str):
        code, out = self.compare(new)
        self.assertEqual(code, 1, out)
        self.assertIn("REFUSED", out)
        self.assertIn(needle, out)

    def test_a_section_removed_without_drop(self):
        code, out = run("compare", str(self.old), str(self.draft))
        self.assertEqual(code, 1, out)
        self.assertIn("section 'reflection prompts'", out)
        self.assertIn("--drop", out)

    def test_a_changed_date(self):
        self.assertRefused(self.variant("2026-03-02", "2026-03-03"), "date")

    def test_a_lost_id(self):
        self.assertRefused(self.variant("(clears S-4 and S-7)", "(clears S-4)"), "S-7")

    def test_a_changed_figure(self):
        self.assertRefused(self.variant("within 5 minutes", "within 15 minutes", 1), "figure")

    def test_a_figure_spelled_out(self):
        self.assertRefused(self.variant("takes 40% of lockers", "takes forty percent of lockers"),
                           "40%")

    def test_a_changed_link(self):
        self.assertRefused(self.variant("matrix-iteration-1.md", "matrix-iteration-2.md"), "link")

    def test_changed_code(self):
        self.assertRefused(self.variant("retention_hours: 72", "retention_hours: 48"), "code")

    def test_changed_inline_code(self):
        self.assertRefused(self.variant("`reservations.v1`", "`reservations.v2`"), "code")

    def test_a_reworded_table_row(self):
        self.assertRefused(self.variant("| 72-hour retention | A-2 | yes |",
                                        "| Retention of 72 hours | A-2 | yes |"), "table row")

    def test_a_gap_filled_with_a_new_field(self):
        self.assertRefused(self.variant("**Deciders:**",
                                        "**Reversibility:** Reversible\n\n**Deciders:**"),
                           "field 'reversibility' added")

    def test_a_changed_status(self):
        self.assertRefused(self.variant("**Status:** Accepted", "**Status:** Proposed"),
                           "field 'status' changed")

    def test_an_alternative_renamed(self):
        self.assertRefused(self.variant("### Retry the synchronous call", "### Retry"),
                           "alternative")

    def test_a_struck_passage_unstruck(self):
        struck = self.draft.read_text(encoding="utf-8").replace(
            "Rejected: two writers", "Rejected: ~~one writer~~ two writers")
        self.old.write_text(self.old.read_text(encoding="utf-8").replace(
            "Rejected: two writers", "Rejected: ~~one writer~~ two writers"), encoding="utf-8")
        self.draft.write_text(struck, encoding="utf-8")
        self.assertRefused(self.variant("~~one writer~~ ", ""), "struck")

    def test_a_banner_reworded(self):
        banner = "> **Amended 2026-04-01:** SMS within 5 minutes.\n\n## Context"
        self.old.write_text(self.old.read_text(encoding="utf-8").replace(
            "## Context", banner, 1), encoding="utf-8")
        self.draft.write_text(self.draft.read_text(encoding="utf-8").replace(
            "## Context", banner, 1), encoding="utf-8")
        self.assertRefused(self.variant("SMS within 5 minutes.", "SMS within 5 minutes now."),
                           "banner")

    def test_a_draft_that_writes_its_own_note(self):
        new = self.variant("Rejected: two writers to locker state.",
                           "Rejected: two writers to locker state.\n\n## Editorial notes\n\n- x")
        self.assertRefused(new, "apply writes it")

    def test_an_earlier_note_changed(self):
        old = self.docs / "adr" / "ADR-0003-push-locker-status.md"
        new = self.tmp / "adr3.md"
        new.write_text(old.read_text(encoding="utf-8").replace("2026-09-01", "2026-09-02"),
                       encoding="utf-8")
        code, out = run("compare", str(old), str(new))
        self.assertEqual(code, 1, out)
        self.assertIn("earlier editorial note", out)


class Confirmations(RestyleCase):

    def assertConfirm(self, new: Path, needle: str):
        code, out = self.compare(new)
        self.assertEqual(code, 3, out)
        self.assertNotIn("REFUSED", out)
        self.assertIn(needle, out)

    def test_must_becomes_should(self):
        new = self.variant("Reservations must not be", "Reservations should not be")
        code, out = self.compare(new)
        self.assertIn("'must' 1 -> 0", out)
        self.assertIn("OLD: Reservations must not be lost", out)
        self.assertIn("NEW: Reservations should not be lost", out)

    def test_a_dropped_not(self):
        self.assertConfirm(self.variant("are not replayed", "are replayed"), "'not'")

    def test_a_contraction_is_not_a_change(self):
        code, out = self.compare(self.variant("are not replayed", "aren't replayed"))
        self.assertNotIn("'not'", out)

    def test_a_changed_title(self):
        self.assertConfirm(self.variant("Queue Locker Reservations Behind",
                                        "Put Locker Reservations Behind"), "title")

    def test_a_lost_name(self):
        self.assertConfirm(self.variant("told by SMS within", "told by text within"),
                           "name(s) no longer in NEW: SMS")

    def test_a_lost_word(self):
        self.assertConfirm(self.variant("it only moves the timeout", "it only moves the delay"),
                           "word(s) no longer in NEW: building, capability, plumbing, queues, "
                           "residuals, timeout")

    def test_an_id_cited_fewer_times(self):
        self.assertConfirm(self.variant("(clears S-4 and S-7)", "(clears S-7)"),
                           "S-4 cited 2 time(s) in OLD, 1 in NEW")

    def test_a_body_that_shrank(self):
        notes = ("\n## Operating notes\n\n" + "Operators watch the depth of the queue every "
                 "morning and page the platform team when it keeps growing. " * 12)
        for path in (self.old, self.draft):
            path.write_text(path.read_text(encoding="utf-8") + notes, encoding="utf-8")
        text = self.draft.read_text(encoding="utf-8")
        new = self.tmp / "short.md"
        new.write_text(text.split("## Operating notes")[0] + "## Operating notes\n\nOperators "
                       "watch the queue.\n", encoding="utf-8")
        self.assertConfirm(new, "shrank")


class Apply(RestyleCase):

    def candidate(self) -> Path:
        cand = self.old.parent / ".restyle" / self.old.name
        cand.parent.mkdir()
        shutil.copy2(self.draft, cand)
        return cand

    def test_refused_writes_nothing(self):
        before = self.old.read_bytes()
        code, out = run("apply", str(self.old), str(self.draft), "--reshaped", "x")
        self.assertEqual(code, 1, out)
        self.assertIn("Not written", out)
        self.assertEqual(self.old.read_bytes(), before)

    def test_waits_for_confirmation(self):
        before = self.old.read_bytes()
        code, out = run("apply", str(self.old), str(self.draft), *DROP, "--reshaped", "x")
        self.assertEqual(code, 3, out)
        self.assertIn("--confirmed", out)
        self.assertEqual(self.old.read_bytes(), before)

    def test_writes_the_note_backs_up_and_clears_the_candidate(self):
        cand = self.candidate()
        code, out = run("apply", str(self.old), str(cand), *DROP, "--confirmed", "--date",
                        "2026-10-04", "--reshaped", "metadata sections as fields")
        self.assertEqual(code, 0, out)
        text = self.old.read_text(encoding="utf-8")
        self.assertTrue(text.rstrip().endswith(
            '- 2026-10-04 · restyled, wording only · reshaped: metadata sections as fields · '
            'dropped: "Reflection prompts" · checked by restyle.py ' + text.rsplit(" ", 1)[1].strip()))
        self.assertIn("## Editorial notes", text)
        self.assertNotIn("Reflection prompts\n", text)
        backup = self.old.parent / ".restyle" / f"{self.old.stem}.pre-restyle-2026-10-04.md"
        self.assertTrue(backup.exists(), out)          # not a git work tree: a backup
        self.assertFalse(cand.exists())
        # against the original, the only refusal left is the note apply wrote
        code, out = run("compare", str(backup), str(self.old), *DROP)
        refused = [x for x in out.splitlines() if "REFUSED" in x]
        self.assertEqual(len(refused), 1, out)
        self.assertIn("editorial note", refused[0])

    def test_no_backup_in_a_clean_work_tree(self):
        subprocess.run([*GIT, "init", "-q", str(self.tmp)], check=True)
        subprocess.run([*GIT, "-C", str(self.tmp), "add", "-A"], check=True)
        subprocess.run([*GIT, "-C", str(self.tmp), "commit", "-qm", "fixture"], check=True)
        cand = self.candidate()
        code, out = run("apply", str(self.old), str(cand), *DROP, "--confirmed",
                        "--reshaped", "x")
        self.assertEqual(code, 0, out)
        self.assertNotIn("backup", out)
        self.assertFalse((self.old.parent / ".restyle").exists())

    def test_a_second_restyle_appends_its_note(self):
        old = self.docs / "adr" / "ADR-0003-push-locker-status.md"
        new = self.tmp / "adr3.md"
        new.write_text(old.read_text(encoding="utf-8").replace(
            "We will publish a status event from each locker on change.",
            "We will publish a status event from each locker when its status changes."),
            encoding="utf-8")
        code, out = run("apply", str(old), str(new), "--confirmed", "--date", "2026-10-04",
                        "--reshaped", "Decision reworded")
        self.assertEqual(code, 0, out)
        notes = old.read_text(encoding="utf-8").split("## Editorial notes")[1].strip().splitlines()
        self.assertEqual(len(notes), 2)
        self.assertTrue(notes[0].startswith("- 2026-09-01"))
        self.assertTrue(notes[1].startswith("- 2026-10-04"))

    def test_keeps_crlf(self):
        self.old.write_bytes(self.old.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        cand = self.candidate()
        code, out = run("apply", str(self.old), str(cand), *DROP, "--confirmed", "--reshaped", "x")
        self.assertEqual(code, 0, out)
        self.assertNotIn(b"\n", self.old.read_bytes().replace(b"\r\n", b""))


class Usage(RestyleCase):

    def test_drop_of_a_heading_old_does_not_have(self):
        code, out = run("compare", str(self.old), str(self.draft), "--drop", "Nope")
        self.assertEqual(code, 2, out)

    def test_same_file(self):
        code, out = run("compare", str(self.old), str(self.old))
        self.assertEqual(code, 2, out)

    def test_apply_needs_reshaped(self):
        code, _ = run("apply", str(self.old), str(self.draft))
        self.assertEqual(code, 2)

    def test_missing_docs(self):
        code, _ = run("survey", str(self.tmp / "nope"))
        self.assertEqual(code, 2)


class Survey(RestyleCase):

    def setUp(self):
        super().setUp()
        self.code, self.out = run("survey", str(self.docs))
        self.blocks = {b.split("\n", 1)[0].split("  [")[0]: b for b in self.out.split("\n\n")}

    def test_lists_old_style_sections_wording_and_gaps(self):
        self.assertEqual(self.code, 1, self.out)
        block = self.blocks[ADR1]
        self.assertIn("old-style section   line ", block)
        self.assertIn("Reflection prompts", block)
        self.assertIn("building the capability", block)
        self.assertIn("field Reversibility, field Review date, section Knock-on changes", block)
        self.assertNotIn("field Status", block)        # a `## Status` section is the field

    def test_a_retired_adr_is_history(self):
        self.assertIn("retired: history", self.blocks["adr/ADR-0002-poll-locker-status.md"])
        self.assertNotIn("gap", self.blocks["adr/ADR-0002-poll-locker-status.md"])

    def test_a_footnote_amendment_belongs_to_the_owning_skill(self):
        self.assertIn("not restyle's", self.blocks["architecture/HLD.md"])
        self.assertIn("Capability being built", self.blocks["architecture/HLD.md"])

    def test_current_and_out_of_scope_documents_are_not_listed(self):
        for rel in ("adr/ADR-0003-push-locker-status.md", "architecture/DEPLOYMENT.md",
                    "journey/journey-state.md"):
            self.assertNotIn(rel, self.out)

    def test_scratch_is_ignored(self):
        scratch = self.docs / "adr" / ".restyle"
        scratch.mkdir()
        shutil.copy2(self.old, scratch / self.old.name)
        _, out = run("survey", str(self.docs))
        self.assertNotIn(".restyle", out)

    def test_nothing_to_restyle(self):
        clean = self.tmp / "clean"
        (clean / "adr").mkdir(parents=True)
        shutil.copy2(self.docs / "adr" / "ADR-0003-push-locker-status.md", clean / "adr")
        code, out = run("survey", str(clean))
        self.assertEqual(code, 0, out)
        self.assertIn("not tone", out)


if __name__ == "__main__":
    unittest.main()
