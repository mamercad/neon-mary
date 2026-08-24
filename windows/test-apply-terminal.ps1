$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$script = Join-Path $PSScriptRoot 'apply-terminal.ps1'

# --- 1. parse ---------------------------------------------------------------
$errors = $null; $tokens = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $script, [ref]$tokens, [ref]$errors)
if ($errors -and $errors.Count) {
    Write-Host "PARSE ERRORS:"; $errors | ForEach-Object {
        Write-Host ("  line {0}: {1}" -f $_.Extent.StartLineNumber, $_.Message) }
    exit 1
}
Write-Host "parse OK ($($tokens.Count) tokens)"

# --- 2. exercise the real jsonc stripper + merge on a realistic settings.json
# Dot-source just the helper by extracting it, so we test the shipped code
# rather than a reimplementation.
$src = Get-Content $script -Raw
$fnMatch = [regex]::Match($src,
    '(?s)function ConvertFrom-Jsonc \{.*?\n\}')
if (-not $fnMatch.Success) { Write-Host 'ConvertFrom-Jsonc not found'; exit 1 }
Invoke-Expression $fnMatch.Value

$sample = @'
{
    // Windows Terminal, with comments -- the real file has these.
    "$help": "https://aka.ms/terminal-documentation",
    "defaultProfile": "{guid-1}",
    /* block comment
       spanning lines */
    "profiles": {
        "defaults": { "font": { "face": "Cascadia Code" } },
        "list": [
            { "guid": "{guid-1}", "name": "PowerShell", "colorScheme": "Campbell" },
            { "guid": "{guid-2}", "name": "Ubuntu" }
        ]
    },
    "schemes": [
        { "name": "Campbell", "background": "#0C0C0C" }
    ],
    "keybindings": [
        { "command": "copy", "keys": "ctrl+c" },
        { "command": { "action": "sendInput", "input": "// not a comment" }, "keys": "ctrl+k" }
    ]
}
'@

$stripped = ConvertFrom-Jsonc $sample
$obj = $stripped | ConvertFrom-Json
Write-Host "jsonc strip + parse OK"

# the string containing "// not a comment" must survive intact
$ki = $obj.keybindings | Where-Object { $_.keys -eq 'ctrl+k' }
if ($ki.command.input -ne '// not a comment') {
    Write-Host "FAIL: stripper ate a string literal: '$($ki.command.input)'"
    exit 1
}
Write-Host "string literals preserved OK"

# unrelated settings survive
if ($obj.defaultProfile -ne '{guid-1}') { Write-Host 'FAIL: lost defaultProfile'; exit 1 }
if ($obj.profiles.defaults.font.face -ne 'Cascadia Code') { Write-Host 'FAIL: lost font'; exit 1 }
if ($obj.profiles.list.Count -ne 2) { Write-Host 'FAIL: lost profiles'; exit 1 }
Write-Host "unrelated settings preserved OK"

# --- 3. end-to-end against a temp settings.json ------------------------------
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) "wt-test-$(Get-Random)"
New-Item -ItemType Directory -Path $tmp | Out-Null
$settings = Join-Path $tmp 'settings.json'
Set-Content -Path $settings -Value $sample -Encoding UTF8

& $script -Variant tron -Mode dark -SettingsPath $settings | Out-Null
$after = ConvertFrom-Jsonc (Get-Content $settings -Raw) | ConvertFrom-Json

$want = 'Neon Mary: Tron (1982) dark'
$found = $after.schemes | Where-Object { $_.name -eq $want }
if (-not $found) {
    Write-Host "FAIL: scheme '$want' not installed"
    Write-Host ("  present: " + (($after.schemes | ForEach-Object { $_.name }) -join ', '))
    exit 1
}
Write-Host "scheme installed OK ($want)"
if ($after.profiles.defaults.colorScheme -ne $want) {
    Write-Host "FAIL: defaults.colorScheme = $($after.profiles.defaults.colorScheme)"
    exit 1
}
Write-Host "profiles.defaults.colorScheme set OK"
if (-not ($after.schemes | Where-Object { $_.name -eq 'Campbell' })) {
    Write-Host 'FAIL: pre-existing Campbell scheme was dropped'; exit 1
}
if ($after.defaultProfile -ne '{guid-1}') { Write-Host 'FAIL: lost defaultProfile'; exit 1 }
Write-Host "pre-existing config preserved OK"

# backup exists
$baks = Get-ChildItem $tmp -Filter '*.bak'
if ($baks.Count -lt 1) { Write-Host 'FAIL: no backup written'; exit 1 }
Write-Host "backup written OK ($($baks[0].Name))"

# --- 4. idempotence: re-run must not duplicate -------------------------------
& $script -Variant tron -Mode dark -SettingsPath $settings | Out-Null
$after2 = ConvertFrom-Jsonc (Get-Content $settings -Raw) | ConvertFrom-Json
$count = @($after2.schemes | Where-Object { $_.name -eq $want }).Count
if ($count -ne 1) { Write-Host "FAIL: re-run produced $count copies of the scheme"; exit 1 }
Write-Host "idempotent re-run OK (1 copy)"

# --- 5. both modes coexist ---------------------------------------------------
& $script -Variant tron -Mode light -SettingsPath $settings | Out-Null
$after3 = ConvertFrom-Jsonc (Get-Content $settings -Raw) | ConvertFrom-Json
$names = $after3.schemes | ForEach-Object { $_.name }
foreach ($n in @('Neon Mary: Tron (1982) dark', 'Neon Mary: Tron (1982) light')) {
    if ($names -notcontains $n) { Write-Host "FAIL: '$n' missing after installing both modes"; exit 1 }
}
Write-Host "dark and light coexist OK"

# --- 6. revert ---------------------------------------------------------------
& $script -Revert -SettingsPath $settings | Out-Null
$after4 = ConvertFrom-Jsonc (Get-Content $settings -Raw) | ConvertFrom-Json
if ($after4.schemes | Where-Object { $_.name -like 'Neon Mary:*' }) {
    Write-Host 'FAIL: revert left Neon Mary schemes behind'; exit 1
}
if (-not ($after4.schemes | Where-Object { $_.name -eq 'Campbell' })) {
    Write-Host 'FAIL: revert removed the user''s own scheme'; exit 1
}
if ($after4.profiles.defaults.PSObject.Properties.Name -contains 'colorScheme') {
    Write-Host 'FAIL: revert left colorScheme set'; exit 1
}
Write-Host "revert OK (Neon Mary gone, user scheme kept)"

Remove-Item $tmp -Recurse -Force
Write-Host ''
Write-Host 'ALL WINDOWS TERMINAL TESTS PASSED'
