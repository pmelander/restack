"""The shells the installers and the update-check snippets are tested with.

On Windows, `bash` on PATH is often C:\\Windows\\System32\\bash.exe, the WSL
launcher. It runs in Linux with the WSL user's own home, because Windows
environment variables do not cross into WSL, so a test that picked it would
read and write that real home instead of its scratch one. Launchers in
System32 and WindowsApps are refused, and Git for Windows' own shells, found
through git itself, are used instead.

Not a test module: discover only collects test*.py.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _is_launcher(path: str) -> bool:
    """A WSL launcher rather than a shell of this machine."""
    p = os.path.normcase(os.path.abspath(path))
    system_root = os.path.normcase(os.environ.get("SystemRoot", r"C:\Windows"))
    return p.startswith(system_root + os.sep) or f"{os.sep}windowsapps{os.sep}" in p


def _git_usr_bin() -> Path | None:
    """Git for Windows' usr/bin, where its sh and bash live."""
    git = shutil.which("git")
    if not git:
        return None
    try:
        done = subprocess.run([git, "--exec-path"], stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, timeout=30, check=True)
        usr_bin = Path(done.stdout.decode().strip()).parents[2] / "usr" / "bin"  # <git>/mingw64/libexec/git-core
    except (OSError, subprocess.SubprocessError, IndexError):
        return None
    return usr_bin if usr_bin.is_dir() else None


def posix_shell(name: str) -> str | None:
    """`sh` or `bash` that runs on this machine, never a WSL launcher."""
    found = shutil.which(name)
    if os.name != "nt":
        return found
    if found and not _is_launcher(found):
        return found
    usr_bin = _git_usr_bin()
    candidate = usr_bin / f"{name}.exe" if usr_bin else None
    return str(candidate) if candidate and candidate.is_file() else None


def posix_env(shell: str, env: dict) -> dict:
    """env for `shell`, with the shell's own tools first on PATH.

    Git's sh started from PowerShell has no /usr/bin on PATH, so mkdir, cp and
    grep would not be found."""
    env = dict(env)
    if os.name == "nt":
        env["PATH"] = str(Path(shell).parent) + os.pathsep + env.get("PATH", "")
    return env


def powershell() -> str | None:
    """Windows PowerShell, or pwsh where it is the only one."""
    return shutil.which("powershell") or shutil.which("pwsh")
