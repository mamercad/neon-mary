<#
.SYNOPSIS
    Install a Neon Mary colour scheme into Windows Terminal and set it active.

.DESCRIPTION
    Merges the variant's scheme into Windows Terminal's settings.json and
    points profiles at it. Called automatically by apply-theme.ps1; usable on
    its own if you only want the terminal and not the desktop.

    Safety, because this edits a live config the user owns:
      * a timestamped backup is written before the first change
      * the existing JSON is parsed, mutated and re-serialised -- never
        regenerated from a template, so unrelated settings survive
      * settings.json permits // and /* */ comments (jsonc). PowerShell's
        ConvertFrom-Json rejects those on Windows PowerShell 5.1, so comments
        are stripped for parsing. That means a rewritten file loses comments;
        the backup preserves the original.
      * matching is by scheme name, so re-running updates in place rather
        than appending duplicates

    Windows Terminal keys schemes by "name", which is why the generated
    schemes are suffixed with their mode -- "Neon Mary: Tron (1982) dark" and
    "... light" are two distinct entries that can coexist.

.PARAMETER Variant
    blade-runner | crow | amelie | tron | dark-city | fifth-element |
    grand-budapest | evangelion

.PARAMETER Mode
    dark or light.

.PARAMETER Scope
    Which profiles to repoint. 'defaults' (default) sets it in
    profiles.defaults so every profile inherits it. 'all' also overwrites any
    per-profile colorScheme that would otherwise shadow the default.
    'none' installs the scheme without activating it.

.PARAMETER SettingsPath
    Override the settings.json location. Autodetected otherwise, covering the
    Store build, the unpackaged/Scoop build, and Windows Terminal Preview.

.PARAMETER Revert
    Remove every Neon Mary scheme and clear references to them.

.EXAMPLE
    .\apply-terminal.ps1 -Variant tron -Mode dark

.EXAMPLE
    .\apply-terminal.ps1 -Variant grand-budapest -Mode light -Scope all
#>
[CmdletBinding(SupportsShouldProcess)]
[Diagnostics.CodeAnalysis.SuppressMessageAttribute(
    'PSReviewUnusedParameter', 'SettingsPath',
    Justification = 'Read inside Find-TerminalSettings via scope inheritance.')]
