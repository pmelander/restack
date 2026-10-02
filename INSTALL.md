# Installing ReStack

**For a person:** clone, run setup, and delete the clone if you like. The
install is a copy in your user profile and does not need it.

```bash
git clone --depth 1 https://github.com/pmelander/restack.git restack-install
cd restack-install && ./setup          # Windows: .\setup.ps1
cd .. && rm -rf restack-install        # optional. Windows: Remove-Item -Recurse -Force restack-install
```

Type `/restack` in Claude Code. Done. `/restack-upgrade` updates it later, with
no clone needed.

> **Update check: on by default, easy to turn off.** Once a day, at
> `/restack-journey start` or `where` or at `/restack-discover paths`, ReStack
> runs a small `git fetch` of `main` from the repository you installed from. If
> a newer version exists, it prints one line. It never upgrades itself. If
> outbound fetches from a skill need approval where you work, **turn it off
> before the first session**: `/restack-upgrade off`, or see
> [Update check and opt-out](#update-check-and-opt-out).

Everything below is for an agent installing on someone's behalf.

---

## For Claude: installing ReStack when pointed at this repository

If someone has asked you to install ReStack — *"install ReStack from
https://github.com/pmelander/restack"*, by pointing at a checkout, or just
"install this" — follow these steps exactly. They are executable instructions,
not reference material.

### What you are about to do

Say this to the user before running anything, so they can decline:

> ReStack is 16 Claude Code skills for architecture work, built on Residuality
> Theory. Installing means cloning the repository into a temporary directory
> and copying 16 directories into `~/.claude/skills/`, all named `restack-*`.
> It will not touch any other skill, and the copy does not depend on the clone,
> which I delete afterwards. Two optional extras exist — openpyxl for
> spreadsheet import, and the Codex CLI for cross-model second opinions — and I
> will not install either without asking. Once a day, at the start of a
> journey, the skills fetch `main` from the repository to see whether a newer
> ReStack exists. That can be turned off, and I can do it now if you prefer.

**Get an explicit yes before writing anything into `~/.claude/skills/`.**
Installing skills changes how their Claude Code behaves in every future
session, which is not a change to make on an implied instruction.

### Step 1 — get the release into a temporary directory

If the user pointed you at an existing checkout, use it and skip the clone, and
do not delete it in step 6. It is theirs. Otherwise:

```bash
D="$(mktemp -d "${TMPDIR:-/tmp}/restack-install.XXXXXX")" && echo "INSTALL_DIR=$D"
git clone --quiet --depth 1 https://github.com/pmelander/restack.git "$D/restack"
```

On Windows PowerShell:

```powershell
$d = Join-Path $env:TEMP ("restack-install." + [guid]::NewGuid().ToString("N")); "INSTALL_DIR=$d"
git clone --quiet --depth 1 https://github.com/pmelander/restack.git "$d\restack"
```

Carry the printed `INSTALL_DIR` into every later step literally. Shell
variables do not survive between commands, and on Windows `$TMP` and `$TEMP`
name the whole temp folder.

Do not clone into `~/.claude/skills/`. The repository is not a skill; `setup`
installs *from* it.

### Step 2 — show what will happen, before it happens

```bash
"<INSTALL_DIR>/restack/setup" --dry-run
```

This writes nothing. It lists every skill that would be installed, updated or
removed. Show the output. If it proposes removing anything, stop and confirm —
a removal means a skill of theirs shares the `restack-` prefix.

### Step 3 — install

```bash
"<INSTALL_DIR>/restack/setup"
```

On Windows PowerShell: `& "<INSTALL_DIR>\restack\setup.ps1"`.

Report the summary line verbatim. It states how many skills were installed,
updated, removed and unchanged. setup also records the repository you cloned
from, which is where `/restack-upgrade` and the update check fetch releases.

### Step 4 — the optional extras

`setup` reports whether each is present and what it affects. Neither is
required.

**openpyxl** — only `/restack-excel` needs it, for `.xlsx` (CSV works without).

```bash
pip install -r "<INSTALL_DIR>/restack/requirements.txt"
```

**Codex CLI** — makes the outside opinion a genuine outside voice. Without it,
`/restack-stressor` and `/restack-design-review` fall back to a fresh subagent:
same model family, so it shares blind spots and its agreement is weak evidence.

```bash
npm i -g @openai/codex
codex login
```

`codex login` is interactive and opens a browser. Do not attempt it on the
user's behalf, and never ask for or handle an API key.

**Do not install either without asking.** It is their machine, and a global npm
install in particular is not implied by "install ReStack".

### Step 5 — verify

```bash
ls -d ~/.claude/skills/restack-* | wc -l    # expect 16
```

### Step 6 — delete the temporary clone

Only the directory you created in step 1, never a checkout the user gave you:

```bash
D="<INSTALL_DIR from step 1>"
case "$(basename "$D")" in restack-install.*) rm -rf "$D" ;; *) echo "refusing to delete '$D'" ;; esac
```

On Windows PowerShell:

```powershell
$d = "<INSTALL_DIR from step 1>"
if ((Split-Path -Leaf $d) -like "restack-install.*") { Remove-Item -LiteralPath $d -Recurse -Force } else { "refusing to delete '$d'" }
```

Then tell them:

> ReStack v{version} installed — {n} skills, as a copy in your profile. Type
> `/restack` in Claude Code to see them. Start with `/restack-journey start` on
> a real system; it will classify the terrain and map the route.
> `/restack-upgrade` updates it later, and `/restack-upgrade off` turns off the
> once-a-day update check.
>
> Worth reading first: RESIDUALITY.md — the skills use *aspiration*, *actor*,
> *intention*, *path*, *stressor* and *residual* precisely, and without that
> vocabulary they will seem to be using ordinary words strangely.

### Rules while doing this

- **Only `restack-*`.** Never delete, move or overwrite anything in
  `~/.claude/skills/` that does not start with `restack-`. `setup` enforces
  this; do not work around it with your own file operations.
- **Never run `setup` with `sudo`.** It writes to the user's home directory and
  needs nothing more.
- **Do not modify their Claude Code settings**, hooks, or configuration.
  Installing ReStack means copying skill directories. Nothing else.
- **If a step fails, stop and report it.** Do not improvise a repair by hand —
  a partial install is confusing, and re-running `setup` is the correct fix for
  almost everything.
- **If they already have ReStack**, this is an upgrade, not an install. Use
  `/restack-upgrade`.

### If you are installing from a fork or a branch

Use the URL and branch they gave you (`git clone --branch <branch> <url>`), and
say which one you used. Do not default to `main` on a different remote — a
fork's `main` may be behind, and the version they end up with should be the one
they asked for. setup records the fork as the source, so later upgrades come
from it too.

---

## setup options

| Command | What it does |
|---|---|
| `./setup` | install or update the copy in `~/.claude/skills`. Safe to re-run |
| `./setup --dry-run` | show what would change; write nothing |
| `./setup --quiet` | print only the summary |

The install is always a copy in the user profile
([ADR-019](docs/adr/ADR-019-copy-only-install.md)). `--symlink` and `--target`
were removed in 2.7.0 and are refused with a message. `CLAUDE_SKILLS_DIR` is
ignored, with a note. If a symlinked install from before 2.7.0 is present, setup
replaces each link with a copy and removes the link as a link. The directory it
pointed at is not touched.

## Developing ReStack

Keep a clone, edit the templates, regenerate, and install:

```bash
python scripts/gen_skills.py && ./setup
```

Your sessions load what you last installed, never what is half-edited in the
working tree. `/restack-upgrade` never touches your clone. It installs the
latest release from a temporary clone, and it asks first if what you installed
is ahead of the release.

## What setup does that a plain copy does not

- **Removes ReStack skills deleted upstream.** `cp -R skills/* ~/.claude/skills/`
  leaves a renamed or removed skill installed forever, and the user keeps
  invoking a command the project no longer has.
- **Reports what changed** — installed, updated, removed, unchanged.
- **Refuses to install a broken tree** — a skill directory with no `SKILL.md`
  would be silently ignored by Claude Code, so setup stops instead.
- **Verifies every section a skill names is installed**, and fails if one is not.
- **Records the install** in `~/.restack/install.json`, including the source
  that `/restack-upgrade` and the update check fetch releases from.
- **Checks the optional dependency** and tells you what it affects.
- **Stays inside the `restack-` prefix**, so it cannot damage another suite.

## Update check and opt-out

**What it does.** At `/restack-journey start`, `/restack-journey where` and
`/restack-discover paths`, at most once a day, the skills fetch `main` at depth 1
from the `source` that `~/.restack/install.json` records: the repository you
installed from. The fetch goes into a small cache, `~/.restack/upstream.git`, so
no checkout is needed. They then compare that `VERSION` with the installed
version. If a newer version exists, they print one line:

```
ReStack v2.8.0 available (installed v2.7.0): /restack-upgrade  (snooze a week: /restack-upgrade snooze)
```

Otherwise they print nothing.

**What it does not do.** It never upgrades anything, and it never runs inside a
decision gate. It sends nothing beyond the git protocol, has no telemetry, and
contacts no endpoint except the source you installed from. It cannot prompt for
credentials: a repository that needs them counts as offline. The fetch is
capped at five seconds. Offline, no recorded source, or no Python means it
stays silent. Design and rationale:
[ADR-016](docs/adr/ADR-016-update-awareness.md), amended by
[ADR-019](docs/adr/ADR-019-copy-only-install.md).

**Turn it off.** Do this before the first session if outbound fetches from a
skill are not acceptable in your environment. Any one of these works, and each
is read before anything touches the network:

| How | Command |
|---|---|
| From Claude Code | `/restack-upgrade off` (and `/restack-upgrade on` to undo) |
| By hand, POSIX shell or Git Bash | `mkdir -p ~/.restack && printf '{"update_check": false}\n' > ~/.restack/config.json` |
| By hand, PowerShell | `New-Item -ItemType Directory -Force "$HOME\.restack" \| Out-Null; Set-Content "$HOME\.restack\config.json" '{"update_check": false}' -Encoding ASCII` |
| Machine or fleet policy | set the environment variable `RESTACK_UPDATE_CHECK=off`. It wins over the file |

A `config.json` that exists but is not valid JSON also counts as off.
`/restack-upgrade check` shows the current setting (`setting: off - ...`), the
source, the last check and any snooze. `rm -rf ~/.restack` removes the opt-out
along with everything else, so set it again after a reinstall.

**Snooze instead.** `/restack-upgrade snooze` hides the notice for seven days,
or `snooze <days>` for 1–90. A newer release still shows straight away.

**Files in `~/.restack/`:**

| File | Written by | Holds |
|---|---|---|
| `install.json` | `setup` | version, source, the directory installed from, skills dir, method, date |
| `config.json` | you, or `/restack-upgrade off` / `on` | `update_check`. `setup` never touches it |
| `update-check.json` | the check | last check time and result, snooze |
| `upstream.git/` | the check | a bare cache of `main`, fetched at depth 1 |

## Uninstalling

```bash
rm -rf ~/.claude/skills/restack-*
rm -rf ~/.restack
```

No trailing slash on the first line. On a symlinked install from before 2.7.0,
`rm -rf link/` would delete the contents of the checkout the link points at,
while `rm -rf link` removes only the link.

Nothing else is left behind — ReStack writes only to the skills directory and
`~/.restack`, and the documents the skills produce live in your own project's
`docs/`.
