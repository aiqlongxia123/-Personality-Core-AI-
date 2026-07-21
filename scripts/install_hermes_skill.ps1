<#
  install_hermes_skill.ps1
  Install personality-core skill into Hermes
#>

$SkillName = "personality-core"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir/.."

if ($env:HERMES_HOME) {
    $SkillsDir = "$env:HERMES_HOME/skills"
} elseif ($env:APPDATA) {
    $SkillsDir = "$env:APPDATA\cn.org.hermesagent.desktop\runtime\hermes-home\skills"
} else {
    $SkillsDir = "$HOME\.hermes\skills"
}

$TargetDir = "$SkillsDir\mlops\$SkillName"
Write-Host "Target: $TargetDir"

$dirs = @($TargetDir, "$TargetDir\references", "$TargetDir\references\src\personality_core", "$TargetDir\references\data")
foreach ($d in $dirs) { New-Item -ItemType Directory -Path $d -Force | Out-Null }

# SKILL.md
$src = "$ProjectRoot\docs\SKILL.md"
if (Test-Path $src) {
    Copy-Item $src "$TargetDir\SKILL.md" -Force
    Write-Host "  OK SKILL.md"
}

# src files
$srcDir = "$ProjectRoot\src\personality_core"
if (Test-Path $srcDir) {
    Copy-Item "$srcDir\*.py" "$TargetDir\references\src\personality_core\" -Force
    $count = (Get-ChildItem "$srcDir\*.py").Count
    Write-Host "  OK src/ ($count files)"
}

# data files
$dataDir = "$ProjectRoot\data"
if (Test-Path $dataDir) {
    Copy-Item "$dataDir\archetypes.json" "$TargetDir\references\data\" -Force -ErrorAction SilentlyContinue
    Copy-Item "$dataDir\archetypes_extended.json" "$TargetDir\references\data\" -Force -ErrorAction SilentlyContinue
    Write-Host "  OK data/"
}

# requirements
@"
sentence-transformers>=3.0
scikit-learn>=1.4
numpy>=1.26
jieba>=0.42
"@ | Out-File -FilePath "$TargetDir\references\requirements.txt" -Encoding utf8

Write-Host "  OK requirements.txt"

$skillOk = Test-Path "$TargetDir\SKILL.md"
$engineOk = Test-Path "$TargetDir\references\src\personality_core\engine.py"

if ($skillOk -and $engineOk) {
    Write-Host "DONE. skill_view('personality-core') to load."
} else {
    Write-Host "FAILED" -ForegroundColor Red
    exit 1
}
