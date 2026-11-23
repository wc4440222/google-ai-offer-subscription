---
name: google-ai-offer-subscription
description: 在安卓模拟器（MuMu）上通过 Google Play 结算库查询并开通 Google AI Pro/Ultra 的隐藏免费试用或促销 offer，支持订阅升级叠加（12+6+6 个月）。当用户提到 Google AI 优惠、Pro 免费、Ultra 一折、试用叠加、Play 收银台、MuMu 领 Google 会员时使用。
license: MIT
compatibility: Agent Skills 通用规范（OpenCode / Claude Code / Codex CLI 等）
---

# Google AI 优惠订阅（MuMu + Frida）

在已 root 的安卓模拟器上，用 Frida 注入 Google One 进程调用 Play 的 BillingClient，查询**隐藏 offer**（普通页面看不到），拉起收银台，在确认 ¥0 后订阅；支持用订阅升级模式把多个免费档叠加到最长 24 个月。

> ⚠️ 适用范围与风险：仅用于**用户自己的账号、自己的设备、自己的付款方式**。优惠是否可领由 Google 按账号画像投放，本 skill 不保证成功、不绕过付费墙。付费档（非 ¥0）必须由用户明确同意后才可确认。使用前请自行评估是否符合相关服务条款。

## 何时使用

- 用户想查自己的 Google 账号有没有 Pro 免费 12 个月 / Ultra 1 折等隐藏优惠
- 想把已到手的免费档叠加延长（12 个月 + 6 个月 × 2 = 24 个月）
- 调试 Play Billing 流程、验证订阅状态

## 硬护栏（必须遵守）

1. **绝不收集或写入凭据**：账号密码、2FA、卡号、offer token 不写入任何文件；使用 `--no-add --no-switch`（账号由用户在模拟器内自行登录）
2. **写操作前必须人工核对**：下单/叠加前，读屏或截图确认收银台显示套餐名正确 + 金额为 ¥0/免费试用；弹窗出现时把看到的内容告诉用户
3. **非 ¥0 一律不点订阅**，除非用户明确授权付费档
4. **每次叠加后必须验收**：读订阅页「下次付款日期」，未 +6 个月则停止后续叠加
5. 任何取消订阅操作都要用户明确同意（默认保留订阅，靠到期提醒处理）
6. `--force` 仅用于新号读屏读不到账号的场景，**使用前必须确认设备里只有目标账号一个 Google 账号**（`adb shell dumpsys account | grep name=`），否则可能跑错号

## 工作流程

1. 读 `references/setup.md`，确认环境前置条件已满足（模拟器/root/frida/Google 登录/绑卡/手机 UI 密度）
2. 读 `references/workflow.md` 获取完整命令序列和参数说明
3. 连接与自检：`adb connect <ADB_HOST>:<ADB_PORT>` → `python scripts/ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --check`
4. 清场：强停 `com.android.vending` 与 `com.google.android.apps.subscriptions.red`（否则账号读屏会失败）
5. 查询（零风险）：`--list --plan pro12` 看免费档；`--list --plan 5x|20x --allow-paid --sku <SKU>` 看 Ultra 促销
6. 下单/叠加：`--plan pro12` → `--plan pro6 --stack` → `--plan pro6b --stack`
7. 每步按硬护栏核对，完成后读订阅页日期并截图留档（本地存，勿上传）

## 常见故障

见 `references/troubleshooting.md`：Java.choose 符号缺失（必须用 patched 版）、wrong_account（Play 停在详情页）、双栏价格误判（人工核对）、Google 组件 enabled=0、Pad UI（密度）、$1 预授权等。

## 文件说明

- `scripts/ultra0.py`：上游公开脚本原始版（来源 github.com/gylive/google-ultra）
- `scripts/ultra0_patched.py`：在本机 Android 15 模拟器上实测修复版（修复 `Java.choose` 的 libart 符号缺失）——**优先使用**
- `scripts/patch_ultra.py`：把原始版重新打补丁的脚本（升级上游后重跑）
- `scripts/device_probe.py`：adb 连接、root、frida、屏幕参数只读探测
- `scripts/read_screen.py`：uiautomator 读屏 / 截图辅助
- `references/`：环境准备、命令流程、故障排查
