#!/usr/bin/env python3
"""Tests for skills/restack-upgrade/scripts/update_check.py (ADR-016).

Every case runs against a scratch ~/.restack (RESTACK_STATE_DIR), a scratch
skills directory, and a local bare repository standing in for the recorded
source. Nothing touches the network or the real ~/.restack.

Since 2.7.0 the check needs no checkout (ADR-019): it fetches the recorded
source into a cache in the state directory. The checkout is used only for a
record written before 2.7.0, which has no source.

    python -m unittest discover -s tests -v

Standard library only, like everything else the toolkit runs.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shells import posix_env, posix_shell  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "restack-upgrade" / "scripts" / "update_check.py"
SECTION = ROOT / "scripts" / "shared" / "update-check.md"

HINT = "(snooze a week: /restack-upgrade snooze)"

# A developer's global config must not leak into the fixture repositories.
GIT = ["git", "-c", "user.name=restack-test", "-c", "user.email=test@example.invalid",
       "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", "-c", "core.autocrlf=false"]


def git(*args: str, cwd: Path | None = None) -> str:
    done = subprocess.run(GIT + list(args), cwd=cwd, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return done.stdout.decode().strip()


def load_module():
    # No __pycache__ inside a shipped skill: setup copies the whole directory.
    previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec = importlib.util.spec_from_file_location("update_check", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


@unittest.skipUnless(shutil.which("git"), "git is required")
class UpdateCheck(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="restack-uc-"))
        self.origin = self.tmp / "origin.git"
        self.seed = self.tmp / "seed"
        self.checkout = self.tmp / "checkout"
        self.home = self.tmp / "home"
        self.skills = self.home / ".claude" / "skills"
        self.state = self.tmp / "state"

        git("init", "-q", "--bare", str(self.origin))
        git("symbolic-ref", "HEAD", "refs/heads/main", cwd=self.origin)
        git("clone", "-q", str(self.origin), str(self.seed))
        git("checkout", "-q", "-B", "main", cwd=self.seed)
        self.publish("2.4.0")
        git("clone", "-q", str(self.origin), str(self.checkout))

        # The script refuses to report on an install it is not running from,
        # so install it where install.json says the skills are.
        installed = self.skills / "restack-upgrade" / "scripts"
        installed.mkdir(parents=True)
        shutil.copy2(SCRIPT, installed / SCRIPT.name)
        self.script = installed / SCRIPT.name

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- fixtures ------------------------------------------------------------

    def publish(self, version: str):
        (self.seed / "VERSION").write_text(version + "\n", encoding="utf-8")
        git("add", "VERSION", cwd=self.seed)
        git("commit", "-q", "-m", f"v{version}", cwd=self.seed)
        git("push", "-q", "origin", "main", cwd=self.seed)

    NO_SOURCE = object()

    def install(self, version="2.4.0", method="copy", repo=None, skills_dir=None, bom=False, source=None):
        """A record as setup writes it. source=NO_SOURCE writes one from before 2.7.0."""
        self.state.mkdir(exist_ok=True)
        data = {"version": version}
        if source is not self.NO_SOURCE:
            data["source"] = str(source or self.origin)
        data.update({
            "repo": str(repo or self.checkout),
            "skills_dir": str(skills_dir or self.skills),
            "method": method,
            "installed_at": "2026-10-02T06:43:01Z",
        })
        text = json.dumps(data, indent=4)
        (self.state / "install.json").write_text(("\ufeff" if bom else "") + text, encoding="utf-8")

    def run_uc(self, *args, env=None, script=None):
        environment = {k: v for k, v in os.environ.items() if k != "RESTACK_UPDATE_CHECK"}
        environment["RESTACK_STATE_DIR"] = str(self.state)
        environment.update(env or {})
        done = subprocess.run([sys.executable, str(script or self.script), *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment, timeout=60)
        if not args or args[0] == "check":
            self.assertEqual(done.returncode, 0, "the check must always exit 0")
            self.assertEqual(done.stderr, b"", "the check must never write to stderr")
        self.last_returncode = done.returncode
        return done.stdout.decode().strip()

    def saved(self) -> dict:
        path = self.state / "update-check.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def age_last_check(self, seconds: int):
        state = self.saved()
        state["checked_at"] = int(time.time()) - seconds
        (self.state / "update-check.json").write_text(json.dumps(state), encoding="utf-8")

    def fetched(self) -> str | None:
        """What the check last fetched into its cache, or None if it never fetched."""
        cache = self.state / "upstream.git"
        if not cache.exists():
            return None
        return git("rev-parse", "refs/remotes/upstream/main", cwd=cache)

    # --- copy installs -------------------------------------------------------

    def test_update_available(self):
        self.install("2.4.0")
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(),
                         f"ReStack v2.5.0 available (installed v2.4.0): /restack-upgrade  {HINT}")
        self.assertEqual(self.saved()["result"], "available")

    def test_up_to_date_is_silent(self):
        self.install("2.4.0")
        self.assertEqual(self.run_uc(), "")
        self.assertEqual(self.saved()["result"], "current")

    def test_ahead_of_remote_is_silent(self):
        self.install("2.6.0")
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(), "")
        self.assertEqual(self.saved()["result"], "ahead")

    def test_numeric_not_lexical_comparison(self):
        self.install("2.9.0")
        self.publish("2.10.0")
        self.assertIn("v2.10.0 available", self.run_uc())

    def test_unreadable_remote_version_is_silent(self):
        self.install("2.4.0")
        self.publish("<<<<<<< HEAD")
        self.assertEqual(self.run_uc(), "")
        self.assertEqual(self.saved()["result"], "unreadable-version")

    def test_offline_is_silent_and_throttled(self):
        self.install("2.4.0", source=self.tmp / "nowhere.git")
        self.assertEqual(self.run_uc(), "")
        self.assertEqual(self.saved()["result"], "offline")
        self.assertIn("checked_at", self.saved(), "an offline attempt still counts for the day")

    def test_hanging_remote_is_cut_off(self):
        # ext:: runs a command as the transport: this one never answers. git
        # refuses ext:: by default, so the test allows it in the cache, which
        # it creates the way the script would.
        py = sys.executable.replace("\\", "/").replace(" ", "% ")
        self.install("2.4.0", source=f"ext::{py} -c import% time;time.sleep(30)")
        git("init", "-q", "--bare", str(self.state / "upstream.git"))
        git("config", "protocol.ext.allow", "always", cwd=self.state / "upstream.git")
        start = time.time()
        self.assertEqual(self.run_uc(), "")
        elapsed = time.time() - start
        module = load_module()
        self.assertLess(elapsed, module.FETCH_TIMEOUT + 4,
                        "a hung transport must not hold the session open past the timeout")
        self.assertEqual(self.saved()["result"], "offline")

    # --- missing or unusable state -------------------------------------------

    def test_no_install_json_is_silent_and_writes_nothing(self):
        self.assertEqual(self.run_uc(), "")
        self.assertFalse(self.state.exists(), "no install means nothing to record")

    def test_malformed_install_json_is_silent(self):
        self.state.mkdir()
        (self.state / "install.json").write_text("{not json", encoding="utf-8")
        self.assertEqual(self.run_uc(), "")

    def test_install_json_with_bom(self):
        # setup.ps1 writes install.json through Out-File -Encoding utf8.
        self.install("2.4.0", bom=True)
        self.publish("2.5.0")
        self.assertIn("v2.5.0 available", self.run_uc())

    def test_works_after_the_checkout_is_deleted(self):
        # Most installers delete their clone after setup. The check must not
        # depend on it: it fetches the recorded source into its own cache.
        self.install("2.4.0")

        def writable(func, path, _exc):         # git marks objects read-only on Windows
            os.chmod(path, 0o700)
            func(path)
        shutil.rmtree(self.checkout, onerror=writable)
        self.assertFalse(self.checkout.exists())
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(),
                         f"ReStack v2.5.0 available (installed v2.4.0): /restack-upgrade  {HINT}")
        self.assertIsNotNone(self.fetched(), "fetched into the cache, not a checkout")

    def test_record_from_before_2_7_uses_its_checkouts_origin(self):
        self.install("2.4.0", source=self.NO_SOURCE)
        self.publish("2.5.0")
        self.assertIn("v2.5.0 available", self.run_uc())

    def test_no_source_and_no_checkout_is_silent(self):
        download = self.tmp / "download"
        download.mkdir()
        (download / "VERSION").write_text("2.4.0\n", encoding="utf-8")
        self.install("2.4.0", repo=download, source=self.NO_SOURCE)
        self.assertEqual(self.run_uc(), "")
        self.assertEqual(self.saved(), {})
        self.assertIn("source unknown", self.run_uc("status"))

    def test_a_source_that_looks_like_an_option_is_refused(self):
        self.install("2.4.0", source="--upload-pack=touch pwned")
        self.assertEqual(self.run_uc(), "")
        self.assertIsNone(self.fetched())

    def test_install_json_for_another_install_is_silent(self):
        # setup --target <scratch> rewrote install.json for the scratch target
        # until 2.5.1, and a record from then is still on disk somewhere.
        other = self.tmp / "scratch-skills"
        (other / "restack-upgrade").mkdir(parents=True)
        self.install("2.4.0", skills_dir=other)
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(), "")
        self.assertIn("not this install", self.run_uc("status"))

    @unittest.skipUnless(os.name == "nt", "MSYS paths exist only on Windows")
    def test_msys_paths_from_git_bash_setup(self):
        def msys(p: Path) -> str:
            drive, rest = p.drive, p.as_posix()[len(p.drive):]
            return f"/{drive[0].lower()}{rest}"
        self.install("2.4.0", repo=msys(self.checkout), skills_dir=msys(self.skills), source=self.NO_SOURCE)
        self.publish("2.5.0")
        self.assertIn("v2.5.0 available", self.run_uc())

    # --- throttle ------------------------------------------------------------

    def test_throttled_within_a_day(self):
        self.install("2.4.0")
        self.publish("2.5.0")
        self.assertIn("v2.5.0 available", self.run_uc())
        before = self.fetched()
        self.publish("2.6.0")
        self.assertEqual(self.run_uc(), "", "a second session open the same day says nothing")
        self.assertEqual(self.fetched(), before, "and fetches nothing")

    def test_throttle_expires_after_a_day(self):
        self.install("2.4.0")
        self.publish("2.5.0")
        self.run_uc()
        self.age_last_check(25 * 3600)
        self.assertIn("v2.5.0 available", self.run_uc())

    def test_future_timestamp_does_not_silence_forever(self):
        self.install("2.4.0")
        self.publish("2.5.0")
        self.run_uc()
        self.age_last_check(-10 * 86400)
        self.assertIn("v2.5.0 available", self.run_uc())

    # --- snooze --------------------------------------------------------------

    def test_snooze_holds_until_a_newer_release(self):
        self.install("2.4.0")
        self.publish("2.5.0")
        self.run_uc()
        self.assertIn("Snoozed the v2.5.0 notice for 7 day(s)", self.run_uc("snooze"))
        self.age_last_check(25 * 3600)
        self.assertEqual(self.run_uc(), "", "snoozed: the same version stays quiet")
        self.assertIn("snoozed:    v2.5.0", self.run_uc("status"))
        self.publish("2.6.0")
        self.age_last_check(25 * 3600)
        self.assertIn("v2.6.0 available", self.run_uc(), "a newer release breaks the snooze")

    def test_snooze_expires(self):
        self.install("2.4.0")
        self.publish("2.5.0")
        self.run_uc()
        self.run_uc("snooze", "1")
        state = self.saved()
        state["snoozed_until"] = int(time.time()) - 1
        state["checked_at"] = int(time.time()) - 25 * 3600
        (self.state / "update-check.json").write_text(json.dumps(state), encoding="utf-8")
        self.assertIn("v2.5.0 available", self.run_uc())

    def test_snooze_with_nothing_pending(self):
        self.install("2.4.0")
        self.run_uc()
        self.assertEqual(self.run_uc("snooze"), "Nothing to snooze: no update notice is pending.")

    def test_snooze_rejects_bad_days(self):
        self.install("2.4.0")
        self.run_uc("snooze", "0")
        self.assertEqual(self.last_returncode, 2)
        self.run_uc("snooze", "soon")
        self.assertEqual(self.last_returncode, 2)

    # --- opt-out -------------------------------------------------------------

    def test_opted_out_by_config_fetches_nothing(self):
        self.install("2.4.0")
        self.assertIn("Update check off", self.run_uc("off"))
        self.assertEqual(json.loads((self.state / "config.json").read_text()), {"update_check": False})
        before = self.fetched()
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(), "")
        self.assertEqual(self.fetched(), before, "opted out means no fetch at all")
        self.assertNotIn("checked_at", self.saved())
        self.assertIn("setting:    off", self.run_uc("status"))

    def test_opted_out_by_environment(self):
        self.install("2.4.0")
        before = self.fetched()
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(env={"RESTACK_UPDATE_CHECK": "off"}), "")
        self.assertEqual(self.fetched(), before)

    def test_environment_wins_over_config_on(self):
        self.install("2.4.0")
        self.run_uc("on")
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(env={"RESTACK_UPDATE_CHECK": "0"}), "")

    def test_unreadable_config_counts_as_off(self):
        self.install("2.4.0")
        (self.state / "config.json").write_text("{update_check: false", encoding="utf-8")
        before = self.fetched()
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(), "")
        self.assertEqual(self.fetched(), before)
        self.run_uc("on")
        self.assertEqual(self.last_returncode, 1, "on must not overwrite a file it cannot read")
        self.assertEqual((self.state / "config.json").read_text(), "{update_check: false")

    def test_on_after_off(self):
        self.install("2.4.0")
        self.run_uc("off")
        self.run_uc("on")
        self.publish("2.5.0")
        self.assertIn("v2.5.0 available", self.run_uc())

    def test_config_keeps_other_keys(self):
        self.install("2.4.0")
        (self.state / "config.json").write_text('{"other": 1}', encoding="utf-8")
        self.run_uc("off")
        self.assertEqual(json.loads((self.state / "config.json").read_text()),
                         {"other": 1, "update_check": False})

    # --- symlinked installs from before 2.7.0 ---------------------------------

    def test_old_symlink_install_is_sent_to_the_upgrade(self):
        # /restack-upgrade runs setup, which replaces the links with copies, so
        # a symlinked install gets the same notice as any other (ADR-019).
        self.install("2.4.0", method="symlink", source=self.NO_SOURCE)
        self.publish("2.5.0")
        self.assertEqual(self.run_uc(),
                         f"ReStack v2.5.0 available (installed v2.4.0): /restack-upgrade  {HINT}")
        self.assertIn("replaces the links with copies", self.run_uc("status"))

    # --- failure is silent at session open, visible in status ----------------

    def test_crash_is_silent_but_reported_by_status(self):
        self.install("2.4.0")
        module = load_module()
        with mock.patch.dict(os.environ, {"RESTACK_STATE_DIR": str(self.state)}), \
                mock.patch.object(module, "check", side_effect=RuntimeError("boom")):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(module.main(["check"]), 0)
            self.assertEqual(out.getvalue(), "")
        self.assertIn("FAILED - RuntimeError: boom", self.run_uc("status"))

    def test_unknown_command(self):
        self.run_uc("upgrade")
        self.assertEqual(self.last_returncode, 2)

    # --- the snippets in the shared section, as written ----------------------

    def snippet(self, lang: str) -> str:
        text = SECTION.read_text(encoding="utf-8")
        match = re.search(rf"```{lang}\n(.*?)```", text, re.DOTALL)
        self.assertIsNotNone(match, f"no {lang} block in {SECTION.name}")
        return match.group(1)

    def test_posix_shell_snippet(self):
        self.install("2.4.0")
        self.publish("2.5.0")
        # posix_shell, not shutil.which: on Windows `bash` may be the WSL
        # launcher, which would run the snippet against the WSL user's real home.
        shells = {s: p for s in ("sh", "bash") if (p := posix_shell(s))}
        if not shells:
            self.skipTest("no POSIX shell")
        for shell, path in shells.items():
            with self.subTest(shell=shell):
                if (self.state / "update-check.json").exists():
                    self.age_last_check(25 * 3600)
                env = dict(os.environ, HOME=self.home.as_posix(), RESTACK_STATE_DIR=str(self.state))
                env.pop("RESTACK_UPDATE_CHECK", None)
                done = subprocess.run([path, "-c", self.snippet("bash")], cwd=self.tmp,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                      env=posix_env(path, env), timeout=60)
                self.assertEqual(done.stdout.decode().strip(),
                                 f"ReStack v2.5.0 available (installed v2.4.0): /restack-upgrade  {HINT}")
                self.assertEqual(done.stderr, b"")

    def test_posix_shell_snippet_without_the_script_is_silent(self):
        shutil.rmtree(self.skills / "restack-upgrade")
        shell = posix_shell("sh") or posix_shell("bash")
        if not shell:
            self.skipTest("no POSIX shell")
        env = dict(os.environ, HOME=self.home.as_posix(), RESTACK_STATE_DIR=str(self.state))
        done = subprocess.run([shell, "-c", self.snippet("bash")], cwd=self.tmp,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              env=posix_env(shell, env), timeout=60)
        self.assertEqual((done.stdout + done.stderr).decode().strip(), "")

    def test_powershell_snippet(self):
        shell = shutil.which("powershell") or shutil.which("pwsh")
        if not shell:
            self.skipTest("no PowerShell")
        self.install("2.4.0")
        self.publish("2.5.0")
        # $HOME is read-only in PowerShell, so point the snippet at the scratch home.
        code = self.snippet("powershell").replace("$HOME/", self.home.as_posix() + "/")
        env = dict(os.environ, RESTACK_STATE_DIR=str(self.state))
        env.pop("RESTACK_UPDATE_CHECK", None)
        done = subprocess.run([shell, "-NoProfile", "-NonInteractive", "-Command", code],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, timeout=120)
        self.assertEqual(done.stdout.decode().strip(),
                         f"ReStack v2.5.0 available (installed v2.4.0): /restack-upgrade  {HINT}")


if __name__ == "__main__":
    unittest.main()