param(
    [ValidateSet('blade-runner', 'crow', 'amelie', 'tron', 'dark-city',
                 'fifth-element', 'grand-budapest', 'evangelion', 'matrix',
                 'solaris', 'suspiria', 'akira', 'dune')]
    [string]$Variant,

    [ValidateSet('dark', 'light')]
    [string]$Mode,

    [ValidateSet('defaults', 'all', 'none')]
    [string]$Scope = 'defaults',

    [string]$SettingsPath,

    [switch]$Revert
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

function Find-TerminalSettings {
    # PSUseSingularNouns: "Settings" is the actual name of the thing
    # (settings.json), not a plural of "Setting".
    # PSReviewUnusedParameter: $SettingsPath is read here via scope inheritance
    # from the param block; the analyzer does not track that.
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseSingularNouns', '')]
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSReviewUnusedParameter', '')]
    param()
    if ($SettingsPath) {
        if (-not (Test-Path $SettingsPath)) {
            throw "settings.json not found at -SettingsPath: $SettingsPath"
        }
        return $SettingsPath
    }
    $candidates = @(
        # Store / MSIX install
        "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json",
        # Preview
        "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe\LocalState\settings.json",
        # unpackaged / Scoop / portable
        "$env:LOCALAPPDATA\Microsoft\Windows Terminal\settings.json"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

function ConvertFrom-Jsonc {
    <#  settings.json is jsonc. Strip // and /* */ so 5.1's parser accepts it,
        without touching sequences inside string literals. #>
    param([string]$Text)
    $sb = [System.Text.StringBuilder]::new()
    $inStr = $false; $esc = $false; $i = 0
    while ($i -lt $Text.Length) {
        $ch = $Text[$i]
        if ($inStr) {
            [void]$sb.Append($ch)
            if ($esc)              { $esc = $false }
            elseif ($ch -eq '\')   { $esc = $true }
            elseif ($ch -eq '"')   { $inStr = $false }
            $i++; continue
        }
        if ($ch -eq '"') { $inStr = $true; [void]$sb.Append($ch); $i++; continue }
        if ($ch -eq '/' -and $i + 1 -lt $Text.Length) {
            if ($Text[$i + 1] -eq '/') {
                while ($i -lt $Text.Length -and $Text[$i] -ne "`n") { $i++ }
                continue
            }
            if ($Text[$i + 1] -eq '*') {
                $i += 2
                while ($i + 1 -lt $Text.Length -and
                       -not ($Text[$i] -eq '*' -and $Text[$i + 1] -eq '/')) { $i++ }
                $i += 2
                continue
            }
        }
        [void]$sb.Append($ch); $i++
    }
    return $sb.ToString()
}

$settings = Find-TerminalSettings
if (-not $settings) {
    Write-Warning 'Windows Terminal settings.json not found. Skipping terminal setup.'
    Write-Warning 'Install Windows Terminal, launch it once, then re-run this script.'
    return
}
Write-Host "  settings: $settings"

$raw = Get-Content -Path $settings -Raw -Encoding UTF8
try {
    $json = ConvertFrom-Jsonc $raw | ConvertFrom-Json
} catch {
    throw "Could not parse $settings as JSON: $($_.Exception.Message)"
}

if ($WhatIfPreference) {
    if ($Revert) {
        Write-Output "WHATIF: remove Neon Mary:* schemes from $settings"
        Write-Output 'WHATIF: clear Neon Mary profiles.defaults/profile colorScheme references'
        Write-Output "WHATIF: preserve existing settings and schemes; no backup written"
        return
    }
    if (-not $Variant) { throw 'Specify -Variant (or -Revert).' }
    if (-not $Mode) {
        $Mode = if ($Variant -eq 'grand-budapest') { 'light' } else { 'dark' }
    }
    $schemeFile = if ($Variant -eq 'blade-runner') {
        Join-Path $repoRoot "terminals\$Mode\windows-terminal.json"
    } else {
        Join-Path $repoRoot "terminals\$Variant\$Mode\windows-terminal.json"
    }
    if (-not (Test-Path $schemeFile)) { throw "Missing scheme file: $schemeFile" }
    $scheme = Get-Content $schemeFile -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Output "WHATIF: install scheme '$($scheme.name)' into $settings"
    Write-Output "WHATIF: set profiles.defaults.colorScheme (scope: $Scope)"
    Write-Output 'WHATIF: no files or registry values changed'
    return
}

# Back up before the first mutation, always.
$stamp  = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = "$settings.neon-mary-$stamp.bak"
if ($PSCmdlet.ShouldProcess($backup, 'Write backup of settings.json')) {
    Copy-Item $settings $backup -Force
    Write-Host "  backup:   $backup"
}

if (-not $json.schemes) {
    $json | Add-Member -NotePropertyName schemes -NotePropertyValue @() -Force
}
$schemes = @($json.schemes)

if ($Revert) {
    $before = $schemes.Count
    $schemes = @($schemes | Where-Object { $_.name -notlike 'Neon Mary:*' })
    Write-Host "  removed $($before - $schemes.Count) Neon Mary scheme(s)"
    if ($json.profiles -and $json.profiles.defaults -and
        $json.profiles.defaults.colorScheme -like 'Neon Mary:*') {
        $json.profiles.defaults.PSObject.Properties.Remove('colorScheme')
        Write-Host '  cleared profiles.defaults.colorScheme'
    }
    if ($json.profiles -and $json.profiles.list) {
        foreach ($p in $json.profiles.list) {
            if ($p.colorScheme -like 'Neon Mary:*') {
                $p.PSObject.Properties.Remove('colorScheme')
            }
        }
    }
    $json.schemes = $schemes
    if ($PSCmdlet.ShouldProcess($settings, 'Remove Neon Mary schemes')) {
        $json | ConvertTo-Json -Depth 32 |
            Set-Content -Path $settings -Encoding UTF8
        Write-Host '  Windows Terminal reverted.'
    }
    return
}

if (-not $Variant) { throw 'Specify -Variant (or -Revert).' }
if (-not $Mode) {
    $Mode = if ($Variant -eq 'grand-budapest') { 'light' } else { 'dark' }
}

$schemeFile = if ($Variant -eq 'blade-runner') {
    Join-Path $repoRoot "terminals\$Mode\windows-terminal.json"
} else {
    Join-Path $repoRoot "terminals\$Variant\$Mode\windows-terminal.json"
}
if (-not (Test-Path $schemeFile)) { throw "Missing scheme file: $schemeFile" }

$scheme = Get-Content $schemeFile -Raw -Encoding UTF8 | ConvertFrom-Json
$name   = $scheme.name
Write-Host "  scheme:   $name"

# Replace in place if present, otherwise append -- never duplicate.
$existing = $schemes | Where-Object { $_.name -eq $name }
if ($existing) {
    $schemes = @($schemes | Where-Object { $_.name -ne $name })
    Write-Host '  (replacing existing entry of the same name)'
}
$schemes += $scheme
$json.schemes = $schemes

if ($Scope -ne 'none') {
    if (-not $json.profiles) {
        $json | Add-Member -NotePropertyName profiles -NotePropertyValue ([pscustomobject]@{}) -Force
    }
    if (-not $json.profiles.defaults) {
        $json.profiles | Add-Member -NotePropertyName defaults -NotePropertyValue ([pscustomobject]@{}) -Force
    }
    $json.profiles.defaults | Add-Member -NotePropertyName colorScheme -NotePropertyValue $name -Force
    Write-Host "  set profiles.defaults.colorScheme = $name"

    if ($Scope -eq 'all' -and $json.profiles.list) {
        $n = 0
        foreach ($p in $json.profiles.list) {
            if ($p.PSObject.Properties.Name -contains 'colorScheme') {
                $p.colorScheme = $name; $n++
            }
        }
        if ($n) { Write-Host "  overwrote colorScheme on $n profile(s)" }
    }
}

if ($PSCmdlet.ShouldProcess($settings, "Install scheme '$name'")) {
    $json | ConvertTo-Json -Depth 32 | Set-Content -Path $settings -Encoding UTF8
    Write-Host '  Windows Terminal updated. Open a new tab to see it.'
    Write-Host '  NOTE: jsonc comments are not preserved; the backup has them.'
}
