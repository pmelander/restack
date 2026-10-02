<#
.SYNOPSIS
  ReStack setup - install or update the skills for Claude Code.

.DESCRIPTION
  Copies (or symlinks) every skills\restack-* directory into the Claude Code
  skills directory, removes ReStack skills that no longer exist upstream, and
  records where the install came from so /restack-upgrade can find it later.
  Only an install into the default skills directory is recorded; a -Target
  run leaves the record alone (ADR-011, Notes).

  Windows-native equivalent of ./setup. Safe to re-run.

  SAFETY: only ever creates, replaces or removes directories whose names begin
  with "restack-". Nothing else in the skills directory is touched, so it
  cannot damage another skill suite.

.PARAMETER Symlink
  Symlink instead of copying, so repository edits are live. Requires Developer
  Mode or an elevated shell on Windows.

.PARAMETER DryRun
  Show what would change; write nothing.

.PARAMETER Target
  Install into this directory instead of $HOME\.claude\skills, once. Not
  recorded in ~\.restack\install.json, so /restack-upgrade keeps tracking the
  default install. For a permanent install elsewhere, set $env:CLAUDE_SKILLS_DIR
  instead; an install there is recorded.

.PARAMETER Quiet
  Only print the summary.

.EXAMPLE
  .\setup.ps1
.EXAMPLE
  .\setup.ps1 -DryRun
.EXAMPLE
  .\setup.ps1 -Symlink
