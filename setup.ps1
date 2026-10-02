<#
.SYNOPSIS
  ReStack setup - install or update the skills for Claude Code.

.DESCRIPTION
  Copies every skills\restack-* directory into $env:USERPROFILE\.claude\skills,
  removes ReStack skills that no longer exist upstream, and records the install
  in ~\.restack\install.json so /restack-upgrade can find it later.

  The install is always a copy in the user profile (ADR-019). It does not
  depend on this checkout: delete the checkout and the skills keep working.
  The checkout is only where the next upgrade copies from.

  Windows-native equivalent of ./setup. Safe to re-run.

  SAFETY: only ever creates, replaces or removes entries whose names begin
  with "restack-". Nothing else in the skills directory is touched, so it
  cannot damage another skill suite. A link left by an older symlinked install
  is removed as a link, never followed: Windows PowerShell 5.1's
  Remove-Item -Recurse on a directory link can delete the contents of the
  directory it points at, which would be the checkout.

.PARAMETER DryRun
  Show what would change; write nothing.

.PARAMETER Quiet
  Only print the summary.

.EXAMPLE
  .\setup.ps1
.EXAMPLE
  .\setup.ps1 -DryRun
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Quiet,
    # Removed in 2.7.0. Declared only so that using them gets a clear message
    # instead of a parameter-binding error.
    [switch]$Symlink,
    [string]$Target
)

$ErrorActionPreference = 'Stop'

if ($Symlink -or $Target) {
    $which = if ($Symlink) { '-Symlink' } else { '-Target' }
    Write-Host "Error: $which was removed in ReStack 2.7.0. Skills always install as a copy"
    Write-Host "into `$env:USERPROFILE\.claude\skills, independent of this checkout (ADR-019)."
    Write-Host "Run .\setup.ps1 with no options."
    exit 2
}

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VersionFile = Join-Path $RepoDir 'VERSION'
if (Test-Path $VersionFile) { $Version = (Get-Content $VersionFile -Raw).Trim() } else { $Version = 'unknown' }

$SkillsDir = Join-Path $env:USERPROFILE '.claude\skills'
$StateDir = Join-Path $env:USERPROFILE '.restack'

function Say([string]$Message) { if (-not $Quiet) { Write-Host $Message } }

# Relative path -> hash for every file under a skill directory. Comparing only
# SKILL.md misses a section edited on its own, which then never reaches the
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

# A symbolic link or junction: anything that is a reparse point.
function Test-Link($Item) {
    return [bool]($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
}

# Remove one installed entry. A link goes through Directory.Delete with
# recursive = $false, which removes the link itself and never what it points
# at. Remove-Item -Recurse is used only on a real directory.
function Remove-Entry($Item) {
    if (Test-Link $Item) {
        [System.IO.Directory]::Delete($Item.FullName, $false)
    } else {
        Remove-Item -LiteralPath $Item.FullName -Recurse -Force
    }
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

# CLAUDE_SKILLS_DIR used to move the install. It no longer does; say so rather
# than install somewhere the architect did not expect.
$skillsEnvNote = ''
if ($env:CLAUDE_SKILLS_DIR) {
    $skillsEnvNote = "CLAUDE_SKILLS_DIR is set ($env:CLAUDE_SKILLS_DIR) and was ignored: since 2.7.0 ReStack always installs into $SkillsDir."
}

if (-not $DryRun -and -not (Test-Path $SkillsDir)) {
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
}

Say "ReStack v$Version"
Say "  from: $RepoDir"
Say "  into: $SkillsDir  (copy)"
if ($DryRun) { Say "  DRY RUN - nothing will be written" }
Say ""

# --- install -----------------------------------------------------------------

$nNew = 0; $nUpd = 0; $nSame = 0; $nDel = 0; $nUnlinked = 0

foreach ($s in $Sources) {
    $name = $s.Name
    $dest = Join-Path $SkillsDir $name
    $destItem = Get-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue

    $action = 'update'
    if ($null -eq $destItem) {
        $action = 'install'; $nNew++
    } elseif (Test-Link $destItem) {
        # Left by a symlinked install from before 2.7.0. Replaced with a copy.
        $nUpd++; $nUnlinked++
    } elseif (Test-SameTree $s.FullName $dest) {
        $action = 'unchanged'; $nSame++
    } else {
        $nUpd++
    }

    if ($action -ne 'unchanged') { Say "  $action  /$name" }
    if ($DryRun -or $action -eq 'unchanged') { continue }

    if ($null -ne $destItem) { Remove-Entry $destItem }
    Copy-Item -LiteralPath $s.FullName -Destination $dest -Recurse -Force
}

# --- remove skills deleted upstream -----------------------------------------
# The reason a plain recursive copy is not good enough: a skill removed or
# renamed upstream stays installed forever, and the user keeps invoking a
# command the project no longer has.

if (Test-Path $SkillsDir) {
    $installed = @(Get-ChildItem -Path $SkillsDir -Directory -Filter 'restack-*' -Force -ErrorAction SilentlyContinue)
    foreach ($d in $installed) {
        if (-not (Test-Path (Join-Path $SourceRoot $d.Name))) {
            Say "  remove   /$($d.Name)  (no longer in ReStack)"
            $nDel++
            if (-not $DryRun) { Remove-Entry $d }
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
# `repo` is the checkout this install was copied from: where /restack-upgrade
# pulls next. The skills do not need it to exist.

# `source` is where /restack-upgrade and the update check fetch releases from:
# this checkout's origin, or the project itself for a download. Read only when
# this directory is itself a checkout, so a ReStack copy vendored inside some
# other repository never records that repository's origin. git writes to
# stderr when there is no origin, which 'Stop' would turn into a terminating
# error, so it runs under 'Continue'.
$Source = ''
if ((Test-Path (Join-Path $RepoDir '.git')) -and (Get-Command git -ErrorAction SilentlyContinue)) {
    $previous = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $out = & git -C $RepoDir remote get-url origin 2>$null
        if ($LASTEXITCODE -eq 0 -and $out) { $Source = "$out".Trim() }
    } catch {
        $Source = ''
    } finally {
        $ErrorActionPreference = $previous
    }
}
if (-not $Source) { $Source = 'https://github.com/pmelander/restack.git' }

if (-not $DryRun) {
    if (-not (Test-Path $StateDir)) { New-Item -ItemType Directory -Path $StateDir -Force | Out-Null }
    $state = [ordered]@{
        version      = $Version
        source       = $Source
        repo         = $RepoDir
        skills_dir   = $SkillsDir
        method       = 'copy'
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

if ($nUnlinked -gt 0) {
    if ($DryRun) { $verb = 'would be' } else { $verb = 'were' }
    Write-Host ""
    Write-Host "Note: $nUnlinked symlink(s) from an older install $verb replaced with copies. The links were"
    Write-Host "removed as links; the checkout they pointed at is untouched."
}
if ($skillsEnvNote) { Write-Host ""; Write-Host "Note: $skillsEnvNote" }
if ($depNote) { Write-Host ""; Write-Host "Note: $depNote" }
if ($codexNote) { Write-Host ""; Write-Host "Note: $codexNote" }

if ($DryRun) {
    Write-Host ""; Write-Host "(dry run - nothing was written)"
} else {
    Write-Host ""; Write-Host "Type /restack in Claude Code to see the skills."
    Write-Host "The install is a copy: it keeps working if $RepoDir is moved or deleted."
}
