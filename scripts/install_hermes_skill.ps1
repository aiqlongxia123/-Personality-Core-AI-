<# 
  install_hermes_skill.ps1
  将 personality-core（渊）技能安装到本地 Hermes 系统

  用法: powershell -ExecutionPolicy Bypass -File scripts/install_hermes_skill.ps1
#>

$SkillName = "personality-core"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir/.."

# ── 找 Hermes 技能目录 ──
if ($env:HERMES_HOME) {
    $SkillsDir = "$env:HERMES_HOME/skills"
} elseif ($env:APPDATA) {
    $Base = "$env:APPDATA\cn.org.hermesagent.desktop\runtime\hermes-home"
    $SkillsDir = "$Base\skills"
} else {
    $SkillsDir = "$HOME\.hermes\skills"
}

$TargetDir = "$SkillsDir\mlops\$SkillName"
Write-Host "📦 安装目录: $TargetDir" -ForegroundColor Cyan

# ── 创建目录 ──
New-Item -ItemType Directory -Path "$TargetDir" -Force | Out-Null

# ── 复制 SKILL.md ──
$DocSkill = "$ProjectRoot\docs\SKILL.md"
if (Test-Path $DocSkill) {
    Copy-Item $DocSkill "$TargetDir\SKILL.md" -Force
    Write-Host "  ✅ SKILL.md" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  docs/SKILL.md 不存在" -ForegroundColor Yellow
}

# ── 复制 quickstart 入口 ──
$Quickstart = "$ProjectRoot\quickstart.py"
if (Test-Path $Quickstart) {
    New-Item -ItemType Directory -Path "$TargetDir\references" -Force | Out-Null
    Copy-Item $Quickstart "$TargetDir\references\quickstart.py" -Force
    Write-Host "  ✅ references/quickstart.py" -ForegroundColor Green
}

# ── 验证 ──
$SkillFile = "$TargetDir\SKILL.md"
if (Test-Path $SkillFile) {
    Write-Host ""
    Write-Host "✅ 安装成功！" -ForegroundColor Green
    Write-Host "   技能位置: $TargetDir"
    Write-Host ""
    Write-Host "🧠 下次启动 Hermes 后，说「渊」「人格引擎」等关键词会自动触发。"
    Write-Host "   或手动加载: skill_view('personality-core')"
    Write-Host ""
    Write-Host "💬 对话时会以「渊」的人格回应（攻击性0.75 温暖度0.65 神秘感0.90 理性度0.95 支配性0.80）"
    Write-Host "   说「换清晏」「恢复正常」「换尼采」切换人格。"
} else {
    Write-Host "❌ 安装失败，SKILL.md 未写入" -ForegroundColor Red
    exit 1
}
