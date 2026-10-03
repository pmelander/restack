#!/usr/bin/env python3
"""Tests for skills/restack-trace/scripts/trace.py (ADR-021).

Every case runs against a scratch copy of tests/fixtures/trace/docs, a
synthetic engagement with one planted defect per check and a clean neighbour
beside each. The copy gets fixed modification times, because a checkout's
mtimes are whatever the clone wrote, and the knock-on and PDF checks compare
dates.

Each check is tested for what it must find and for what it must leave alone.
The second half matters as much: a check that cries wolf gets ignored, and an
ignored check is a failed control.

    python -m unittest discover -s tests -v

Standard library only, like everything else the toolkit runs.
"""

from __future__ import annotations

import datetime as dt
import json
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
SCRIPT = ROOT / "skills" / "restack-trace" / "scripts" / "trace.py"
SECTION = ROOT / "scripts" / "shared" / "trace.md"
FIXTURE = ROOT / "tests" / "fixtures" / "trace" / "docs"

# Last-changed dates for the fixture. Anything not listed gets DEFAULT.
DEFAULT = "2026-04-20"
MTIMES = {
    "architecture/HLD.md": "2026-03-20",            # before ADR-0003 (2026-04-01) said it was updated
    "deployment/DEPLOYMENT.md": "2026-04-02",       # after ADR-0003: the clean neighbour
    "operations/RUNBOOK.md": "2026-04-02",
}

GIT = ["git", "-c", "user.name=restack-test", "-c", "user.email=test@example.invalid",
       "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false"]


def stamp(day: str) -> float:
    return dt.datetime.fromisoformat(day + "T12:00:00").timestamp()


def run(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONIOENCODING"}
    done = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=cwd, env=env,
                          capture_output=True, timeout=60)
    return done.returncode, done.stdout.decode("utf-8") + done.stderr.decode("utf-8")


class TraceCase(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="restack-trace-"))
        self.docs = self.tmp / "docs"
        shutil.copytree(FIXTURE, self.docs)
        for path in self.docs.rglob("*"):
            if path.is_file():
                rel = path.relative_to(self.docs).as_posix()
                when = stamp(MTIMES.get(rel, DEFAULT))
                os.utime(path, (when, when))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def scan(self, *extra: str) -> list[dict]:
        code, out = run("scan", str(self.docs), "--json", "--dates", "mtime", *extra)
        self.assertIn(code, (0, 1), out)
        return json.loads(out)["findings"]

    def of(self, check: str, *extra: str) -> list[dict]:
        return [f for f in self.scan("--only", check, *extra) if f["check"] == check]

    @staticmethod
    def text(findings: list[dict]) -> str:
        return "\n".join(f"{f['path']}:{f['line']} {f['message']} {f['detail']}" for f in findings)


