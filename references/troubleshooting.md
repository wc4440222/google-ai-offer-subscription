# 故障排查

## Frida / 注入类

| 症状 | 原因 | 解决 |
|---|---|---|
| `choose_err: libart.so: unable to find export ...EnsurePluginLoaded...` → `no_activity` → `launch_failed` | Android 15 上 `Java.choose` 依赖的 libart 符号缺失（frida 16.5.9 兼容问题），查得到 offer 但拉不起收银台 | 用 `ultra0_patched.py`（已修复 `getActivity()`），不要用原始版 |
| 升级上游后补丁失效 | 上游脚本改动了 `getActivity` 函数 | 重跑 `python scripts/patch_ultra.py` |
| frida-server 推送/启动失败 | 设备 ABI 识别失败或网络 | 检查 `adb shell getprop ro.product.cpu.abi`；脚本会自动下载对应架构的 frida-server |

## 账号 / 流程类

| 症状 | 原因 | 解决 |
|---|---|---|
| 弹出 Google 登录页让重新登录 | 漏加 `--no-add`，走了自动加号流程 | 所有命令都带 `--no-add` |
| `wrong_account`（当前账号"未知"） | Play 停在订阅详情页，读屏读不到「账号和设置」按钮里的邮箱 | 先强停 `com.android.vending` 和 `com.google.android.apps.subscriptions.red` 后重跑 |
| `wrong_account` 反复出现（新号尤其常见） | 新号的 Play 主页/界面元素与旧号不同，读屏找不到邮箱按钮 | **确认设备里只有目标账号一个 Google 账号后**（`adb shell dumpsys account \| grep name=`），用 `--force` 跳过读屏校验；脚本会打印"已跳过 Play 账号校验（--force）" |
| 查不到 offer / `offers: []` | 该账号未被投放该优惠 | 正常现象，查询不消耗资格；可换档位或接受无资格 |
| 收银台没弹出来 | Play 进程异常/网络瞬断 | 重跑；连续失败重启模拟器 |
| 新号注册卡在二维码/手机验证 | 机房 IP（hosting/data center）+ 全新设备 + 手机号组合被 Google 风控识别 | 这是 Google 官方验证流程：手机扫码后是**接收** Google 发的短信验证码（不是给国际号码发短信）；收不到查短信拦截箱、试语音通话、等 24h 后用同节点同浏览器重试；不要用接码平台/住宅代理规避 |

## 价格 / 订阅类

| 症状 | 原因 | 解决 |
|---|---|---|
| 工具提示"当前金额 US$19.99，不是 0 元，不点确认"，但弹窗明明写着今天免费 | Play 双栏价格排版（今天 ¥0 / 未来 $19.99）被正则误判 | 实测叠加步骤几乎必现的误报；人工读屏确认套餐+今天免费+折算天数后**手动点订阅**，再读订阅页日期验收，不要只看脚本日志 |
| 叠加后日期没 +6 个月 | 升级模式未生效或订阅已取消 | 停下不再叠加；检查订阅是否活跃 |
| 卡上出现 $1 扣款 | Play 的预授权验证 | 数日内自动退回，无需处理 |
| Gemini 高级模型仍带锁 | 订阅权益同步延迟 | 最长 24 小时，不是失败 |

## 显示 / Google App 类

| 症状 | 原因 | 解决 |
|---|---|---|
| Gemini 死循环提示"前往 Play 商店下载 Google" | Google App / GMS 组件被默认停用（`enabled=0`） | `adb shell pm enable com.google.android.googlequicksearchbox`（及 gms/gsf） |
| Google 全家桶显示 Pad 双栏 UI | dp 宽度 ≥600 被判平板 | `adb shell wm density 320`（或更高），保持 1080×1920 |
| 模拟器窗口调完自动恢复 | 未固定窗口 | MuMu 设置中心勾选「固定窗口大小」「记住窗口位置」 |
| 找不到返回/主页/后台划掉手势 | 桌面窗口模式隐藏了导航栏 | 改用「单应用模式」，或在系统设置里切换导航方式 |
