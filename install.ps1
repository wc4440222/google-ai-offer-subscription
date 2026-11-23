# Windows 一键安装（OpenCode 全局；其他 Agent 改 $Dst 路径即可）
param([string]$Agent = "opencode")
$src = Split-Path -Parent $MyInvocation.MyCommand.Path
$skill = Join-Path $src "google-ai-offer-subscription"
$sub = switch ($Agent) {
  "opencode" { ".config\opencode\skills" }
  "claude"   { ".claude\skills" }
  "codex"    { ".codex\skills" }
  default    { ".config\opencode\skills" }
}
$dst = Join-Path $env:USERPROFILE $sub
New-Item -ItemType Directory -Force -Path $dst | Out-Null
$target = Join-Path $dst "google-ai-offer-subscription"
if (Test-Path $target) { Remove-Item -Recurse -Force $target }
Copy-Item -Recurse -Force $skill $target
Write-Host "已安装到: $target"
Write-Host "重启 Agent 后生效；也可在会话里用 @google-ai-offer-subscription 显式加载"