class Checks(TraceCase):

    def test_ref_finds_undefined_ids(self):
        found = self.text(self.of("REF"))
        self.assertIn("ADR-0009 is cited", found)
        self.assertIn("D9 is cited", found)
        self.assertIn("A-7 is cited", found)

    def test_ref_ignores_ids_far_past_the_log(self):
        self.assertNotIn("D365", self.text(self.of("REF")))

    def test_ref_treats_padded_and_unpadded_ids_as_one(self):
        hld = self.docs / "architecture" / "HLD.md"
        hld.write_text(hld.read_text(encoding="utf-8") + "\nA-01 and ADR-3 are both defined.\n",
                       encoding="utf-8")
        found = self.text(self.of("REF"))
        self.assertNotIn("A-1 is cited", found)
        self.assertNotIn("ADR-0003 is cited", found)

    def test_reg_finds_row_contradicted_by_its_status_line(self):
        found = self.text(self.of("REG"))
        self.assertIn("A-1 row says 'Open', but its last status line", found)
        self.assertIn("'Maybe': A-2", found)
        self.assertNotIn("A-3 row", found)

    def test_reg_reports_rows_outside_any_table(self):
        reg = self.docs / "journey" / "assumptions-register.md"
        lines = reg.read_text(encoding="utf-8").splitlines()
        at = next(i for i, line in enumerate(lines) if line.startswith("| A-3"))
        lines.insert(at, "- A-2 · Open · 2026-04-06 · a stray status line")
        reg.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertIn("1 row(s) sit outside any table", self.text(self.of("REG")))

    def test_reg_reads_legacy_update_bullets(self):
        reg = self.docs / "journey" / "assumptions-register.md"
        text = reg.read_text(encoding="utf-8").split("## Status lines")[0]
        text += "### Updates 2026-04-12\n- **A-1: FALSIFIED (High).** The logs disagree.\n"
        reg.write_text(text, encoding="utf-8")
        found = self.of("REG")
        legacy = [f for f in found if "A-1 row says" in f["message"]]
        self.assertTrue(legacy and legacy[0]["heuristic"], self.text(found))
        self.assertIn("'Update' heading", self.text(found))

    def test_ko_finds_each_unfinished_knock_on(self):
        found = self.text(self.of("KO"))
        self.assertIn("says architecture/HLD.md was 'updated', but it last changed 2026-03-20", found)
        self.assertIn("RUNBOOK.md was bannered, but nothing above its body cites ADR-0003", found)
        self.assertIn("names LLD-04, and no document by that name exists", found)
        self.assertIn("'Test strategy' is recorded as 'pending'", found)
        self.assertIn("ADR-0004: Knock-on changes is empty", found)
        self.assertIn("adr/ADR-0005-courier-identity.md", found)

    def test_ko_leaves_finished_rows_alone(self):
        found = self.text(self.of("KO"))
        self.assertNotIn("DEPLOYMENT", found)                  # changed after the ADR
        self.assertNotIn("ADR-0006", found)                    # "None", after a grep
        self.assertNotIn("ADR-0007", found)                    # ticketed

    def test_ko_tbd_handed_to_a_registered_assumption_is_not_pending(self):
        # ADR-0007's LLD-02 row reads "struck; ... TBD (A-3)": the knock-on was
        # made, and the open question has an owner in the register.
        self.assertNotIn("ADR-0007", self.text(self.of("KO")))
        adr = self.docs / "adr" / "ADR-0007-notification-channel.md"
        adr.write_text(adr.read_text(encoding="utf-8").replace("TBD (A-3)", "TBD (A-99)"),
                       encoding="utf-8")
        self.assertIn("ADR-0007: 'LLD-02' is recorded as", self.text(self.of("KO")))

    def test_ko_banner_counts_once_written(self):
        runbook = self.docs / "operations" / "RUNBOOK.md"
        text = runbook.read_text(encoding="utf-8").replace(
            "# Lockerline: operations runbook\n",
            "# Lockerline: operations runbook\n\n> **Stale since ADR-0003:** §2 is replaced.\n")
        runbook.write_text(text, encoding="utf-8")
        self.assertNotIn("bannered", self.text(self.of("KO")))

    def test_ko_ignores_adrs_from_before_the_field_was_adopted(self):
        found = self.text(self.of("KO"))
        self.assertNotIn("ADR-0001", found)
        self.assertNotIn("ADR-0002", found)

    def test_am_finds_footnote_amendments(self):
        found = self.of("AM")
        paths = {f["path"] for f in found}
        self.assertEqual(paths, {"adr/ADR-0002-reservation-expiry.md",
                                 "architecture/LLD-02-reservation-api.md"}, self.text(found))
        lld = next(f for f in found if f["path"].startswith("architecture/LLD-02"))
        self.assertEqual(lld["detail"], ["line 21: Amendment (2026-04-20)"])  # not the covered one

    def test_am_leaves_inline_marked_sections_alone(self):
        self.assertNotIn("HLD.md", self.text(self.of("AM")))

    def test_am_accepts_other_banner_wording(self):
        # ADR-0006's banner says "Current state", not "AMENDED".
        self.assertNotIn("ADR-0006", self.text(self.of("AM")))

    def test_am_metadata_line_is_not_a_banner(self):
        adr = self.docs / "adr" / "ADR-0002-reservation-expiry.md"
        adr.write_text(adr.read_text(encoding="utf-8").replace(
            "**Date:** 2026-03-10\n", "**Date:** 2026-03-10\n\n**Updated:** 2026-04-25\n"),
            encoding="utf-8")
        self.assertIn("adr/ADR-0002-reservation-expiry.md", self.text(self.of("AM")))

    def test_sup_finds_unmarked_citation_of_superseded_adr(self):
        found = self.of("SUP")
        self.assertEqual(len(found), 1, self.text(found))
        self.assertEqual((found[0]["path"], found[0]["line"]), ("architecture/HLD.md", 15))

    def test_sup_ignores_history_and_archive(self):
        found = self.text(self.of("SUP"))
        self.assertNotIn("reviews/", found)
        self.assertNotIn("archive/", found)

    def test_sup_reports_superseded_without_successor(self):
        adr = self.docs / "adr" / "ADR-0001-reservation-store-relational.md"
        adr.write_text(adr.read_text(encoding="utf-8").replace("Superseded by ADR-0003", "Superseded"),
                       encoding="utf-8")
        self.assertIn("names no successor", self.text(self.of("SUP")))

    def test_base_finds_matrix_scored_before_actor_change(self):
        found = self.text(self.of("BASE"))
        self.assertIn("matrix-2026-04-01-iter2.md:3 scored at D2; D3 changed the actor set", found)
        self.assertIn("architecture/HLD.md:24 quotes matrix-2026-04-01-iter2.md", found)
        self.assertNotIn("iter3", found)

    def test_base_accepts_the_qualifier(self):
        m = self.docs / "stressor-analysis" / "matrix-2026-04-01-iter2.md"
        m.write_text(m.read_text(encoding="utf-8").replace(
            "**Scoring baseline:** D2", "**Scoring baseline:** D2, `scored pre-D3`"), encoding="utf-8")
        self.assertEqual(self.of("BASE"), [])

    def test_mx_checks_arithmetic_and_binary_scoring(self):
        found = self.of("MX")
        self.assertTrue(all(f["path"].endswith("iter2.md") for f in found), self.text(found))
        details = "\n".join(d for f in found for d in f["detail"])
        self.assertIn("S-2 cells sum to 2, row total says 3", details)
        self.assertIn("column LC sums to 1, totals row says 2", details)
        self.assertIn("S-3 × NS = 2", details)
        self.assertNotIn("S-1", details)

    def test_alert_finds_runbook_only_alerts(self):
        found = self.of("ALERT")
        self.assertEqual(len(found), 1, self.text(found))
        self.assertIn("LOCKER-GHOST", found[0]["message"])
        self.assertTrue(found[0]["heuristic"])

    def test_ph_skips_fenced_blocks_and_registered_gaps(self):
        # DEPLOYMENT's TBD is in a code block; the HLD's names A-1.
        found = self.of("PH")
        self.assertEqual([f["path"] for f in found], ["adr/ADR-0002-reservation-expiry.md"])

    def test_ph_tbd_naming_an_unregistered_assumption_still_counts(self):
        hld = self.docs / "architecture" / "HLD.md"
        hld.write_text(hld.read_text(encoding="utf-8").replace("TBD (A-1)", "TBD (A-99)"),
                       encoding="utf-8")
        self.assertIn("architecture/HLD.md", self.text(self.of("PH")))

    def test_pdf_older_than_its_source(self):
        pdf = self.docs / "deployment" / "DEPLOYMENT.pdf"
        pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
        os.utime(pdf, (stamp("2026-03-01"),) * 2)
        current = self.docs / "architecture" / "HLD.pdf"
        current.write_bytes(b"%PDF-1.4\n%%EOF\n")
        os.utime(current, (stamp("2026-04-25"),) * 2)
        found = self.of("PDF")
        self.assertEqual([f["path"] for f in found], ["deployment/DEPLOYMENT.pdf"])

    def test_pdf_renamed_export_is_paired_with_its_source(self):
        pdf = self.docs / "architecture" / "HLD-high-level-design.pdf"
        pdf.write_bytes(b"%PDF-1.4\n%%EOF\n")
        os.utime(pdf, (stamp("2026-03-01"),) * 2)
        found = self.of("PDF")
        self.assertEqual([(f["path"], f["heuristic"]) for f in found],
                         [("architecture/HLD-high-level-design.pdf", True)])


