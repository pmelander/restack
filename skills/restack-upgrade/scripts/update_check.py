#!/usr/bin/env python3
"""ReStack update check: one line at session open, at most once a day.

The session-opening commands (/restack-journey start and where, and
/restack-discover paths) run this through the shared section update-check.md.
/restack-upgrade runs it for snooze, off, on and status. The design is in
ADR-016.

    python update_check.py              # check: prints one line, or nothing
    python update_check.py snooze [N]   # hide the pending notice for N days (default 7)
    python update_check.py off          # opt out: writes ~/.restack/config.json
    python update_check.py on           # opt back in
    python update_check.py status       # what the check knows (/restack-upgrade check)

The check never upgrades anything. A skill set that changes under an in-flight
journey breaks the journey's audit trail.

It also never fails loudly. It prints nothing and exits 0 when it is opted out,
when install.json is missing or names no source, when git is missing, when the
machine is offline or the network is slow, and when a version cannot be parsed. A session-opening command must not start with an error about
an optional notice. Silence must not hide a broken check either, so an
unexpected failure is recorded in the state file and `status` reports it.

Opt-out. This is checked before anything touches the network:
    ~/.restack/config.json      {"update_check": false}
    RESTACK_UPDATE_CHECK=off    environment variable; it wins over the file
If config.json exists but cannot be read, the check counts as off. Whoever
wrote the file meant to set something, and in an environment that restricts
egress the safe reading is "no outbound fetch".

The only network call is a depth-1 `git fetch <source> main` into a small bare
cache, ~/.restack/upstream.git. <source> is the URL install.json records, the
`origin` of the checkout setup ran from (ADR-019). The install needs no
checkout: most installers delete their clone after setup. A record from before
2.7.0 has no source, so the origin of the checkout it names is used instead,
if that checkout still exists. The fetch sends no payload, cannot prompt for
credentials, and is capped at FETCH_TIMEOUT seconds.

Testing: RESTACK_STATE_DIR points the script at a scratch ~/.restack.

Standard library only (ADR-010).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

BRANCH = "main"
CACHE_DIR = "upstream.git"      # bare cache under ~/.restack; owned by this script
CACHE_REF = f"refs/remotes/upstream/{BRANCH}"
THROTTLE = 24 * 3600            # at most one check, and one notice, per day
CLOCK_SKEW = 300                # a timestamp further ahead than this is ignored
DEFAULT_SNOOZE_DAYS = 7
MAX_SNOOZE_DAYS = 90
FETCH_TIMEOUT = 5               # hard cap on the one network call, in seconds
GIT_TIMEOUT = 5                 # local git reads

INSTALL_FILE = "install.json"   # written by setup / setup.ps1
CONFIG_FILE = "config.json"     # owned by the user: the opt-out lives here
STATE_FILE = "update-check.json"  # owned by this script: throttle, result, snooze

OFF_WORDS = {"0", "false", "off", "no", "never", "disable", "disabled"}
VERSION_RE = re.compile(r"^\d+(?:\.\d+){0,3}$")
SNOOZE_HINT = "(snooze a week: /restack-upgrade snooze)"

# Never prompt and never open a window. A credential dialog at session open is
# worse than no notice, so authentication failures count as offline.
GIT_ENV = {
    "GIT_TERMINAL_PROMPT": "0",
    "GCM_INTERACTIVE": "never",        # Git Credential Manager (the Windows default)
    "SSH_ASKPASS_REQUIRE": "never",    # OpenSSH 8.4+: no askpass GUI either
}
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


# --- paths and files ---------------------------------------------------------

def native_path(raw: str) -> Path:
    """Turn a recorded path into one this Python can open.

    `setup` run from Git Bash records /c/Users/...; native Windows Python reads
    that as C:\\c\\Users and finds nothing. That would make the check silent
    on exactly the machine it was written for.
    """
    if os.name == "nt":
        m = re.match(r"^/(?:cygdrive/)?([A-Za-z])(/.*)?$", raw)
        if m:
            raw = f"{m.group(1).upper()}:{m.group(2) or '/'}"
    return Path(os.path.expanduser(raw))


def state_dir() -> Path:
    override = os.environ.get("RESTACK_STATE_DIR")
    if override:
        return native_path(override)
    # setup writes $HOME/.restack and setup.ps1 writes $env:USERPROFILE\.restack.
    # They are the same directory unless HOME was pointed somewhere else.
    candidates = []
    if os.environ.get("HOME"):
        candidates.append(native_path(os.environ["HOME"]) / ".restack")
    candidates.append(Path.home() / ".restack")
    for candidate in candidates:
        if (candidate / INSTALL_FILE).is_file():
            return candidate
    return candidates[-1]


def load_json(path: Path) -> tuple[bool, object]:
    """(present, value). The value is None when the file exists but cannot be read."""
    if not path.is_file():
        return False, None
    try:
        # utf-8-sig: setup.ps1 writes install.json with a byte-order mark.
        return True, json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return True, None


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def load_state(sdir: Path) -> dict:
    _, state = load_json(sdir / STATE_FILE)
    return state if isinstance(state, dict) else {}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig").strip()
    except OSError:
        return ""


# --- decisions ---------------------------------------------------------------

def is_off(value: object) -> bool:
    return value is False or value == 0 or str(value).strip().lower() in OFF_WORDS


def opted_out(sdir: Path) -> str | None:
    """Why the check is off, or None when it is on."""
    env = os.environ.get("RESTACK_UPDATE_CHECK", "")
    if env.strip() and is_off(env):
        return f"RESTACK_UPDATE_CHECK={env.strip()} in the environment"
    present, config = load_json(sdir / CONFIG_FILE)
    if not present:
        return None
    if not isinstance(config, dict):
        return f"{CONFIG_FILE} cannot be read, which counts as off"
    if is_off(config.get("update_check", True)):
        return f'"update_check": {json.dumps(config.get("update_check"))} in {CONFIG_FILE}'
    return None


def parse_version(text: object) -> tuple[int, ...] | None:
    text = str(text or "").strip()
    if not VERSION_RE.match(text):
        return None                     # "unknown", an HTML error page, a merge conflict
    parts = [int(p) for p in text.split(".")]
    return tuple(parts + [0] * (4 - len(parts)))


def throttled(last: object, now: float) -> bool:
    if not isinstance(last, (int, float)) or isinstance(last, bool):
        return False
    if last > now + CLOCK_SKEW:
        return False                    # a clock set back must not silence the check for good
    return now - last < THROTTLE


def snoozed(state: dict, remote: str, now: float) -> bool:
    """A snooze holds one version. A newer release breaks through it."""
    until = state.get("snoozed_until")
    return (
        state.get("snoozed_version") == remote
        and isinstance(until, (int, float))
        and now < until
    )


def runs_from_recorded_install(install: dict) -> bool:
    """Is install.json describing the install this script is running from?

    Until 2.5.1, `setup --target <scratch>` rewrote install.json for the scratch
    target. setup no longer does, but a record written then, or edited by hand,
    can still describe another install. If the check believed it, it would
    report on an install nobody is using. Staying silent is better than being
    wrong.
    """
    recorded = install.get("skills_dir")
    if not recorded:
        return True                     # nothing recorded to compare against
    mine = Path(os.path.abspath(__file__)).parent.parent
    try:
        return os.path.samefile(mine, native_path(str(recorded)) / mine.name)
    except OSError:
        return False


# --- git ---------------------------------------------------------------------

def git(repo: Path, *args: str, timeout: float = GIT_TIMEOUT, capture: bool = True) -> str | None:
    """stdout of a git command ("" when not captured), or None on any failure,
    including a timeout."""
    exe = shutil.which("git")
    if not exe:
        return None
    env = dict(os.environ, **GIT_ENV)
    # stderr always goes to DEVNULL, never to a pipe. On a timeout Python kills
    # git, then on Windows waits for its pipes to close. The transport helper
    # (git-remote-https, ssh) inherits git's stderr and outlives the kill, so a
    # piped stderr would hold the session open for the hung connection after
    # all - measured at 20 s against a 3 s timeout. stdout is piped only when
    # it is needed, and the fetch does not need it.
    out = subprocess.PIPE if capture else subprocess.DEVNULL
    try:
        done = subprocess.run(
            [exe, "-C", str(repo), *args],
            stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.DEVNULL,
            env=env, timeout=timeout, creationflags=CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.decode("utf-8", "replace").strip() if capture else ""


def source_url(install: dict) -> str | None:
    """Where releases come from, or None when nothing says.

    setup records `source` from 2.7.0. An older record has only `repo`, the
    checkout it was installed from, so that checkout's origin stands in while
    it still exists. Nothing is guessed: no source means a silent check.
    """
    source = str(install.get("source") or "").strip()
    if not source and install.get("repo"):
        repo = native_path(str(install["repo"]))
        if (repo / ".git").exists():
            source = git(repo, "remote", "get-url", "origin") or ""
    if not source or source.startswith("-"):
        return None                     # a leading dash would be read as a git option
    return source


def fetch_remote_version(sdir: Path, source: str) -> str | None:
    cache = sdir / CACHE_DIR
    if not (cache / "HEAD").is_file():
        if git(sdir, "init", "--bare", "--quiet", CACHE_DIR) is None:
            return None
    fetched = git(
        cache,
        # git aborts a stalled transfer itself, which releases its own locks.
        # The subprocess timeout is the backstop for a connect that hangs.
        "-c", "http.lowSpeedLimit=1000", "-c", "http.lowSpeedTime=3",
        "-c", "gc.auto=0", "-c", "maintenance.auto=false",
        "fetch", "--quiet", "--no-tags", "--no-recurse-submodules", "--depth", "1",
        source, f"+refs/heads/{BRANCH}:{CACHE_REF}",
        timeout=FETCH_TIMEOUT, capture=False,
    )
    if fetched is None:
        return None
    return git(cache, "show", f"{CACHE_REF}:VERSION")


# --- commands ----------------------------------------------------------------

def notice(installed: str, remote: str) -> str:
    return f"ReStack v{remote} available (installed v{installed}): /restack-upgrade  {SNOOZE_HINT}"


def check(now: float) -> str | None:
    sdir = state_dir()
    if opted_out(sdir):
        return None
    _, install = load_json(sdir / INSTALL_FILE)
    if not isinstance(install, dict):
        return None
    if not runs_from_recorded_install(install):
        return None
    if not shutil.which("git"):
        return None
    source = source_url(install)
    if source is None:
        return None                     # nothing names where releases come from

    state = load_state(sdir)
    if throttled(state.get("checked_at"), now):
        return None

    # Record the attempt before making it. An offline machine then pays one
    # timeout a day rather than one per session. If the attempt cannot be
    # recorded, do not make it: "at most once a day" is the promise.
    state.update(checked_at=int(now), result="pending")
    for stale in ("error", "installed", "remote", "method"):
        state.pop(stale, None)
    try:
        save_json(sdir / STATE_FILE, state)
    except OSError:
        return None

    # The install is a copy (ADR-019), so what runs is what setup recorded. A
    # symlinked install from before 2.7.0 is sent to /restack-upgrade like any
    # other: its setup run replaces the links with copies.
    installed = str(install.get("version") or "")
    remote = fetch_remote_version(sdir, source)
    state.update(installed=installed, remote=remote)

    have, want = parse_version(installed), parse_version(remote)
    if remote is None:
        state["result"] = "offline"
    elif have is None or want is None:
        state["result"] = "unreadable-version"
    elif want < have:
        state["result"] = "ahead"
    elif want == have:
        state["result"] = "current"
    else:
        state["result"] = "available"
    save_json(sdir / STATE_FILE, state)

    if state["result"] != "available" or snoozed(state, remote, now):
        return None
    return notice(installed, remote)


def record_failure(exc: BaseException) -> None:
    try:
        sdir = state_dir()
        state = load_state(sdir)
        state.update(result="error", error=f"{type(exc).__name__}: {exc}")
        save_json(sdir / STATE_FILE, state)
    except Exception:
        pass


def when(epoch: object) -> str:
    if not isinstance(epoch, (int, float)):
        return "never"
    return time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(epoch))


def snooze(days: int, now: float) -> int:
    sdir = state_dir()
    state = load_state(sdir)
    remote = state.get("remote")
    if state.get("result") != "available" or not remote:
        print("Nothing to snooze: no update notice is pending.")
        return 0
    until = int(now + days * 86400)
    state.update(snoozed_version=remote, snoozed_until=until)
    save_json(sdir / STATE_FILE, state)
    print(f"Snoozed the v{remote} notice for {days} day(s), until {when(until)}. "
          f"A release newer than v{remote} shows straight away.")
    return 0


def set_enabled(enabled: bool) -> int:
    sdir = state_dir()
    path = sdir / CONFIG_FILE
    present, config = load_json(path)
    if present and not isinstance(config, dict):
        print(f"{path} is not valid JSON, so the update check is already off. "
              f"It was not changed - fix or delete it by hand.")
        return 1
    config = dict(config or {})
    config["update_check"] = enabled
    save_json(path, config)
    if enabled:
        print(f'Update check on ("update_check": true in {path}). It runs at most once a day, '
              f"at /restack-journey start or where and /restack-discover paths.")
        env = os.environ.get("RESTACK_UPDATE_CHECK", "")
        if env.strip() and is_off(env):
            print(f"Note: RESTACK_UPDATE_CHECK={env.strip()} is set in this environment and still wins.")
    else:
        print(f'Update check off ("update_check": false in {path}). No ReStack skill fetches anything '
              f"at session open. Turn it back on with /restack-upgrade on.")
    return 0


def status(now: float) -> int:
    sdir = state_dir()
    reason = opted_out(sdir)
    config = sdir / CONFIG_FILE
    print("ReStack update check")
    print(f"  setting:    {'off - ' + reason if reason else 'on'}")
    print(f"  config:     {config}{'' if config.is_file() else ' (absent - the check is on by default)'}")

    present, install = load_json(sdir / INSTALL_FILE)
    if not isinstance(install, dict):
        print(f"  install:    {sdir / INSTALL_FILE} {'cannot be read' if present else 'is missing'} "
              f"- the check stays silent until setup writes it")
    else:
        line = f"v{install.get('version')}, source {source_url(install) or 'unknown - the check stays silent'}"
        if install.get("method") == "symlink":
            line += " - symlinked by a setup older than 2.7.0; /restack-upgrade replaces the links with copies"
        if not runs_from_recorded_install(install):
            line += f" - describes {install.get('skills_dir')}, not this install; re-run setup"
        print(f"  install:    {line}")

    state = load_state(sdir)
    result = state.get("result")
    detail = {
        "available": f"v{state.get('remote')} available (installed v{state.get('installed')})",
        "current": f"up to date (v{state.get('installed')})",
        "ahead": f"ahead of the source's {BRANCH} (v{state.get('installed')} > v{state.get('remote')})",
        "offline": f"could not reach the source's {BRANCH} (offline, slow, or needs credentials)",
        "unreadable-version": f"unreadable version (installed {state.get('installed')!r}, remote {state.get('remote')!r})",
        "error": f"FAILED - {state.get('error')}",
        "pending": "started and did not finish (interrupted or timed out)",
    }.get(result, "")
    print(f"  last check: {when(state.get('checked_at'))}{' - ' + detail if detail else ''}")
    checked = state.get("checked_at")
    if isinstance(checked, (int, float)) and throttled(checked, now):
        print(f"  next check: at the first session open after {when(checked + THROTTLE)}")
    if state.get("snoozed_version") and snoozed(state, str(state["snoozed_version"]), now):
        print(f"  snoozed:    v{state['snoozed_version']} until {when(state.get('snoozed_until'))}")
    return 0


USAGE = "usage: update_check.py [check | snooze [days] | off | on | status]"


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(errors="replace")   # a non-ASCII path must not crash the print
    except (AttributeError, ValueError):
        pass
    now = time.time()
    command = argv[0] if argv else "check"

    if command == "check":
        try:
            line = check(now)
        except Exception as exc:        # silent at session open, visible in status
            record_failure(exc)
            return 0
        if line:
            print(line)
        return 0
    if command == "snooze":
        days = DEFAULT_SNOOZE_DAYS
        if len(argv) > 1:
            if not argv[1].isdigit() or not 1 <= int(argv[1]) <= MAX_SNOOZE_DAYS:
                print(f"snooze takes a number of days, 1 to {MAX_SNOOZE_DAYS}", file=sys.stderr)
                return 2
            days = int(argv[1])
        return snooze(days, now)
    if command in ("off", "on"):
        return set_enabled(command == "on")
    if command == "status":
        return status(now)
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
