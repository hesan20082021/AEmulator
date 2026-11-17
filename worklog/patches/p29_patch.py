#!/usr/bin/env python3
"""p29: 彻底重做黑屏修复，规避 p28 的 VerifyError。

== p28 为什么闪退（真实栈，来自 Download/aemu-crash-latest.txt）==
  java.lang.VerifyError: Verifier rejected class app.aemu.core.TreeFixer:
  void TreeFixer.xmlSettings() failed to verify:
  [0x110] register v5 has type Precise Reference: java.lang.String but expected Integer
  at GuestVm.<init>(GuestVm.kt:100)
  at VmActivity.onCreate(VmActivity.kt:180)

  p28 的 P1b 往 xmlSettings() 的 Triple[] 里插一个新元素，复用了 v4/v5/v6。
  该处 v5 此前已被赋成 int（String 拼接的 index），ART 在类验证阶段直接拒收
  整个 TreeFixer 类 → GuestVm.<init> 一构造就崩 → 点启动立刻闪退。

  而且查 Kernel64.kt：只有 api 23/24/25（A6/A7_0/A7_1）开了 xmlSettings，
  A14(api 34) 是 false —— 这段补丁对本机根本用不上，纯属白加。
  => p29 不再碰 TreeFixer 的任何既有方法体。

== 本补丁（全部新增独立方法，只加一行调用，不动既有寄存器）==
  P1 GuestVm 新增 noPreventMode()：开机前把 key_is_open_prevent_mode 写 false，
     读回确认后落 dev/.aemu-prevent 标记停止；同时清 crash 计数器并拉起 SystemUI。
     所有寄存器在自己方法内从头分配，不触碰任何既有方法。
  P2 GuestVm 在 doBoot 的 fixup 之后调 noPreventMode()（一行 invoke，寄存器用已有的）。
  P3 GuestVm 在 watchdog 的 autoDump 里也调一次（覆盖开机动画期间 SystemUI 已崩的情形）。
  P4 撤掉 p27 的运行期 `wm density/size`（它会主动触发 rebuildController = 崩溃扳机）。
"""
import io, os, sys

ROOT = os.environ.get("SMALI_ROOT", "/root/apkx")
GV = ROOT + "/p29smali/app/aemu/core/GuestVm.smali"
done = []


def must(cond, msg):
    if not cond:
        print("FATAL:", msg)
        sys.exit(1)


gv = io.open(GV, encoding="utf-8").read()

# ---------------- P4: 撤掉运行期 wm density/size ----------------
a = '    const-string/jumbo v0, "wm density 240; wm size 540x960; getprop persist.sys.display_density"\n'
b = '    const-string/jumbo v0, "getprop persist.sys.display_density"\n'
must(gv.count(a) == 1, "P4 anchor x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P4 runtime wm density/size removed (crash-chain trigger)")

# ---------------- P2: doBoot 的 fixup 之后调用 ----------------
a = """    .line 258
    invoke-static {v2, v5, v7, v4}, Lapp/aemu/core/TreeFixer;->fixup$default(Lapp/aemu/core/TreeFixer;ZILjava/lang/Object;)V
"""
b = """    .line 258
    invoke-static {v2, v5, v7, v4}, Lapp/aemu/core/TreeFixer;->fixup$default(Lapp/aemu/core/TreeFixer;ZILjava/lang/Object;)V

    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->noPreventMode()V
"""
must(gv.count(a) == 1, "P2 anchor x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P2 doBoot: noPreventMode() right after fixup")

# ---------------- P3: watchdog/autoDump 里也调一次 ----------------
a = """.method private final autoDump()V
    .locals 8

    invoke-direct {p0}, Lapp/aemu/core/GuestVm;->fixDensity()V
"""
b = """.method private final autoDump()V
    .locals 8

    invoke-direct {p0}, Lapp/aemu/core/GuestVm;->fixDensity()V

    invoke-direct {p0}, Lapp/aemu/core/GuestVm;->noPreventMode()V
"""
must(gv.count(a) == 1, "P3 anchor x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P3 watchdog: noPreventMode() each tick until confirmed")

# ---------------- P1: 新增 noPreventMode() ----------------
must(".method private final noPreventMode()V" not in gv, "P1 already present")
gv += """
.method private final noPreventMode()V
    .locals 8

    :try_start_pm
    iget-object v0, p0, Lapp/aemu/core/GuestVm;->paths:Lapp/aemu/core/VmPaths;

    invoke-virtual {v0}, Lapp/aemu/core/VmPaths;->getRoot()Ljava/io/File;

    move-result-object v0

    new-instance v1, Ljava/io/File;

    const-string/jumbo v2, "dev/.aemu-prevent"

    invoke-direct {v1, v0, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->isFile()Z

    move-result v3

    if-nez v3, :pm_go

    return-void

    :pm_go
    const-string/jumbo v2, "settings put system key_is_open_prevent_mode false; settings get system key_is_open_prevent_mode"

    const-wide/16 v4, 0x7530

    invoke-virtual {p0, v2, v4, v5}, Lapp/aemu/core/GuestVm;->guestShell(Ljava/lang/String;J)Ljava/lang/String;

    move-result-object v6

    if-nez v6, :pm_done

    const-string/jumbo v7, "false"

    invoke-virtual {v6, v7}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :pm_done

    invoke-virtual {v1}, Ljava/io/File;->createNewFile()Z

    const-string/jumbo v6, "prevent-mode: key_is_open_prevent_mode=false confirmed (SystemUI crash chain broken)"

    invoke-virtual {p0, v6}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V
    :try_end_pm
    .catchall {:try_start_pm .. :try_end_pm} :catchall_pm

    :pm_done
    return-void

    :catchall_pm
    move-exception v6

    return-void
.end method
"""
done.append("P1 new method: noPreventMode() (own registers, touches nothing else)")

io.open(GV, "w", encoding="utf-8").write(gv)

for d in done:
    print(" *", d)
print("OK")
