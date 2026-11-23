#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读屏辅助：uiautomator dump + pull，提取可见文本（可选坐标）。

用法：
  python read_screen.py [--host 127.0.0.1] [--port 16384] [--with-bounds]
"""
import subprocess, argparse, io, re, os, tempfile

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", default="16384")
    ap.add_argument("--with-bounds", action="store_true")
    a = ap.parse_args()
    serial = f"{a.host}:{a.port}"
    adb = "adb"
    remote = "/data/local/tmp/ui.xml"
    local = os.path.join(tempfile.gettempdir(), "opencode_skill_ui.xml")
    subprocess.run([adb, "-s", serial, "shell", f"uiautomator dump {remote}"], capture_output=True, timeout=30)
    r = subprocess.run([adb, "-s", serial, "pull", remote, local], capture_output=True, timeout=30)
    if r.returncode != 0:
        print("读屏失败：", (r.stdout + r.stderr).decode("utf-8", "replace")[:200]); return 1
    x = io.open(local, encoding="utf-8", errors="replace").read()
    seen = set()
    if a.with_bounds:
        for m in re.finditer(r'text="([^"]+)"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', x):
            t = m.group(1).strip()
            if not t or t in seen: continue
            seen.add(t)
            cx = int(m.group(2)) + int(m.group(4)) // 2
            cy = int(m.group(3)) + int(m.group(5)) // 2
            print(f"({cx},{cy}) {t[:70]}")
    else:
        for m in re.finditer(r'text="([^"]+)"', x):
            t = m.group(1).strip()
            if t and t not in seen:
                seen.add(t); print(t[:80])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
