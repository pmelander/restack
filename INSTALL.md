# Installing ReStack

**For a person:** clone and run setup.

```bash
git clone https://github.com/pmelander/restack.git ~/restack
cd ~/restack && ./setup          # Windows: .\setup.ps1
```

Type `/restack` in Claude Code. Done.

> **Update check: on by default, easy to turn off.** Once a day, at
> `/restack-journey start` or `where` or at `/restack-discover paths`, ReStack
> runs `git fetch origin main` in this checkout. If a newer version exists, it
> prints one line. It never upgrades itself. If outbound fetches from a skill
> need approval where you work, **turn it off before the first session**:
> `/restack-upgrade off`, or see [Update check and opt-out](#update-check-and-opt-out).

Everything below is for an agent installing on someone's behalf.

---

## For Claude: installing ReStack when pointed at this repository

If someone has asked you to install ReStack — *"install ReStack from
https://github.com/pmelander/restack"*, by pointing at a checkout, or just
"install this" — follow these steps exactly. They are executable instructions,
not reference material.

### What you are about to do

Say this to the user before running anything, so they can decline:

> ReStack is 15 Claude Code skills for architecture work, built on Residuality
> Theory. Installing means cloning the repository and copying 15 directories
> into `~/.claude/skills/`, all named `restack-*`. It will not touch any other
> skill. Two optional extras exist — openpyxl for spreadsheet import, and the
> Codex CLI for cross-model second opinions — and I will not install either
> without asking. Once a day, at the start of a journey, the skills run
> `git fetch` in the checkout to see whether a newer ReStack exists. That can
> be turned off, and I can do it now if you prefer.

**Get an explicit yes before writing anything into `~/.claude/skills/`.**
Installing skills changes how their Claude Code behaves in every future
session, which is not a change to make on an implied instruction.

### Step 1 — decide where the repository goes

If a checkout already exists, use it. Otherwise ask where they want it, or
propose `~/restack` and let them redirect you.

```bash
git clone https://github.com/pmelander/restack.git ~/restack
```

Do not clone into `~/.claude/skills/`. The repository is not a skill; `setup`
installs *from* it.

### Step 2 — show what will happen, before it happens

```bash
cd ~/restack && ./setup --dry-run
```

This writes nothing. It lists every skill that would be installed, updated or
removed. Show the output. If it proposes removing anything, stop and confirm —
a removal means a skill of theirs shares the `restack-` prefix.

### Step 3 — install

```bash
cd ~/restack && ./setup
```

On Windows without a POSIX shell:

```powershell
cd ~\restack; .\setup.ps1
```

Report the summary line verbatim. It states how many skills were installed,
updated, removed and unchanged.

### Step 4 — the optional extras

`setup` reports whether each is present and what it affects. Neither is
required.

**openpyxl** — only `/restack-excel` needs it, for `.xlsx` (CSV works without).

```bash
cd ~/restack && pip install -r requirements.txt
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

### Step 5 — verify and hand over

```bash
ls -d ~/.claude/skills/restack-*/ | wc -l    # expect 15
```

Then tell them:

> ReStack v{version} installed — {n} skills. Type `/restack` in Claude Code to
> see them. Start with `/restack-journey start` on a real system; it will
> classify the terrain and map the route. `/restack-upgrade` updates it later,
> and `/restack-upgrade off` turns off the once-a-day update check.
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
  a partial install is confusing, and `./setup` re-run is the correct fix for
  almost everything.
- **If they already have ReStack**, this is an upgrade, not an install. Use
  `/restack-upgrade`, which checks for local changes before pulling.

### If you are installing from a fork or a branch

Use the URL and branch they gave you, and say which one you used. Do not
default to `main` on a different remote — a fork's `main` may be behind, and
the version they end up with should be the one they asked for.

---

## Install methods

| Method | Command | When |
|---|---|---|
| **Copy** (default) | `./setup` | normal use — the install is independent of the checkout |
| **Symlink** | `./setup --symlink` | developing ReStack; edits in the repo are live. Needs symlink support — see below |
| **One-off target** | `./setup --target DIR` | a scratch or test install. Not recorded in `install.json` |
| **Dry run** | `./setup --dry-run` | see what would change |

`CLAUDE_SKILLS_DIR` overrides the default location for all of them. For a
permanent install outside `~/.claude/skills`, export it rather than using
`--target`: an install there is recorded, and `/restack-upgrade` re-installs
there.

**Symlinks on Windows.** Git Bash silently *copies* when `ln -s` is used without
symlink support enabled — the command succeeds and you get a directory. setup
probes for this and, if it cannot create symlinks, says so and installs by copy
rather than claiming edits are live. To get working symlinks: enable Developer
Mode (Settings › For developers), run in an elevated shell, or

```bash
MSYS=winsymlinks:nativestrict ./setup --symlink
```

## What setup does that a plain copy does not

- **Removes ReStack skills deleted upstream.** `cp -R skills/* ~/.claude/skills/`
  leaves a renamed or removed skill installed forever, and the user keeps
  invoking a command the project no longer has.
- **Reports what changed** — installed, updated, removed, unchanged.
- **Refuses to install a broken tree** — a skill directory with no `SKILL.md`
  would be silently ignored by Claude Code, so setup stops instead.
- **Records the install** in `~/.restack/install.json`, which is how
  `/restack-upgrade` finds the repository later. Only an install into the
  default skills directory is recorded, so a `--target` run cannot overwrite
  the record of the real one.
- **Checks the optional dependency** and tells you what it affects.
- **Stays inside the `restack-` prefix**, so it cannot damage another suite.

## Update check and opt-out

**What it does.** At `/restack-journey start`, `/restack-journey where` and
`/restack-discover paths`, at most once a day, the skills run
`git fetch origin main` in the checkout that `~/.restack/install.json` names.
They then compare `origin/main:VERSION` with the installed version. If a newer
version exists, they print one line:

```
ReStack v2.5.0 available (installed v2.4.0): /restack-upgrade  (snooze a week: /restack-upgrade snooze)
```

Otherwise they print nothing.

**What it does not do.** It never upgrades anything, and it never runs inside a
decision gate. It sends nothing beyond the git protocol, has no telemetry, and
contacts no endpoint except the `origin` you cloned from. It cannot prompt for
credentials: a repository that needs them counts as offline. The fetch is
capped at five seconds. Offline, no checkout or no Python means it stays
silent. Its only local effect is to update `origin/main` in the checkout.
Design and rationale:
[ADR-016](docs/adr/ADR-016-update-awareness.md).

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
last check and any snooze. `rm -rf ~/.restack` removes the opt-out along with
everything else, so set it again after a reinstall.

**Snooze instead.** `/restack-upgrade snooze` hides the notice for seven days,
or `snooze <days>` for 1–90. A newer release still shows straight away.

**Symlinked development installs** get different wording, because the upgrade
is a pull, not `/restack-upgrade`. On `main`, the line names
`git -C "<repo>" pull --ff-only`. On any other branch, it only reports the gap.

**Files in `~/.restack/`:**

| File | Written by | Holds |
|---|---|---|
| `install.json` | `setup` | version, repo path, skills dir, method, date |
| `config.json` | you, or `/restack-upgrade off` / `on` | `update_check`. `setup` never touches it |
| `update-check.json` | the check | last check time and result, snooze |

## Uninstalling

```bash
rm -rf ~/.claude/skills/restack-*/
rm -rf ~/.restack
```

The repository checkout can then be deleted too. Nothing else is left behind —
ReStack writes only to the skills directory and `~/.restack`, and the documents
the skills produce live in your own project's `docs/`.
