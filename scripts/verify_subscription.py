#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验收：拉起 Play 订阅页，读屏找「下次付款金额/日期」，截图留档。

用法：
  python verify_subscription.py [--host 127.0.0.1] [--port 16384] [--shot DIR]
"""
import subprocess, argparse, io, re, os, tempfile, time

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", default="16384")
    ap.add_argument("--shot", default=None, help="截图保存目录（默认系统临时目录）")
    a = ap.parse_args()
    serial = f"{a.host}:{a.port}"
    adb = "adb"
    subprocess.run([adb, "-s", serial, "shell",
        "am start -a android.intent.action.VIEW -d 'https://play.google.com/store/account/subscriptions'"],
        capture_output=True, timeout=30)
    time.sleep(12)
    remote = "/data/local/tmp/ui.xml"
    local = os.path.join(tempfile.gettempdir(), "opencode_skill_sub_ui.xml")
    found = False
    for _ in range(3):
        subprocess.run([adb, "-s", serial, "shell", f"uiautomator dump {remote}"], capture_output=True, timeout=30)
        subprocess.run([adb, "-s", serial, "pull", remote, local], capture_output=True, timeout=30)
        x = io.open(local, encoding="utf-8", errors="replace").read()
        lines = []
        for m in re.finditer(r'text="([^"]+)"', x):
            t = m.group(1).strip()
            if t and any(k in t for k in ["付款", "Google One", "AI Pro", "AI Ultra", "202", "取消"]):
                if t not in lines: lines.append(t[:100])
        if lines:
            print("== 订阅关键信息 ==")
            for l in lines: print(l)
            found = True
            break
        time.sleep(4)
    if not found:
        print("未读到订阅信息，请人工查看模拟器屏幕")
    if a.shot:
        os.makedirs(a.shot, exist_ok=True)
        pic = os.path.join(a.shot, "subscription.png")
        subprocess.run([adb, "-s", serial, "shell", "screencap -p /data/local/tmp/sub.png"], capture_output=True, timeout=30)
        subprocess.run([adb, "-s", serial, "pull", "/data/local/tmp/sub.png", pic], capture_output=True, timeout=30)
        print("截图：", pic)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
