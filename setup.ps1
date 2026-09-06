<#
.SYNOPSIS
  ReStack setup - install or update the skills for Claude Code.

.DESCRIPTION
  Copies (or symlinks) every skills\restack-* directory into the Claude Code
  skills directory, removes ReStack skills that no longer exist upstream, and
  records where the install came from so /restack-upgrade can find it later.

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
  Install into this directory instead of $HOME\.claude\skills.

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

if ($Target) {
    $SkillsDir = $Target
} elseif ($env:CLAUDE_SKILLS_DIR) {
    $SkillsDir = $env:CLAUDE_SKILLS_DIR
} else {
    $SkillsDir = Join-Path $env:USERPROFILE '.claude\skills'
}

if ($Symlink) { $Method = 'symlink' } else { $Method = 'copy' }
$StateDir = Join-Path $env:USERPROFILE '.restack'

function Say([string]$Message) { if (-not $Quiet) { Write-Host $Message } }

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
            $srcSkill = Join-Path $s.FullName 'SKILL.md'
            $dstSkill = Join-Path $dest 'SKILL.md'
            if ((Test-Path $dstSkill) -and
                ((Get-FileHash $srcSkill).Hash -eq (Get-FileHash $dstSkill).Hash)) {
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

# --- record the install ------------------------------------------------------

if (-not $DryRun) {
    if (-not (Test-Path $StateDir)) { New-Item -ItemType Directory -Path $StateDir -Force | Out-Null }
    $state = [ordered]@{
        version      = $Version
        repo         = $RepoDir
        skills_dir   = $SkillsDir
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

if ($depNote) { Write-Host ""; Write-Host "Note: $depNote" }

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
