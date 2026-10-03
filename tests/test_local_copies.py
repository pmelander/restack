#!/usr/bin/env python3
"""Tests for skills/restack-upgrade/scripts/local_copies.py and its session-open line (ADR-024).

Each case builds a scratch project with a `.claude` folder holding old ReStack
copies and look-alikes that must be left alone, and a scratch ~/.restack
(RESTACK_STATE_DIR). The installed skill set the copies are compared against
is this repository's `skills/`, the directory the script sits in.

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "restack-upgrade" / "scripts"
LOCAL = SCRIPTS / "local_copies.py"
UPDATE = SCRIPTS / "update_check.py"


def load(name: str, path: Path):
    previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def skill(root: Path, name: str, text: str) -> None:
    d = root / ".claude" / "skills" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(text, encoding="utf-8")


class LocalCopies(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="restack-local-"))
        self.project = self.tmp / "project"
        self.state = self.tmp / "state"
        self.state.mkdir()
        self.home = self.tmp / "home"
        (self.home / ".claude" / "skills").mkdir(parents=True)
        p = self.project
        # Old ReStack copies, in each way one can be recognised.
        skill(p, "journey", "---\ndescription: old\n---\n\n# Architect's Journey\n\nOrchestrate.\n")
        skill(p, "adr", "---\ndescription: decisions\n---\n\n# ADR Builder\n\nRecord the residual it implements.\n")
        skill(p, "restack-trace", "---\nname: restack-trace\nversion: 0.9.0\n---\n\n# Document Trace\n")
        (p / ".claude" / "commands").mkdir(parents=True)
        (p / ".claude" / "commands" / "stressor.md").write_text("Walk each path against stressors.\n",
                                                                 encoding="utf-8")
        # Look-alikes that must be left alone.
        skill(p, "excel", "---\ndescription: our own spreadsheet helper\n---\n\n# Sheets\n\nNo method here.\n")
        skill(p, "md2pdf", "---\ndescription: pdf\n---\n\n# md2pdf\n\nresiduals, stressors\n")
        (p / ".claude" / "skills" / "README.md").write_text("notes\n", encoding="utf-8")
        (p / "commands").mkdir()
        (p / "commands" / "journey.md").write_text("# Architect's Journey\n", encoding="utf-8")
        self.lc = load("local_copies", LOCAL)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def env(self, **extra: str) -> dict:
        # A scratch home, so the profile check never reads the real ~/.claude.
        env = dict(os.environ, RESTACK_STATE_DIR=str(self.state), HOME=str(self.home),
                   USERPROFILE=str(self.home), **extra)
        if "RESTACK_UPDATE_CHECK" not in extra:
            env.pop("RESTACK_UPDATE_CHECK", None)
        return env

    def run_script(self, script: Path, *args: str, cwd: Path | None = None, **env) -> tuple[int, str]:
        done = subprocess.run([sys.executable, "-B", str(script), *args], cwd=cwd or self.project,
                              env=self.env(**env), capture_output=True, timeout=60)
        return done.returncode, (done.stdout + done.stderr).decode("utf-8", "replace")

    # --- finding -------------------------------------------------------------

    def test_finds_each_kind_of_copy(self):
        found = {c["rel"]: c["why"] for c in self.lc.find(self.project)}
        self.assertEqual(set(found), {".claude/skills/journey", ".claude/skills/adr",
                                      ".claude/skills/restack-trace", ".claude/commands/stressor.md"})
        self.assertIn('same title as /restack-journey ("Architect\'s Journey")', found[".claude/skills/journey"])
        self.assertIn("residuality vocabulary", found[".claude/skills/adr"])
        self.assertIn("restack-* copy", found[".claude/skills/restack-trace"])

    def test_leaves_look_alikes_and_other_tools_alone(self):
        rels = {c["rel"] for c in self.lc.find(self.project)}
        self.assertNotIn(".claude/skills/excel", rels)          # shares a name, not the content
        self.assertNotIn(".claude/skills/md2pdf", rels)         # not a ReStack skill
        self.assertFalse(any(r.startswith("commands/") for r in rels))   # OpenCode, not Claude Code

    def test_list_names_them_and_exits_one(self):
        code, out = self.run_script(LOCAL, "list")
        self.assertEqual(code, 1, out)
        self.assertIn("4 ReStack skill copies", out)
        self.assertIn(".claude/skills/restack-trace  (a restack-* copy inside the project, v0.9.0; "
                      "replaced by /restack-trace)", out)

    def test_project_without_copies(self):
        clean = self.tmp / "clean"
        (clean / ".claude" / "skills").mkdir(parents=True)
        code, out = self.run_script(LOCAL, "list", "--project", str(clean))
        self.assertEqual(code, 0)
        self.assertIn("No ReStack skill copies", out)
        self.assertIsNone(self.lc.session_line(clean))
        self.assertIsNone(self.lc.session_line(self.tmp / "nothing-here"))

    # --- retiring ------------------------------------------------------------

    def test_retire_is_a_dry_run_by_default(self):
        before = sorted(p.relative_to(self.project).as_posix() for p in self.project.rglob("*"))
        code, out = self.run_script(LOCAL, "retire", "--date", "2026-10-03")
        self.assertEqual(code, 0, out)
        self.assertIn("Would move 4 copies", out)
        self.assertIn("Dry run: nothing moved", out)
        self.assertEqual(before, sorted(p.relative_to(self.project).as_posix() for p in self.project.rglob("*")))

    def test_retire_moves_and_leaves_an_undo_note(self):
        code, out = self.run_script(LOCAL, "retire", "--yes", "--date", "2026-10-03")
        self.assertEqual(code, 0, out)
        retired = self.project / ".claude" / "skills-retired-2026-10-03"
        self.assertTrue((retired / "skills" / "journey" / "SKILL.md").is_file())
        self.assertTrue((retired / "commands" / "stressor.md").is_file())
        self.assertFalse((self.project / ".claude" / "skills" / "journey").exists())
        self.assertTrue((self.project / ".claude" / "skills" / "excel").is_dir())     # untouched
        self.assertTrue((self.project / ".claude" / "skills" / "md2pdf").is_dir())
        readme = (retired / "README.md").read_text(encoding="utf-8")
        self.assertIn("To restore one, move it back", readme)
        self.assertIn(".claude/skills/journey -> .claude/skills-retired-2026-10-03/skills/journey", readme)
        self.assertEqual(self.lc.find(self.project), [])
        self.assertIn("nothing to retire", self.run_script(LOCAL, "retire", "--yes")[1])

    def test_retire_never_overwrites_an_earlier_retirement(self):
        self.run_script(LOCAL, "retire", "--yes", "--date", "2026-10-03")
        skill(self.project, "journey", "# Architect's Journey\n")
        self.run_script(LOCAL, "retire", "--yes", "--date", "2026-10-03")
        retired = self.project / ".claude" / "skills-retired-2026-10-03" / "skills"
        self.assertTrue((retired / "journey").is_dir())
        self.assertTrue((retired / "journey-2").is_dir())

    # --- the session-open line ----------------------------------------------

    def test_check_prints_the_line_without_install_or_network(self):
        code, out = self.run_script(UPDATE, "check")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "ReStack: this project has 4 old ReStack skill copies in .claude "
                                      "(adr, journey, restack-trace, stressor) that load beside the "
                                      "installed restack-* skills: /restack-upgrade retire-local")
        self.assertFalse((SCRIPTS / "__pycache__").exists())

    def test_line_is_shown_once_a_day_per_project(self):
        self.assertTrue(self.run_script(UPDATE, "check")[1].strip())
        self.assertEqual(self.run_script(UPDATE, "check")[1].strip(), "")
        other = self.tmp / "other"
        skill(other, "journey", "# Architect's Journey\n")
        self.assertIn("1 old ReStack skill copy", self.run_script(UPDATE, "check", cwd=other)[1])
        update = load("update_check", UPDATE)
        os.environ["RESTACK_STATE_DIR"] = str(self.state)
        try:
            self.assertIsNotNone(update.local_notice(time.time() + 25 * 3600, self.project))
        finally:
            os.environ.pop("RESTACK_STATE_DIR", None)

    # --- the user profile (installs from before the restack- prefix) --------

    def profile_copies(self):
        skill(self.home, "stressor", "# Stressor Analysis\n")
        skill(self.home, "restack-stressor", "---\nname: restack-stressor\n---\n\n# Stressor Analysis\n")

    def test_profile_counts_unprefixed_copies_never_the_install(self):
        self.profile_copies()
        code, out = self.run_script(LOCAL, "list", "--profile")
        self.assertEqual(code, 1, out)
        self.assertIn(".claude/skills/stressor", out)
        self.assertNotIn("restack-stressor  (", out)
        self.assertIn("retire-local --profile", out)

    def test_profile_line_is_separate_and_throttled_on_its_own(self):
        self.profile_copies()
        out = self.run_script(UPDATE, "check")[1].strip().splitlines()
        self.assertEqual(len(out), 2, out)
        self.assertTrue(out[1].startswith("ReStack: your profile has 1 old ReStack skill copy in ~/.claude"))
        other = self.tmp / "other"
        other.mkdir()
        self.assertEqual(self.run_script(UPDATE, "check", cwd=other)[1].strip(), "")   # profile already shown today

    def test_retire_profile(self):
        self.profile_copies()
        code, out = self.run_script(LOCAL, "retire", "--profile", "--yes", "--date", "2026-10-03")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.home / ".claude" / "skills-retired-2026-10-03" / "skills" / "stressor").is_dir())
        self.assertTrue((self.home / ".claude" / "skills" / "restack-stressor").is_dir())

    def test_opt_out_silences_it(self):
        code, out = self.run_script(UPDATE, "check", RESTACK_UPDATE_CHECK="off")
        self.assertEqual((code, out.strip()), (0, ""))

    def test_status_lists_them(self):
        code, out = self.run_script(UPDATE, "status")
        self.assertEqual(code, 0, out)
        self.assertIn("local:      4 old ReStack skill copies", out)
        self.assertIn(".claude/commands/stressor.md (a ReStack skill's name and residuality vocabulary)", out)


if __name__ == "__main__":
    unittest.main()
