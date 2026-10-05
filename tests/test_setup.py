#!/usr/bin/env python3
"""Tests for setup and setup.ps1 (ADR-019, and the mods of ADR-029).

The install is always a copy in the user profile: $HOME/.claude/skills. It must
not depend on the checkout it came from, must replace a link left by an old
symlinked install without deleting what the link points at, and must record
where releases come from so /restack-upgrade needs no checkout.

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
DEFAULT_SOURCE = "https://github.com/pmelander/restack.git"
REMOVED = "removed in ReStack 2.7.0"

GIT = ["git", "-c", "user.name=restack-test", "-c", "user.email=test@example.invalid",
       "-c", "init.defaultBranch=main"]


def make_link(link: Path, target: Path) -> str:
    """A directory link of the kind an old --symlink install left behind.

    A symbolic link where the OS allows one. Windows without Developer Mode or
    elevation does not, so a junction stands in: Remove-Item -Recurse follows
    it into the target exactly as it follows a symbolic link, which is the
    hazard the tests exist to catch.
    """
    try:
        os.symlink(target, link, target_is_directory=True)
        return "symlink"
    except OSError:
        if os.name != "nt":
            raise unittest.SkipTest("cannot create a directory link here")
    import _winapi
    _winapi.CreateJunction(str(target), str(link))
    return "junction"


def is_link(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()) or (
        os.name == "nt" and path.exists() and bool(os.lstat(path).st_file_attributes & 0x400))


class InstallCases:
    """What an installer must do. Mixed into one TestCase per installer, so
    both are held to the same cases."""

    stderr_must_be_empty = False

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="restack-setup-"))
        self.repo = self.tmp / "repo"
        skill = self.repo / "skills" / "restack-demo"
        (skill / "sections").mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: restack-demo\n---\nRead `<base>/sections/a.md`.\n", encoding="utf-8")
        (skill / "sections" / "a.md").write_text("section\n", encoding="utf-8")
        (self.repo / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        for name in ("setup", "setup.ps1"):
            shutil.copy2(ROOT / name, self.repo / name)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.default = self.home / ".claude" / "skills"
        self.record = self.home / ".restack" / "install.json"

    def tearDown(self):
        # A link must not be followed while cleaning up either.
        for entry in self.default.glob("restack-*") if self.default.exists() else []:
            if is_link(entry):
                os.rmdir(entry) if os.name == "nt" else entry.unlink()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_setup(self, *args, dry_run=False, skills_env=None, expect=0) -> str:
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_SKILLS_DIR"}
        env["HOME"] = self.home.as_posix()
        env["USERPROFILE"] = str(self.home)
        if skills_env is not None:
            env["CLAUDE_SKILLS_DIR"] = str(skills_env)
        # The point of the whole file: never the real profile.
        for key in ("HOME", "USERPROFILE"):
            self.assertTrue(Path(env[key]).resolve().is_relative_to(self.tmp.resolve()), key)
        done = subprocess.run(self.command(list(args), dry_run), cwd=self.tmp,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=self.environment(env), timeout=120)
        out, err = done.stdout.decode(errors="replace"), done.stderr.decode(errors="replace")
        self.assertEqual(done.returncode, expect, out + err)
        if expect == 0 and self.stderr_must_be_empty:
            self.assertEqual(err, "")
        return out + err

    def recorded(self) -> dict:
        # utf-8-sig: setup.ps1 writes install.json with a byte-order mark.
        return json.loads(self.record.read_text(encoding="utf-8-sig"))

    def native(self, raw: str) -> Path:
        """A path as the installer recorded it, readable from here."""
        return Path(raw)

    def installed(self) -> Path:
        return self.default / "restack-demo"

    # --- where it installs, and what it records ------------------------------

    def test_installs_a_copy_into_the_profile_and_records_it(self):
        self.run_setup()
        self.assertTrue((self.installed() / "SKILL.md").is_file())
        self.assertFalse(is_link(self.installed()), "the install is a copy, never a link")
        data = self.recorded()
        self.assertEqual(data["version"], "9.9.9")
        self.assertEqual(data["method"], "copy")
        self.assertEqual(data["source"], DEFAULT_SOURCE, "a download records the project itself")
        self.assertTrue(self.native(data["skills_dir"]).samefile(self.default))
        self.assertTrue(self.native(data["repo"]).samefile(self.repo))

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_source_is_the_checkouts_origin(self):
        subprocess.run(GIT + ["init", "-q", str(self.repo)], check=True)
        subprocess.run(GIT + ["-C", str(self.repo), "remote", "add", "origin",
                              "https://example.invalid/fork/restack.git"], check=True)
        self.run_setup()
        self.assertEqual(self.recorded()["source"], "https://example.invalid/fork/restack.git")

    def test_the_install_survives_deleting_the_checkout(self):
        self.run_setup()
        shutil.rmtree(self.repo)
        self.assertTrue((self.installed() / "SKILL.md").is_file())
        self.assertTrue((self.installed() / "sections" / "a.md").is_file())

    def test_rerun_is_a_no_op_and_picks_up_a_section_edit(self):
        self.run_setup()
        self.assertIn("already up to date", self.run_setup())
        (self.repo / "skills" / "restack-demo" / "sections" / "a.md").write_text("edited\n", encoding="utf-8")
        self.assertIn("1 updated", self.run_setup())
        self.assertEqual((self.installed() / "sections" / "a.md").read_text(encoding="utf-8"), "edited\n")

    def test_dry_run_writes_nothing(self):
        self.run_setup(dry_run=True)
        self.assertFalse(self.default.exists() and any(self.default.iterdir()))
        self.assertFalse(self.record.exists())

    # --- removed options ------------------------------------------------------

    def test_symlink_and_target_are_refused(self):
        for args in self.removed_options():
            with self.subTest(args=args):
                out = self.run_setup(*args, expect=2)
                self.assertIn(REMOVED, out)
                self.assertFalse(self.default.exists(), "a refused run installs nothing")
                self.assertFalse(self.record.exists())

    def test_claude_skills_dir_is_ignored_and_said_so(self):
        custom = self.tmp / "custom-skills"
        out = self.run_setup(skills_env=custom)
        self.assertTrue((self.installed() / "SKILL.md").is_file())
        self.assertFalse(custom.exists())
        self.assertIn("CLAUDE_SKILLS_DIR", out)

    # --- links left by an old --symlink install -------------------------------

    def test_a_link_is_replaced_by_a_copy_and_its_target_survives(self):
        checkout = self.tmp / "old-checkout" / "restack-demo"
        checkout.mkdir(parents=True)
        (checkout / "SKILL.md").write_text("old\n", encoding="utf-8")
        (checkout / "keep.txt").write_text("the architect's work\n", encoding="utf-8")
        self.default.mkdir(parents=True)
        kind = make_link(self.installed(), checkout)

        out = self.run_setup()

        self.assertFalse(is_link(self.installed()), f"the {kind} must be replaced by a copy")
        self.assertIn("name: restack-demo", (self.installed() / "SKILL.md").read_text(encoding="utf-8"))
        self.assertTrue((checkout / "keep.txt").is_file(), f"deleting the {kind} emptied its target")
        self.assertEqual((checkout / "SKILL.md").read_text(encoding="utf-8"), "old\n")
        self.assertIn("replaced with copies", out)

    def test_a_link_to_a_skill_removed_upstream_is_unlinked_not_followed(self):
        gone = self.tmp / "old-checkout" / "restack-gone"
        gone.mkdir(parents=True)
        (gone / "keep.txt").write_text("the architect's work\n", encoding="utf-8")
        self.default.mkdir(parents=True)
        kind = make_link(self.default / "restack-gone", gone)

        out = self.run_setup()

        self.assertFalse(os.path.lexists(self.default / "restack-gone"))
        self.assertTrue((gone / "keep.txt").is_file(), f"removing the {kind} emptied its target")
        self.assertIn("remove", out)

    def test_dry_run_leaves_a_link_alone(self):
        checkout = self.tmp / "old-checkout" / "restack-demo"
        checkout.mkdir(parents=True)
        (checkout / "SKILL.md").write_text("old\n", encoding="utf-8")
        self.default.mkdir(parents=True)
        make_link(self.installed(), checkout)
        out = self.run_setup(dry_run=True)
        self.assertTrue(is_link(self.installed()))
        self.assertIn("would be replaced with copies", out)

    # --- mods (ADR-029) ------------------------------------------------------

    def add_mod(self, name="restack-demoview", hooks=True) -> Path:
        """A mod in the repository: a manifest, hooks.json, a module, and the
        .claude-plugin/types/ Claude Code writes on a development load."""
        mod = self.repo / "mods" / name
        (mod / ".claude-plugin" / "types").mkdir(parents=True)
        (mod / ".claude-plugin" / "plugin.json").write_text(f'{{ "name": "{name}" }}\n', encoding="utf-8")
        (mod / ".claude-plugin" / "types" / "core.d.ts").write_text("// generated\n", encoding="utf-8")
        (mod / "hooks").mkdir()
        if hooks:
            (mod / "hooks" / "hooks.json").write_text('{ "modules": ["./register.ts"] }\n', encoding="utf-8")
        (mod / "hooks" / "register.ts").write_text("export const register = () => {}\n", encoding="utf-8")
        return mod

    def mod_installed(self, name="restack-demoview") -> Path:
        return self.default / name

    def test_a_mod_is_not_installed_without_asking(self):
        self.add_mod()
        out = self.run_setup()
        self.assertFalse(self.mod_installed().exists())
        self.assertIs(self.recorded()["mods"], False)
        self.assertIn(self.mods_flag(), out, "a plain run says how to add the mods")

    def test_mods_installs_beside_the_skills_without_the_generated_types(self):
        self.add_mod()
        self.run_setup(self.mods_flag())
        self.assertTrue((self.mod_installed() / ".claude-plugin" / "plugin.json").is_file())
        self.assertTrue((self.mod_installed() / "hooks" / "register.ts").is_file())
        self.assertFalse((self.mod_installed() / ".claude-plugin" / "types").exists(),
                         "the types Claude Code generates are never installed")
        self.assertTrue((self.installed() / "SKILL.md").is_file(), "the skills install as before")
        self.assertIs(self.recorded()["mods"], True)

    def test_a_plain_rerun_keeps_and_refreshes_an_installed_mod(self):
        mod = self.add_mod()
        self.run_setup(self.mods_flag())
        self.assertIn("already up to date", self.run_setup())
        (mod / "hooks" / "register.ts").write_text("export const register = () => { /* edited */ }\n",
                                                  encoding="utf-8")
        self.assertIn("1 updated", self.run_setup())
        self.assertIn("edited", (self.mod_installed() / "hooks" / "register.ts").read_text(encoding="utf-8"))

    def test_generated_types_in_the_install_are_not_a_change(self):
        self.add_mod()
        self.run_setup(self.mods_flag())
        written = self.mod_installed() / ".claude-plugin" / "types"
        written.mkdir()
        (written / "core.d.ts").write_text("// written by a session\n", encoding="utf-8")
        self.assertIn("already up to date", self.run_setup())

    def test_no_mods_removes_the_mod_and_is_remembered(self):
        self.add_mod()
        self.run_setup(self.mods_flag())
        out = self.run_setup(self.no_mods_flag())
        self.assertFalse(os.path.lexists(self.mod_installed()))
        self.assertIn("remove", out)
        self.assertIs(self.recorded()["mods"], False)
        self.run_setup()
        self.assertFalse(self.mod_installed().exists(), "a plain run after --no-mods adds nothing")
        self.assertTrue((self.installed() / "SKILL.md").is_file(), "the skills stay")

    def test_a_mod_removed_upstream_is_removed(self):
        mod = self.add_mod()
        self.run_setup(self.mods_flag())
        shutil.rmtree(mod)
        self.assertIn("remove", self.run_setup())
        self.assertFalse(os.path.lexists(self.mod_installed()))

    def test_without_a_record_an_installed_mod_counts_as_chosen(self):
        self.add_mod()
        self.run_setup(self.mods_flag())
        self.record.unlink()
        self.run_setup()
        self.assertTrue((self.mod_installed() / ".claude-plugin" / "plugin.json").is_file())
        self.assertIs(self.recorded()["mods"], True)

    def test_a_broken_mod_is_refused(self):
        self.add_mod(hooks=False)
        out = self.run_setup(self.mods_flag(), expect=1)
        self.assertIn("broken mod", out)
        self.assertFalse(self.mod_installed().exists())
        self.assertFalse(self.record.exists(), "a refused run records nothing")

    def test_a_mod_named_like_a_skill_is_refused(self):
        self.add_mod(name="restack-demo")
        out = self.run_setup(self.mods_flag(), expect=1)
        self.assertIn("name of a skill", out)
        self.assertFalse(self.record.exists())

    def test_mods_and_no_mods_together_are_refused(self):
        self.add_mod()
        out = self.run_setup(self.mods_flag(), self.no_mods_flag(), expect=2)
        self.assertIn("contradict", out)
        self.assertFalse(self.default.exists())

    def test_dry_run_with_mods_writes_nothing(self):
        self.add_mod()
        out = self.run_setup(self.mods_flag(), dry_run=True)
        self.assertIn("restack-demoview", out)
        self.assertFalse(self.default.exists() and any(self.default.iterdir()))
        self.assertFalse(self.record.exists())


class PosixSetup(InstallCases, unittest.TestCase):
    """./setup under sh."""

    stderr_must_be_empty = True             # catches a test that rejects a construct

    @classmethod
    def setUpClass(cls):
        cls.shell = posix_shell("sh")
        if not cls.shell:
            raise unittest.SkipTest("no POSIX sh")

    def command(self, args, dry_run):
        cmd = [self.shell, (self.repo / "setup").as_posix(), "--quiet", *args]
        if dry_run:
            cmd.append("--dry-run")
        return cmd

    def removed_options(self):
        return [["--symlink"], ["--target", (self.tmp / "elsewhere").as_posix()]]

    def mods_flag(self):
        return "--mods"

    def no_mods_flag(self):
        return "--no-mods"

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

    @unittest.skipIf(os.name == "nt", "Windows cannot name a directory with a double quote")
    def test_paths_with_backslashes_and_quotes_are_valid_json(self):
        # setup wrote values raw into the JSON, so C:\Users\... recorded an
        # invalid \U escape, and the update check (ADR-016) read the record as
        # unreadable and stayed silent.
        odd = self.tmp / 'back\\slash "quoted" repo'
        shutil.move(str(self.repo), str(odd))
        self.repo = odd
        self.run_setup()
        self.assertTrue(self.native(self.recorded()["repo"]).samefile(odd))


@unittest.skipUnless(os.name == "nt", "setup.ps1 is the Windows-native installer")
class PowerShellSetup(InstallCases, unittest.TestCase):
    """setup.ps1 under Windows PowerShell."""

    @classmethod
    def setUpClass(cls):
        cls.shell = powershell()
        if not cls.shell:
            raise unittest.SkipTest("no PowerShell")

    def command(self, args, dry_run):
        cmd = [self.shell, "-NoProfile", "-NonInteractive", "-File", str(self.repo / "setup.ps1"), "-Quiet", *args]
        if dry_run:
            cmd.append("-DryRun")
        return cmd

    def removed_options(self):
        return [["-Symlink"], ["-Target", str(self.tmp / "elsewhere")]]

    def mods_flag(self):
        return "-Mods"

    def no_mods_flag(self):
        return "-NoMods"

    def environment(self, env):
        return env


if __name__ == "__main__":
    unittest.main()