class Commands(TraceCase):

    def test_scan_is_the_default_command(self):
        code, out = run(str(self.docs), "--dates", "mtime")
        self.assertEqual(code, 1)
        self.assertIn("A worklist, not a verdict", out)
        self.assertIn("file modification times", out)

    def test_clean_tree_exits_zero(self):
        empty = self.tmp / "empty"
        (empty / "adr").mkdir(parents=True)
        code, out = run("scan", str(empty))
        self.assertEqual(code, 0, out)
        self.assertIn("Nothing found", out)

    def test_terms_lists_unmarked_passages_only(self):
        code, out = run("terms", "poll", "--docs", str(self.docs), "--json")
        self.assertEqual(code, 1)
        hits = [(f["path"], f["line"]) for f in json.loads(out)["findings"]]
        self.assertEqual(hits, [("adr/ADR-0002-reservation-expiry.md", 15),
                                ("architecture/LLD-02-reservation-api.md", 15)])

    def test_terms_exits_zero_once_marked(self):
        for rel, old, new in (
                ("adr/ADR-0002-reservation-expiry.md", "by polling the", "by ~~polling~~ the"),
                ("architecture/LLD-02-reservation-api.md", "still polls the", "still ~~polls~~ the")):
            path = self.docs / rel
            path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
        code, out = run("terms", "poll", "--docs", str(self.docs))
        self.assertEqual(code, 0, out)

    def test_terms_in_named_files(self):
        lld = self.docs / "architecture" / "LLD-02-reservation-api.md"
        code, out = run("terms", "poll", "--in", str(lld), "--json")
        self.assertEqual(len(json.loads(out)["findings"]), 1)

    def test_refs_labels_kind_and_marking(self):
        code, out = run("refs", "ADR-1", "--docs", str(self.docs), "--json")
        found = json.loads(out)["findings"]
        hld = [f["message"] for f in found if f["path"] == "architecture/HLD.md"]
        self.assertEqual(len(hld), 2)
        self.assertTrue(hld[0].startswith("[descriptive, unmarked]"))
        self.assertTrue(hld[1].startswith("[descriptive, marked]"))

    def test_usage_errors_exit_two(self):
        self.assertEqual(run("scan", str(self.tmp / "missing"))[0], 2)
        self.assertEqual(run("scan", str(self.docs), "--only", "NOPE")[0], 2)
        self.assertEqual(run("refs", "banana", "--docs", str(self.docs))[0], 2)

    def test_output_survives_a_legacy_console_encoding(self):
        env = dict(os.environ, PYTHONIOENCODING="cp1252")
        done = subprocess.run([sys.executable, "-B", str(SCRIPT), str(self.docs), "--only", "MX"],
                              env=env, capture_output=True, timeout=60)
        self.assertEqual(done.returncode, 1, done.stderr)
        self.assertIn("S-3 × NS = 2", done.stdout.decode("utf-8"))

    def test_never_writes_to_the_docs(self):
        before = {p: p.stat().st_mtime for p in self.docs.rglob("*")}
        run(str(self.docs))
        run("terms", "poll", "--docs", str(self.docs))
        after = {p: p.stat().st_mtime for p in self.docs.rglob("*")}
        self.assertEqual(before, after)


