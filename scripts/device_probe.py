#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""adb 只读探测：设备连接 / root / 屏幕参数 / frida-server / Google 组件启用状态。

用法：
  python device_probe.py [--host 127.0.0.1] [--port 16384]
"""
import subprocess, argparse, sys, os

def sh(adb, serial, cmd, timeout=20):
    r = subprocess.run([adb, "-s", serial, "shell", cmd], capture_output=True, timeout=timeout)
    return (r.stdout + r.stderr).decode("utf-8", "replace").strip()

def find_adb(explicit=None):
    if explicit and __import__("os").path.exists(explicit):
        return explicit
    import shutil
    p = shutil.which("adb")
    if p: return p
    for c in [r"C:\Android\Sdk\platform-tools\adb.exe",
              os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe")]:
        if os.path.exists(c): return c
    return "adb"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", default="16384")
    ap.add_argument("--adb", default=None)
    a = ap.parse_args()
    adb = find_adb(a.adb)
    serial = f"{a.host}:{a.port}"
    subprocess.run([adb, "connect", serial], capture_output=True, timeout=15)
    print("== 设备 ==")
    print(sh(adb, serial, "adb devices >/dev/null 2>&1; getprop ro.product.model; getprop ro.build.version.release"))
    print("== 权限 ==")
    print(sh(adb, serial, "id"))
    print("== 屏幕 ==")
    print(sh(adb, serial, "wm size; wm density"))
    print("== ABI ==")
    print(sh(adb, serial, "getprop ro.product.cpu.abi"))
    print("== frida-server ==")
    print(sh(adb, serial, "ls -l /data/local/tmp/ 2>/dev/null | grep -i frida || echo none"))
    print("== Google 组件（enabled=0 需 pm enable）==")
    for p in ["com.google.android.googlequicksearchbox", "com.google.android.gms", "com.google.android.gsf"]:
        out = sh(adb, serial, f"dumpsys package {p} | grep -m1 enabled=")
        print(p, "->", out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
