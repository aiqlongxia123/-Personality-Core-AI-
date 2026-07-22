# Hermes Agent 技能安装脚本
# 用法：powershell -ExecutionPolicy Bypass -File scripts/install_hermes_skill.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$SkillDir = "$env:USERPROFILE\.hermes\skills\mlops\personality-core"

Write-Host "=== 安装 Personality Core 到 Hermes Agent ===" -ForegroundColor Cyan
Write-Host "项目路径: $ProjectRoot"
Write-Host "技能目录: $SkillDir"

# 创建技能目录
New-Item -ItemType Directory -Force -Path $SkillDir | Out-Null

# 复制 SKILL.md（从 docs 或技能包）
$SkillMdSource = "$ProjectRoot\docs\SKILL.md"
if (Test-Path $SkillMdSource) {
    Copy-Item $SkillMdSource -Destination "$SkillDir\SKILL.md" -Force
    Write-Host "✓ SKILL.md 已复制" -ForegroundColor Green
} else {
    Write-Host "⚠ docs/SKILL.md 不存在，使用已安装的技能版本" -ForegroundColor Yellow
}

# 复制参考文档
$RefsDir = "$SkillDir\references"
New-Item -ItemType Directory -Force -Path $RefsDir | Out-Null
$RefsSource = "$ProjectRoot\docs\references"
if (Test-Path $RefsSource) {
    Copy-Item "$RefsSource\*" -Destination $RefsDir -Force -Recurse
    Write-Host "✓ 参考文档已复制" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== 安装完成 ===" -ForegroundColor Green
Write-Host "重启 Hermes Agent 后，技能自动生效。"
Write-Host "对话中说「换渊」「换清晏」即可切换人格。"
