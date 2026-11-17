#!/usr/bin/env python3
"""p31: 黑屏第四轮 —— 用「更新设置 + 重启 SystemUI」的可靠路径。

== 三轮下来的事实链（都有实证）==
1. p28 崩溃：VerifyError，TreeFixer.xmlSettings 里 v5 类型冲突
   （Download/aemu-crash-latest.txt 实证）→ 点启动闪退。
2. p29 崩溃修好，但 noPreventMode() 在 doBoot() 里 fixup 后立刻调
   guestShell("settings put ...")：那一刻 zygote 还没起来，命令跑不了，
   异常被 catchall 吞掉 → 日志一行不留 → 黑屏照旧。
3. 查 p27 基线：fixup() 根本不调 noScreenSleep()；只有 afterBoot() 调。
4. 查 noScreenSleep() 实现：settings.db 不存在就直接 return-void。
   => 第一次开机时 db 不存在，我在「开机前」写的所有设置全部落空。
5. 查 Kernel64.kt：API34 的 A14 xmlSettings = false，xml 分支也不走。
   => 设置只有在 afterBoot（约 101 秒后）才真正写进 db。

== 结论 ==
设置写入时机无法再提前（db 之前不存在），而 SystemUI 在开机动画期间
就已经因为「读不到设置 → 默认开启防误触 → inflate 失败」崩掉了。
所以正确做法是：**afterBoot 写完设置后，把已经崩死的 SystemUI 重新拉起。**

== 本轮改动（只有 1 处，最小且可验证）==
P1 afterBoot() 在 noScreenSleep() 之后，用 guestShell 执行：
     am force-stop com.android.systemui
     am start-service -n com.android.systemui/.SystemUIService
   并把输出写进宿主日志（宿主可直接看到，不依赖猜测）。

  注意：此时 zygote 已起来、系统已 boot 完成，guestShell 一定可用。
  上一轮失败正是因为放在了 zygote 起来之前。

== 为什么这次不会再 VerifyError ==
只往 afterBoot() 里插一条 invoke-virtual（无参、不碰任何寄存器赋值）。
afterBoot 里 v1 = this（该方法通篇如此），用它调实例方法类型正确。
"""
import io
import os
import sys

ROOT = os.environ.get("SMALI_ROOT", "/root/apkx")
GV = ROOT + "/p31smali/app/aemu/core/GuestVm.smali"
done = []


def must(cond, msg):
    if not cond:
        print("FATAL:", msg)
        sys.exit(1)


gv = io.open(GV, encoding="utf-8").read()

# ---------------- P0: 撤掉 p27 的运行期 wm density/size ----------------
a = '    const-string/jumbo v0, "wm density 240; wm size 540x960; getprop persist.sys.display_density"\n'
b = '    const-string/jumbo v0, "getprop persist.sys.display_density"\n'
must(gv.count(a) == 1, "P0 anchor x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P0 fixDensity: drop wm density/size (triggers rebuildController -> crash chain)")

# ---------------- P1: afterBoot 里重写设置并重启 SystemUI ----------------
# 方案：新增独立方法 restartSystemUi()，寄存器全在它自己的帧里分配；
# then 在 afterBoot() 末尾只加一行无参 invoke（不碰任何既有寄存器）。
# 这是唯一能保证不触发 VerifyError 的形式 —— 前几次在既有方法里复用寄存器
# 都撞上了「该寄存器在原代码里已被赋成别的类型」。
a = """    invoke-virtual {v2, v3, v0}, Lapp/aemu/core/ImageStore;->save(Landroid/content/Context;Lapp/aemu/core/GuestImage;)V

    return-void
"""
b = """    invoke-virtual {v2, v3, v0}, Lapp/aemu/core/ImageStore;->save(Landroid/content/Context;Lapp/aemu/core/GuestImage;)V

    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->restartSystemUi()V

    return-void
"""
must(gv.count(a) == 1, "P1 anchor x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P1 afterBoot: write setting + force-stop SystemUI + restart it (logged)")

# ---------------- P2: 新增独立方法 restartSystemUi() ----------------
must(".method private final restartSystemUi()V" not in gv, "P2 already present")
gv += """
.method private final restartSystemUi()V
    .locals 6

    :try_start_rs
    const-string/jumbo v0, "settings put system key_is_open_prevent_mode false; settings get system key_is_open_prevent_mode; am force-stop com.android.systemui; sleep 2; am start-service -n com.android.systemui/.SystemUIService; echo AEMU-SUI-RESTART; pidof com.android.systemui"

    const-wide/16 v1, 0x7530

    invoke-virtual {p0, v0, v1, v2}, Lapp/aemu/core/GuestVm;->guestShell(Ljava/lang/String;J)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {p0, v0}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V
    :try_end_rs
    .catchall {:try_start_rs .. :try_end_rs} :catchall_rs

    goto :rs_done

    :catchall_rs
    move-exception v3

    const-string/jumbo v3, "AEMU-SUI-RESTART failed"

    invoke-virtual {p0, v3}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V

    :rs_done
    return-void
.end method
"""
done.append("P2 new method restartSystemUi() (own registers; caller only adds one invoke)")

io.open(GV, "w", encoding="utf-8").write(gv)

for d in done:
    print(" *", d)
print("OK")
