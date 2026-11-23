#!/usr/bin/env bash
# macOS/Linux 一键安装（OpenCode 全局；其他 Agent 改 DEST 路径即可）
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SKILL="$HERE/google-ai-offer-subscription"
AGENT="${1:-opencode}"
case "$AGENT" in
  opencode) SUB=".config/opencode/skills" ;;
  claude)   SUB=".claude/skills" ;;
  codex)    SUB=".codex/skills" ;;
  *)        SUB=".config/opencode/skills" ;;
esac
DEST="$HOME/$SUB/google-ai-offer-subscription"
mkdir -p "$(dirname "$DEST")"
rm -rf "$DEST"
cp -R "$SKILL" "$DEST"
echo "已安装到: $DEST"
echo "重启 Agent 后生效；也可在会话里用 @google-ai-offer-subscription 显式加载"
