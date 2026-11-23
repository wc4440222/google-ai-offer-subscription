#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把上游 ultra0.py 打上 Android 15 兼容补丁，输出 ultra0_patched.py。

补丁内容：替换 getActivity()，从 Java.choose（libart 符号缺失会失败）
改为 ActivityThread.currentActivityThread().mActivities 遍历取前台 Activity。
"""
import io, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "ultra0.py")
DST = os.path.join(HERE, "ultra0_patched.py")

PATCH = '''function getActivity(){
  var found=null;
  try{
    var at=Java.use("android.app.ActivityThread").currentActivityThread();
    var arr=at.mActivities.value.values().iterator();
    while(arr.hasNext()){
      var rec=arr.next();
      try{
        var f=rec.getClass().getDeclaredField("activity");
        f.setAccessible(true);
        var a=f.get(rec);
        if(a){
          var act=Java.cast(a, Java.use("android.app.Activity"));
          if(!act.isFinishing()){ found=act; break; }
        }
      }catch(e1){}
    }
  }catch(e0){
    try{
      Java.choose("android.app.Activity", {
        onMatch:function(a){ try{ if(!found && !a.isFinishing()) found=a; }catch(e){} },
        onComplete:function(){}
      });
    }catch(e){ S({ev:"choose_err", m:String(e).slice(0,80)}); }
  }
  return found;
}'''

def main():
    if not os.path.exists(SRC):
        print("找不到", SRC); return 1
    c = io.open(SRC, encoding="utf-8").read()
    pat = re.compile(r'function getActivity\(\)\{.*?\n\}', re.S)
    if not pat.search(c):
        print("未找到 getActivity 函数，上游脚本可能已改动，请人工检查"); return 1
    c2 = pat.sub(lambda m: PATCH, c, count=1)
    io.open(DST, "w", encoding="utf-8").write(c2)
    import ast
    ast.parse(io.open(DST, encoding="utf-8").read())
    print("已生成", DST, "（语法检查通过）")
    return 0

if __name__ == "__main__":
    sys.exit(main())
