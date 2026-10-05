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

  With -Mods it also installs the mods in mods\restack-* beside the skills,
  where Claude Code loads each as a plugin (<name>@skills-dir; ADR-029). The
  choice is recorded, so a later plain run keeps it.

  Windows-native equivalent of ./setup. Safe to re-run.

  SAFETY: only ever creates, replaces or removes entries whose names begin
  with "restack-". Nothing else in the skills directory is touched, so it
  cannot damage another skill suite. A link left by an older symlinked install
  is removed as a link, never followed: Windows PowerShell 5.1's
  Remove-Item -Recurse on a directory link can delete the contents of the
  directory it points at, which would be the checkout.

.PARAMETER Mods
  Also install the mods: the journey band above the prompt (ADR-029).
  Remembered: later runs keep them up to date.

.PARAMETER NoMods
  Remove the mods, and stop installing them.

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
    [switch]$Mods,
    [switch]$NoMods,
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

if ($Mods -and $NoMods) {
    Write-Host "Error: -Mods and -NoMods contradict each other."
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
# install. A mod's .claude-plugin\types\ is left out: Claude Code writes it
# there when it loads a mod for development, and it is never installed.
function Get-TreeHash([string]$Dir) {
    $map = @{}
    Get-ChildItem -LiteralPath $Dir -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($Dir.Length)
        if ($rel -notlike '\.claude-plugin\types\*') {
            $map[$rel] = (Get-FileHash -LiteralPath $_.FullName).Hash
        }
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

# --- mods (ADR-029) -----------------------------------------------------------
# A mod is a plugin directory: Claude Code loads one it finds under
# ~\.claude\skills\ as <name>@skills-dir. Installed only on request; the
# request is recorded in install.json, so a plain re-run (and /restack-upgrade)
# keeps what was chosen. Without a record, an installed mod counts as chosen.

$ModRoot = Join-Path $RepoDir 'mods'
$ModSources = @()
if (Test-Path $ModRoot) {
    $ModSources = @(Get-ChildItem -Path $ModRoot -Directory -Filter 'restack-*' | Sort-Object Name)
}

$RecordPath = Join-Path $StateDir 'install.json'
if ($Mods) {
    $WantMods = $true
} elseif ($NoMods) {
    $WantMods = $false
} else {
    $WantMods = $false
    if (Test-Path $RecordPath) {
        try {
            $previousRecord = Get-Content -LiteralPath $RecordPath -Raw | ConvertFrom-Json
            if ($previousRecord.mods -eq $true) { $WantMods = $true }
        } catch {
            $WantMods = $false
        }
    } else {
        foreach ($m in $ModSources) {
            if (Test-Path (Join-Path $SkillsDir "$($m.Name)\.claude-plugin\plugin.json")) { $WantMods = $true }
        }
    }
}

# Refuse a mod Claude Code would not load, or one that would take a skill's
# place: same check as the skills', before anything is written.
if ($WantMods) {
    foreach ($m in $ModSources) {
        $manifest = Join-Path $m.FullName '.claude-plugin\plugin.json'
        $hooks = Join-Path $m.FullName 'hooks\hooks.json'
        if (-not (Test-Path $manifest) -or -not (Test-Path $hooks)) {
            Write-Error "mods\$($m.Name) has no .claude-plugin\plugin.json or hooks\hooks.json - refusing to install a broken mod."
        }
        if (Test-Path (Join-Path $SourceRoot $m.Name)) {
            Write-Error "mods\$($m.Name) has the name of a skill - one would replace the other."
        }
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

$nNew = 0; $nUpd = 0; $nSame = 0; $nDel = 0; $nUnlinked = 0; $nMods = 0

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

# --- install the mods ---------------------------------------------------------

if ($WantMods) {
    foreach ($m in $ModSources) {
        $name = $m.Name
        $dest = Join-Path $SkillsDir $name
        $destItem = Get-Item -LiteralPath $dest -Force -ErrorAction SilentlyContinue
        $nMods++

        $action = 'update'
        if ($null -eq $destItem) {
            $action = 'install'; $nNew++
        } elseif (Test-Link $destItem) {
            $nUpd++
        } elseif (Test-SameTree $m.FullName $dest) {
            $action = 'unchanged'; $nSame++
        } else {
            $nUpd++
        }

        if ($action -ne 'unchanged') { Say "  $action  $name  (mod)" }
        if ($DryRun -or $action -eq 'unchanged') { continue }

        if ($null -ne $destItem) { Remove-Entry $destItem }
        Copy-Item -LiteralPath $m.FullName -Destination $dest -Recurse -Force
        $generated = Join-Path $dest '.claude-plugin\types'
        if (Test-Path -LiteralPath $generated) { Remove-Item -LiteralPath $generated -Recurse -Force }
    }
}

# --- remove skills deleted upstream -----------------------------------------
# The reason a plain recursive copy is not good enough: a skill removed or
# renamed upstream stays installed forever, and the user keeps invoking a
# command the project no longer has.

if (Test-Path $SkillsDir) {
    $installed = @(Get-ChildItem -Path $SkillsDir -Directory -Filter 'restack-*' -Force -ErrorAction SilentlyContinue)
    foreach ($d in $installed) {
        if (Test-Path (Join-Path $SourceRoot $d.Name)) { continue }
        if (Test-Path (Join-Path $ModRoot $d.Name)) {
            if ($WantMods) { continue }
            Say "  remove   $($d.Name)  (mod; -NoMods)"
        } else {
            Say "  remove   /$($d.Name)  (no longer in ReStack)"
        }
        $nDel++
        if (-not $DryRun) { Remove-Entry $d }
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
        mods         = [bool]$WantMods
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
    $modsPart = ''
    if ($nMods -gt 0) { $modsPart = ", $nMods mod(s)" }
    Write-Host "ReStack v$Version - already up to date ($($nSame - $nMods) skills$modsPart)."
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

if ($WantMods -and $nMods -gt 0) {
    $modNames = ($ModSources | ForEach-Object { $_.Name }) -join ' '
    Write-Host ""
    Write-Host "Mods: $modNames load as plugins in new sessions (/reload-plugins in an open one)."
    Write-Host "The journey band hides with /restack-view band off; .\setup.ps1 -NoMods removes it."
} elseif ($ModSources.Count -gt 0 -and -not $NoMods) {
    Write-Host ""
    Write-Host "Optional: .\setup.ps1 -Mods adds the journey band above the prompt (ADR-029)."
}

if ($DryRun) {
    Write-Host ""; Write-Host "(dry run - nothing was written)"
} else {
    Write-Host ""; Write-Host "Type /restack in Claude Code to see the skills."
    Write-Host "The install is a copy: it keeps working if $RepoDir is moved or deleted."
}
