# 完整命令流程

所有命令在 `scripts/` 目录执行（或把脚本路径写全）。`<YOUR_GMAIL>` 等占位符自行替换。

## 0. 连接与自检

```
adb connect <ADB_HOST>:<ADB_PORT>
python ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --check
```

全绿项：设备连接、root 提权、frida、计费模块、Play 进程。

## 1. 清场（重要）

工具的 `current_play_account()` 用读屏找 Play 主页的「账号和设置」按钮里的邮箱。若 Play 停在订阅详情页等页面，会读成"未知"导致 `wrong_account` 中止。每次跑之前：

```
adb shell am force-stop com.android.vending
adb shell am force-stop com.google.android.apps.subscriptions.red
```

## 2. 查询 offer（零风险，不消耗资格）

```
# 查 Pro 免费档（12 个月 + 6 个月 ×3）
python ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --list --plan pro12

# 查 Ultra 20TB / 30TB 档
python ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --list --plan 5x --allow-paid
python ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --list --plan 20x --allow-paid

# 精确查某个促销 SKU（返回 offers: [] = 该账号无此优惠）
python ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --list --allow-paid --sku <SKU>
```

报告写入 `ultra0-report/*.json`（含本次运行的 offer 明细；**勿分享该文件**）。

## 3. 下单与叠加（¥0 才确认）

```
# 第 1 步：开通 12 个月免费
python ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --plan pro12

# 第 2 步：叠加 +6 个月（读当前 purchaseToken，CHARGE_FULL_PRICE 升级模式）
python ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --plan pro6 --stack

# 第 3 步：再叠加 +6 个月（用另一个 offer 档）
python ultra0_patched.py --account <YOUR_GMAIL> --no-add --no-switch --plan pro6b --stack
```

成功标志：日志出现「已拉起收银台」「已确认 0 元订阅」。

**人工核对点**：工具的 `confirm_zero` 用正则匹配价格，Play 的双栏价格排版（"今天 ¥0 / 2027年 $19.99"）可能被误判为收费而不点。弹窗出现时必须读屏/截图核对：套餐名正确 + 今天免费 + 有折算天数字样；确认无误后人工点订阅。

## 4. 验收

```
adb shell am start -a android.intent.action.VIEW -d 'https://play.google.com/store/account/subscriptions'
```

读屏找「下次付款金额/日期」。每叠加成功一次，日期应 +6 个月。截图留档（本地保存，勿上传）。

## 5. 参数速查

| 参数 | 含义 |
|---|---|
| `--no-add` | 跳过自动加号，**必须用**，否则弹 Google 登录页 |
| `--no-switch` | 不自动切号，只校验当前 Play 账号匹配 |
| `--list` | 只查询不下单（零风险） |
| `--stack` | 订阅升级叠加（读旧 purchaseToken） |
| `--plan pro12 / pro6 / pro6b / pro6c` | Pro 各免费档 |
| `--plan 5x / 20x` | Ultra 20TB / 30TB 档 |
| `--allow-paid` | 允许付费促销 offer（默认只追 ¥0） |
| `--sku <ID>` | 精确指定商品 ID |

## 6. 收尾

- 每次下单/叠加会触发约 $1 的卡预授权，数日内自动退回，无需操作
- 自动续费默认保留；Google 会在到期前 7 天邮件提醒，到时由用户决定是否取消