#>
[CmdletBinding()]
param(
    [switch]$Symlink,
    [switch]$DryRun,
    [string]$Target,
    [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VersionFile = Join-Path $RepoDir 'VERSION'
if (Test-Path $VersionFile) { $Version = (Get-Content $VersionFile -Raw).Trim() } else { $Version = 'unknown' }

if ($env:CLAUDE_SKILLS_DIR) {
    $DefaultSkillsDir = $env:CLAUDE_SKILLS_DIR
} else {
    $DefaultSkillsDir = Join-Path $env:USERPROFILE '.claude\skills'
}
if ($Target) { $SkillsDir = $Target } else { $SkillsDir = $DefaultSkillsDir }

if ($Symlink) { $Method = 'symlink' } else { $Method = 'copy' }
$StateDir = Join-Path $env:USERPROFILE '.restack'

function Say([string]$Message) { if (-not $Quiet) { Write-Host $Message } }

# Relative path -> hash for every file under a skill directory. Comparing only
# SKILL.md misses a section edited on its own, which then never reaches a copy
# install.
function Get-TreeHash([string]$Dir) {
    $map = @{}
    Get-ChildItem -LiteralPath $Dir -Recurse -File | ForEach-Object {
        $map[$_.FullName.Substring($Dir.Length)] = (Get-FileHash -LiteralPath $_.FullName).Hash
    }
    return $map
}

function Test-SameTree([string]$A, [string]$B) {
    $ha = Get-TreeHash $A; $hb = Get-TreeHash $B
    if ($ha.Count -ne $hb.Count) { return $false }
    foreach ($k in $ha.Keys) { if ($hb[$k] -ne $ha[$k]) { return $false } }
    return $true
}

# One directory however it is spelled: relative, trailing separator, / or \,
# different case. -eq on strings is case-insensitive, as NTFS is.
function Test-SameDir([string]$A, [string]$B) {
    $full = foreach ($p in $A, $B) {
        $abs = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($p)
        [System.IO.Path]::GetFullPath($abs).TrimEnd('\', '/')
    }
    return $full[0] -eq $full[1]
}

# --- sanity ------------------------------------------------------------------

$SourceRoot = Join-Path $RepoDir 'skills'
if (-not (Test-Path $SourceRoot)) {
    Write-Error "No skills\ directory next to this script ($RepoDir). Run setup.ps1 from a ReStack checkout."
}

$Sources = @(Get-ChildItem -Path $SourceRoot -Directory -Filter 'restack-*' | Sort-Object Name)
if ($Sources.Count -eq 0) { Write-Error "No skills\restack-* directories found." }

# Refuse to install a skill with no SKILL.md - Claude Code would silently
# ignore it and the user would wonder why the command does not exist.
foreach ($s in $Sources) {
    if (-not (Test-Path (Join-Path $s.FullName 'SKILL.md'))) {
        Write-Error "$($s.Name) has no SKILL.md - refusing to install a broken tree. If developing, run: python scripts/gen_skills.py"
    }
}

if (-not $DryRun -and -not (Test-Path $SkillsDir)) {
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
}

# --- is this the install the record describes? -------------------------------
# install.json describes one install: the one a bare setup.ps1 maintains,
# because that is what /restack-upgrade re-runs. A -Target run into a scratch
# directory used to overwrite it, and /restack-upgrade then verified the
# scratch tree.

$Record = Test-SameDir $SkillsDir $DefaultSkillsDir

# --- can this shell actually create symlinks? --------------------------------
# Without Developer Mode or elevation, New-Item -ItemType SymbolicLink throws.
# Probe once so the failure is a clear message rather than an abort halfway
# through the install, and so we never claim "edits are live" when they are not.

$SymlinkDegraded = $false
$SymlinkUnverified = $false
if ($Method -eq 'symlink') {
    if ($DryRun) {
        $SymlinkUnverified = $true
    } else {
        $probe = Join-Path $SkillsDir '.restack-symlink-probe'
        if (Test-Path -LiteralPath $probe) { Remove-Item -LiteralPath $probe -Recurse -Force }
        try {
            New-Item -ItemType SymbolicLink -Path $probe -Target $RepoDir -ErrorAction Stop | Out-Null
            Remove-Item -LiteralPath $probe -Force
        } catch {
            if (Test-Path -LiteralPath $probe) { Remove-Item -LiteralPath $probe -Recurse -Force }
            $Method = 'copy'
            $SymlinkDegraded = $true
        }
    }
}

Say "ReStack v$Version"
Say "  from: $RepoDir"
Say "  into: $SkillsDir  ($Method)"
if ($SymlinkDegraded) { Say "        (-Symlink requested; this shell cannot create symlinks)" }
if ($DryRun) { Say "  DRY RUN - nothing will be written" }
Say ""

# --- install -----------------------------------------------------------------

$nNew = 0; $nUpd = 0; $nSame = 0; $nDel = 0

foreach ($s in $Sources) {
    $name = $s.Name
    $dest = Join-Path $SkillsDir $name
    $destItem = Get-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue

    $action = 'update'
    if ($null -eq $destItem) {
        $action = 'install'; $nNew++
    } else {
        $isLink = $destItem.LinkType -eq 'SymbolicLink'
        if ($Method -eq 'symlink' -and $isLink -and $destItem.Target -contains $s.FullName) {
            $action = 'unchanged'; $nSame++
        } elseif ($Method -eq 'copy' -and -not $isLink) {
            if (Test-SameTree $s.FullName $dest) {
                $action = 'unchanged'; $nSame++
            } else { $nUpd++ }
        } else { $nUpd++ }
    }

    if ($action -ne 'unchanged') { Say "  $action  /$name" }
    if ($DryRun -or $action -eq 'unchanged') { continue }

    if ($null -ne $destItem) { Remove-Item -LiteralPath $dest -Recurse -Force }
    if ($Method -eq 'symlink') {
        New-Item -ItemType SymbolicLink -Path $dest -Target $s.FullName | Out-Null
    } else {
        Copy-Item -LiteralPath $s.FullName -Destination $dest -Recurse -Force
    }
}

# --- remove skills deleted upstream -----------------------------------------
# The reason a plain recursive copy is not good enough: a skill removed or
# renamed upstream stays installed forever, and the user keeps invoking a
# command the project no longer has.

if (Test-Path $SkillsDir) {
    $installed = @(Get-ChildItem -Path $SkillsDir -Directory -Filter 'restack-*' -ErrorAction SilentlyContinue)
    foreach ($d in $installed) {
        if (-not (Test-Path (Join-Path $SourceRoot $d.Name))) {
            Say "  remove   /$($d.Name)  (no longer in ReStack)"
            $nDel++
            if (-not $DryRun) { Remove-Item -LiteralPath $d.FullName -Recurse -Force }
        }
    }
}

# --- verify every section path resolves --------------------------------------
# A skill names its sections as <base>/sections/<file>. If one is missing from
# the install, the step that reads it silently does not run - which is how the
# outside opinion went missing for every copy install. Check the tree that was
# actually installed (the source tree in a dry run), and fail loudly.

$missing = 0
foreach ($s in $Sources) {
    if ($DryRun) { $root = $s.FullName } else { $root = Join-Path $SkillsDir $s.Name }
    $skillMd = Join-Path $root 'SKILL.md'
    if (-not (Test-Path -LiteralPath $skillMd)) { continue }
    $refs = Select-String -LiteralPath $skillMd -Pattern '<base>/sections/[A-Za-z0-9_.-]+\.md' -AllMatches |
        ForEach-Object { $_.Matches } | ForEach-Object { $_.Value } | Sort-Object -Unique
    foreach ($ref in $refs) {
        $file = Join-Path $root ($ref.Substring('<base>/'.Length))
        if (-not (Test-Path -LiteralPath $file)) {
            Write-Host "Error: /$($s.Name) names $ref but $file is missing."
            $missing++
        }
    }
}
if ($missing -gt 0) {
    Write-Error "$missing section file(s) missing - the install is incomplete. Re-run setup.ps1; if it persists, report it."
}

# --- record the install ------------------------------------------------------
# Recorded under the default's own spelling, so the file reads the same however
# -Target named it.

$recordNote = ''
if (-not $Record) {
    $recordNote = "$(Join-Path $StateDir 'install.json') left unchanged - $SkillsDir is not the default skills directory ($DefaultSkillsDir), and the record tracks only that one, because it is what /restack-upgrade re-installs. For a permanent install elsewhere, set `$env:CLAUDE_SKILLS_DIR = '$SkillsDir' instead of -Target."
} elseif (-not $DryRun) {
    if (-not (Test-Path $StateDir)) { New-Item -ItemType Directory -Path $StateDir -Force | Out-Null }
    $state = [ordered]@{
        version      = $Version
        repo         = $RepoDir
        skills_dir   = $DefaultSkillsDir
        method       = $Method
        installed_at = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    }
    $state | ConvertTo-Json | Out-File -FilePath (Join-Path $StateDir 'install.json') -Encoding utf8
}

# --- optional dependency check ----------------------------------------------

$depNote = ''
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) {
    $depNote = 'Python not found - /restack-excel will not work. Everything else is unaffected.'
} else {
    & $py.Source -c "import openpyxl" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $depNote = 'openpyxl not installed - /restack-excel cannot read .xlsx (CSV still works). Fix: pip install -r requirements.txt'
    }
}

# --- summary -----------------------------------------------------------------

Say ""
if (($nNew + $nUpd + $nDel) -eq 0) {
    Write-Host "ReStack v$Version - already up to date ($nSame skills)."
} else {
    Write-Host "ReStack v$Version - $nNew installed, $nUpd updated, $nDel removed, $nSame unchanged."
}

$codexNote = ''
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    $codexNote = 'Codex CLI not found - the outside opinion falls back to a same-family subagent (weaker; shares blind spots). Optional: npm i -g @openai/codex && codex login'
}

if ($recordNote) { Write-Host ""; Write-Host "Note: $recordNote" }
if ($depNote) { Write-Host ""; Write-Host "Note: $depNote" }
if ($codexNote) { Write-Host ""; Write-Host "Note: $codexNote" }

if ($SymlinkDegraded) {
    Write-Host ""
    Write-Host "Warning: -Symlink was requested but this shell cannot create symlinks, so"
    Write-Host "the skills were INSTALLED BY COPY. Edits in the repository are NOT live -"
    Write-Host "re-run setup.ps1 after each change, or enable Developer Mode"
    Write-Host "(Settings > For developers) or run in an elevated shell, then retry."
}

if ($DryRun) {
    Write-Host ""; Write-Host "(dry run - nothing was written)"
    if ($SymlinkUnverified) { Write-Host "Symlink support not probed in a dry run; a real run verifies it." }
} else {
    Write-Host ""; Write-Host "Type /restack in Claude Code to see the skills."
    if ($Method -eq 'symlink') {
        Write-Host "Symlinked: edits in $RepoDir are live after a regenerate."
        Write-Host "Claude Code re-reads skills when they change; a fresh session is the sure way."
    }
}
