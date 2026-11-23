# Google AI Offer Subscription Skill

一个跨 Agent 通用的技能包：在已 root 的安卓模拟器上，通过 Google Play 结算库（BillingClient）查询 Google AI 的隐藏优惠 offer，拉起收银台并在确认 ¥0 后订阅；支持订阅升级叠加，把免费期延长到最长 24 个月。

> 这是非官方工具。优惠是否可领由服务方按账号投放，不保证成功。仅用于你自己的账号、设备和付款方式；使用前请自行评估是否符合相关服务条款。

## 背景

Google One 的部分促销 offer（如 AI Pro 的 12 个月免费、AI Ultra 的限时折扣）不会显示在普通页面上，只存在于 Play 结算库对特定账号的返回值里。本 skill 通过 Frida 注入 Google One 进程调用 BillingClient 查询这些 offer，挑出免费期最长的档位拉起收银台，并在确认金额为 0 时才点击订阅。

在 Android 15 模拟器上，上游脚本使用的 `Java.choose` 因 libart 符号缺失无法拿到前台 Activity，导致「查得到 offer、拉不起收银台」。本包附带实测修复版 `ultra0_patched.py`（改用 `ActivityThread.mActivities` 获取 Activity），并提供重新打补丁的脚本。

## 功能

- 环境探测：adb 连接、root、屏幕密度、frida-server、Google 组件状态（只读）
- offer 查询：`--list` 模式零风险，不消耗试用资格
- 订阅与叠加：12 个月免费 → +6 个月 → +6 个月（升级模式自动读 purchaseToken）
- 验收：读 Play 订阅页的下次付款日期，确认每次叠加生效
- 故障排查：常见坑的对照表

## 目录结构

```
google-ai-offer-subscription/
├── SKILL.md                  # 技能主入口（Agent 按需加载）
├── scripts/
│   ├── ultra0.py             # 上游公开脚本原始版
│   ├── ultra0_patched.py     # Android 15 兼容修复版（优先用）
│   ├── patch_ultra.py        # 从原始版重新生成修复版
│   ├── device_probe.py       # 只读环境探测
│   ├── read_screen.py        # uiautomator 读屏
│   └── verify_subscription.py# 订阅状态验收 + 截图
├── references/
│   ├── setup.md              # 一次性环境准备
│   ├── workflow.md           # 完整命令流程
│   └── troubleshooting.md    # 故障排查
└── LICENSE
```

## 安装（跨 Agent）

技能遵循通用 Agent Skills 规范（`SKILL.md` + frontmatter）。把整个 `google-ai-offer-subscription/` 目录复制到你所用 Agent 的 skills 目录：

| Agent | 全局目录 | 项目目录 |
|---|---|---|
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex CLI | `~/.codex/skills/` | `.agents/skills/` |

Windows PowerShell 一键装到 OpenCode 全局目录（其他 Agent 改路径即可）：

```powershell
$src = (Resolve-Path .\google-ai-offer-subscription).Path
$dst = Join-Path $env:USERPROFILE ".config\opencode\skills\google-ai-offer-subscription"
New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
Copy-Item -Recurse -Force $src $dst
```

安装后重启 Agent（或在会话里 `@google-ai-offer-subscription` 显式加载）。

## 快速开始

1. 先读 `SKILL.md` 和 `references/setup.md`，满足前置条件
2. `python scripts/device_probe.py` 确认环境
3. `python scripts/ultra0_patched.py --account <你的邮箱> --no-add --no-switch --check` 自检
4. 按 `references/workflow.md` 查询 → 下单 → 验收

**重要**：脚本不会索要密码或卡号；账号请自行在模拟器内登录，卡请自行在 Play 内绑定。下单前务必人工核对收银台的套餐名和金额；非 ¥0 不要点订阅。

## 上游与许可

- `scripts/ultra0.py` 来自公开项目 `github.com/gylive/google-ultra`，按其原许可使用；本仓库的补丁、文档与辅助脚本为 MIT（见 LICENSE）。
- 本仓库不包含任何账号、邮箱、卡号、设备标识、token 或运行报告；运行产生的 `ultra0-report/` 与截图已被 `.gitignore` 排除，请勿提交。

## 免责声明

本工具仅供个人学习与自动化操作自有账号使用。作者不对优惠资格、服务方政策变化、账号风险或任何费用承担责任。付费档必须经使用者明确知情同意。