class SharedSnippet(TraceCase):
    """The snippet in scripts/shared/trace.md, run as written, from a project root."""

    def snippet(self) -> str:
        text = SECTION.read_text(encoding="utf-8")
        match = re.search(r"```bash\n(.*?)```", text, re.DOTALL)
        self.assertIsNotNone(match, f"no bash block in {SECTION.name}")
        return match.group(1)

    def run_snippet(self, home: Path) -> tuple[int, str]:
        # posix_shell, not shutil.which: on Windows `bash` may be the WSL
        # launcher, which would run against the WSL user's real home.
        shell = posix_shell("sh") or posix_shell("bash")
        if not shell:
            self.skipTest("no POSIX shell")
        env = dict(os.environ, HOME=home.as_posix())
        done = subprocess.run([shell, "-c", self.snippet()], cwd=self.tmp, capture_output=True,
                              env=posix_env(shell, env), timeout=60)
        return done.returncode, (done.stdout + done.stderr).decode("utf-8", errors="replace")

    def test_snippet_runs_the_installed_script(self):
        home = self.tmp / "home"
        installed = home / ".claude" / "skills" / "restack-trace"
        shutil.copytree(ROOT / "skills" / "restack-trace", installed)
        code, out = self.run_snippet(home)
        self.assertEqual(code, 1, out)                    # the fixture has items
        self.assertIn("trace: docs", out)
        self.assertIn("A worklist, not a verdict", out)

    def test_snippet_without_the_script_says_so(self):
        code, out = self.run_snippet(self.tmp / "empty-home")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.strip(), "trace unavailable (script or Python missing): do the checks by hand")


@unittest.skipUnless(shutil.which("git"), "git is required")
class GitDates(TraceCase):

    def git(self, *args: str, when: str | None = None) -> None:
        env = dict(os.environ)
        if when:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when + "T12:00:00"
        subprocess.run(GIT + list(args), cwd=self.tmp, env=env, check=True, capture_output=True)

    def test_commit_dates_win_over_mtimes(self):
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "fixture", when="2026-04-25")
        # The commit says the HLD changed after ADR-0003, whatever its mtime.
        code, out = run("scan", str(self.docs), "--only", "KO", "--dates", "git")
        self.assertIn("git commit times", out)
        self.assertNotIn("architecture/HLD.md was 'updated'", out)

    def test_uncommitted_change_uses_mtime(self):
        self.git("init", "-q")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "fixture", when="2026-03-15")
        code, out = run("scan", str(self.docs), "--only", "KO", "--dates", "git")
        self.assertIn("HLD.md was 'updated', but it last changed 2026-03-15", out)
        dep = self.docs / "deployment" / "DEPLOYMENT.md"
        dep.write_text(dep.read_text(encoding="utf-8") + "\nEdited.\n", encoding="utf-8")
        os.utime(dep, (stamp("2026-04-03"),) * 2)
        code, out = run("scan", str(self.docs), "--only", "KO", "--dates", "git")
        self.assertNotIn("DEPLOYMENT.md was", out)

    def test_git_mode_outside_a_work_tree_is_an_error(self):
        code, out = run("scan", str(self.docs), "--dates", "git")
        self.assertNotEqual(code, 0)
        self.assertIn("not inside a git work tree", out)


if __name__ == "__main__":
    unittest.main()
