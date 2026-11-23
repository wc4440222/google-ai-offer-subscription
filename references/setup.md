# 一次性环境准备

> 本文件只写通用步骤，不含任何个人信息。所有 `<...>` 占位符由使用者替换。

## 1. 安卓模拟器

- MuMu 模拟器 6.x（Android 12 或 15 均可，自带 root）或其他已 root 的安卓模拟器/真机
- 开启 USB 调试；模拟器走 adb TCP 端口连接（MuMu 6 默认 `127.0.0.1:16384`）
- 电脑安装 Android platform-tools，确认 `adb connect <ADB_HOST>:<ADB_PORT>` 后 `adb shell id` 显示 `uid=0(root)`

## 2. Google 服务

- 在模拟器里用 Google 安装器安装：Play 商店、Google 服务框架（GMS）、Google App、Google One、Gemini、YouTube
- **常见坑**：安装器装完后个别组件处于默认停用状态（`enabled=0`），表现为 Gemini 死循环提示"前往 Play 商店下载 Google"。检查并启用：
  ```
  adb shell dumpsys package com.google.android.googlequicksearchbox | grep enabled
  adb shell pm enable com.google.android.googlequicksearchbox
  adb shell pm enable com.google.android.gms
  adb shell pm enable com.google.android.gsf
  ```
- 在模拟器设置里登录目标 Google 账号（**不要用主力号试**）
- 在 Play 商店绑定一张付款方式（订阅验证需要；建议低额度卡）
- 确认 Play 商店能正常打开、能加载页面（出口 IP 建议为优惠投放友好的地区，如美国）

## 3. 显示设置（避免 Pad UI）

Google 按 dp 宽度判断手机/平板（阈值 600dp）。若分辨率 1080px、密度 240dpi → 720dp，会被当平板下发双栏 Pad UI。正确组合：

```
adb shell wm size 1080x1920
adb shell wm density 320   # 1080/320*160=540dp <600，手机 UI；420dpi 则≈411dp，更接近真机观感
```

MuMu 设置中心里可选 `1080 x 1920, 480 DPI (手机)` 等手机预设；勾选「固定窗口大小」「记住关闭时窗口位置」，避免自动恢复。

## 4. Python 与 Frida

- Python 3.9+（需能 pip 安装）
- `pip install frida==16.5.9`（**必须 16.x**，17.x 移除了 Java bridge 不可用）
- frida-server 不需要手动准备：脚本首次自检会按设备 ABI 自动下载并推送启动

## 5. 上游脚本

仓库 `scripts/` 已包含原始版 `ultra0.py` 和修复版 `ultra0_patched.py`。若从上游更新了原始版，重跑补丁：

```
python scripts/patch_ultra.py
```

补丁内容：把 `getActivity()` 从 `Java.choose("android.app.Activity")` 改为通过 `ActivityThread.currentActivityThread().mActivities` 遍历 `ActivityClientRecord.activity` 字段取前台 Activity（Android 15 上 Java.choose 依赖的 libart 符号缺失）。
