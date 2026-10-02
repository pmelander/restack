#!/usr/bin/env python3
"""Tests for setup and setup.ps1: which runs write ~/.restack/install.json.

The record describes one install, the one a bare setup maintains, because that
is what /restack-upgrade re-runs. A --target run into a scratch directory must
leave it alone (ADR-011, Notes).

Each case copies the installer into a scratch repository holding one skill and
runs it with HOME and USERPROFILE pointed at a scratch home, so nothing touches
the real ~/.claude/skills or ~/.restack. Both installers run the same cases,
because they are meant to behave identically.

    python -m unittest discover -s tests -v

Standard library only, like everything else the toolkit runs.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shells import posix_env, posix_shell, powershell  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NOTE = "left unchanged"

# Stands in for the record of the architect's real install.
REAL_RECORD = (
    b'{\n  "version": "2.4.0",\n  "repo": "/home/architect/restack",\n'
    b'  "skills_dir": "/home/architect/.claude/skills",\n  "method": "symlink",\n'
    b'  "installed_at": "2026-10-02T06:43:01Z"\n}\n'
)


class RecordCases:
    """What an installer must do with install.json. Mixed into one TestCase
    per installer, so both are held to the same cases."""

    stderr_must_be_empty = False

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="restack-setup-"))
        self.repo = self.tmp / "repo"
        skill = self.repo / "skills" / "restack-demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: restack-demo\n---\n", encoding="utf-8")
        (self.repo / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        for name in ("setup", "setup.ps1"):
            shutil.copy2(ROOT / name, self.repo / name)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.default = self.home / ".claude" / "skills"
        self.record = self.home / ".restack" / "install.json"
        self.other = self.tmp / "scratch-skills"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_setup(self, target=None, dry_run=False, skills_env=None, cwd=None) -> str:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_SKILLS_DIR"}
        env["HOME"] = self.home.as_posix()
        env["USERPROFILE"] = str(self.home)
        if skills_env is not None:
            env["CLAUDE_SKILLS_DIR"] = skills_env.as_posix()
        # The point of the whole file: never the real profile.
        for key in ("HOME", "USERPROFILE", "CLAUDE_SKILLS_DIR"):
            if key in env:
                self.assertTrue(Path(env[key]).resolve().is_relative_to(self.tmp.resolve()), key)
        done = subprocess.run(self.command(target, dry_run), cwd=cwd or self.tmp,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=self.environment(env), timeout=120)
        out, err = done.stdout.decode(errors="replace"), done.stderr.decode(errors="replace")
        self.assertEqual(done.returncode, 0, out + err)
        if self.stderr_must_be_empty:
            self.assertEqual(err, "")
        return out

    def recorded(self) -> dict:
        # utf-8-sig: setup.ps1 writes install.json with a byte-order mark.
        return json.loads(self.record.read_text(encoding="utf-8-sig"))

    def native(self, raw: str) -> Path:
        """A path as the installer recorded it, readable from here."""
        return Path(raw)

    # --- cases ---------------------------------------------------------------

    def test_default_install_is_recorded(self):
        out = self.run_setup()
        self.assertTrue((self.default / "restack-demo" / "SKILL.md").is_file())
        data = self.recorded()
        self.assertEqual(data["version"], "9.9.9")
        self.assertEqual(data["method"], "copy")
        self.assertTrue(self.native(data["skills_dir"]).samefile(self.default))
        self.assertTrue(self.native(data["repo"]).samefile(self.repo))
        self.assertNotIn(NOTE, out)

    def test_target_elsewhere_leaves_the_record_alone(self):
        self.record.parent.mkdir()
        self.record.write_bytes(REAL_RECORD)
        out = self.run_setup(target=self.other)
        self.assertTrue((self.other / "restack-demo" / "SKILL.md").is_file())
        self.assertEqual(self.record.read_bytes(), REAL_RECORD)
        self.assertIn(NOTE, out)            # printed even under --quiet
        self.assertIn("CLAUDE_SKILLS_DIR", out)

    def test_target_elsewhere_creates_no_record(self):
        self.run_setup(target=self.other)
        self.assertFalse(self.record.parent.exists())

    def test_target_naming_the_default_is_recorded_as_the_default(self):
        self.run_setup()
        bare = self.recorded()["skills_dir"]
        spellings = {"relative": ".claude/skills", "trailing slash": self.default.as_posix() + "/"}
        if os.name == "nt":
            spellings["other case"] = self.default.as_posix().upper()
        for label, spelling in spellings.items():
            with self.subTest(spelling=label):
                self.record.unlink()
                out = self.run_setup(target=spelling, cwd=self.home)
                self.assertEqual(self.recorded()["skills_dir"], bare)
                self.assertNotIn(NOTE, out)

    def test_claude_skills_dir_is_recorded(self):
        custom = self.tmp / "custom-skills"
        out = self.run_setup(skills_env=custom)
        self.assertTrue((custom / "restack-demo" / "SKILL.md").is_file())
        self.assertTrue(self.native(self.recorded()["skills_dir"]).samefile(custom))
        self.assertNotIn(NOTE, out)

    def test_target_is_measured_against_claude_skills_dir(self):
        # A bare setup installs into CLAUDE_SKILLS_DIR, so ~/.claude/skills is
        # the one-off here.
        out = self.run_setup(target=self.default, skills_env=self.tmp / "custom-skills")
        self.assertFalse(self.record.exists())
        self.assertIn(NOTE, out)

    def test_dry_run_writes_no_record(self):
        for label, target in (("default", None), ("elsewhere", self.other)):
            with self.subTest(target=label):
                out = self.run_setup(target=target, dry_run=True)
                self.assertFalse(self.record.exists())
                self.assertEqual(NOTE in out, target is not None)


class PosixSetup(RecordCases, unittest.TestCase):
    """./setup under sh."""

    stderr_must_be_empty = True             # catches a test that rejects -ef

    @classmethod
    def setUpClass(cls):
        cls.shell = posix_shell("sh")
        if not cls.shell:
            raise unittest.SkipTest("no POSIX sh")

    def command(self, target, dry_run):
        cmd = [self.shell, (self.repo / "setup").as_posix(), "--quiet"]
        if target is not None:
            cmd += ["--target", target.as_posix() if isinstance(target, Path) else target]
        if dry_run:
            cmd.append("--dry-run")
        return cmd

    def environment(self, env):
        return posix_env(self.shell, env)

    def native(self, raw: str) -> Path:
        # Git Bash records its own view of a path: /c/Users/..., or /tmp/...
        # for the Windows temp directory, which only its cygpath can map back.
        cygpath = Path(self.shell).parent / "cygpath.exe"
        if os.name == "nt" and raw.startswith("/") and cygpath.is_file():
            done = subprocess.run([str(cygpath), "-m", raw], stdout=subprocess.PIPE, check=True, timeout=30)
            return Path(done.stdout.decode().strip())
        return Path(raw)


@unittest.skipUnless(os.name == "nt", "setup.ps1 is the Windows-native installer")
class PowerShellSetup(RecordCases, unittest.TestCase):
    """setup.ps1 under Windows PowerShell."""

    @classmethod
    def setUpClass(cls):
        cls.shell = powershell()
        if not cls.shell:
            raise unittest.SkipTest("no PowerShell")

    def command(self, target, dry_run):
        cmd = [self.shell, "-NoProfile", "-NonInteractive", "-File", str(self.repo / "setup.ps1"), "-Quiet"]
        if target is not None:
            cmd += ["-Target", str(target)]
        if dry_run:
            cmd.append("-DryRun")
        return cmd

    def environment(self, env):
        return env


if __name__ == "__main__":
    unittest.main()
