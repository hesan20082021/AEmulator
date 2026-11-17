#!/usr/bin/env python3
"""p28: 修「进 rom 后黑屏 + 点不动」。

== 根因（guest 日志 systemui 崩溃栈，逐层可查）==
  SystemUIApplication.startServicesIfNeeded
   → ChargingAnimationImpl.init              (ChargingAnimationImpl.java:318)
   → getOplusPreventMode() → OplusPreventModeExImpl.<init>   (kt:500)
   → handlePreventMode()
   → KeyguardSettingUtil.getPreventModeSettingsForUser()
        Settings.System["key_is_open_prevent_mode"] == null
   → smali 实证 KeyguardSettingUtil$Companion:
        if-nez p0, :cond_39
        const/4 p0, 0x1          ← 读不到就当成 true（开启）
   → start() → rebuildController()
   → inflate oplus_prevent_mode_window_view_content 第 27 行 TextView
   → UnsupportedOperationException: Can't convert value at index 2 to dimension
       (主题被顶成 Theme.DeviceDefault.Light.DarkActionBar, forced)
   → SystemUI 每 ~2s 崩一次 → "crashed too many times, killing!"
   → 无 SystemUI → 无焦点窗口 → Input dispatching timed out → 黑屏 + 点不动

p27 还额外踩了扳机：开机后执行 `wm density 240; wm size 540x960`，
ConfigurationControllerImpl.addCallback → onDensityOrFontScaleChanged
会主动 rebuildController()，等于每次开机都把这条崩溃链硬拉起来。

== 本补丁（4 处，全在 app 侧，不动 ROM 镜像）==
  P1a TreeFixer.noScreenSleep()  sqlite 分支：system/key_is_open_prevent_mode="false"
  P1b TreeFixer.xmlSettings()    xml  分支：同上（Triple 数组 6→7）
  P2  GuestVm.fixDensity()       删掉 wm density/wm size（去掉崩溃扳机）
  P3  GuestVm.afterBoot()        开机自检：重写设置 → 查 SystemUI → 不在就拉起 → 打 AEMU-SUI-CHECK
  P4  TreeFixer.fixup()          提前调 noScreenSleep()（**关键时序**：原来只在开机完成后写，
                                 而 SystemUI 在开机动画期间就崩了）
"""
import io, os
import sys

ROOT = os.environ.get("SMALI_ROOT", "/root/apkx")
GV = ROOT + "/p28smali/app/aemu/core/GuestVm.smali"
TF = ROOT + "/p28smali/app/aemu/core/TreeFixer.smali"
done = []


def must(cond, msg):
    if not cond:
        print("FATAL:", msg)
        sys.exit(1)


gv = io.open(GV, encoding="utf-8").read()
tf = io.open(TF, encoding="utf-8").read()

# ---------------- P1a: sqlite 分支写入 prevent-mode=false ----------------
a = """    const-string/jumbo v0, "user_setup_complete"

    invoke-static {p0, v5, v7, v0, v3}, Lapp/aemu/core/TreeFixer;->noScreenSleep$lambda$0$0$put(Lapp/aemu/core/TreeFixer;Landroid/database/sqlite/SQLiteDatabase;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 1799
"""
b = """    const-string/jumbo v0, "user_setup_complete"

    invoke-static {p0, v5, v7, v0, v3}, Lapp/aemu/core/TreeFixer;->noScreenSleep$lambda$0$0$put(Lapp/aemu/core/TreeFixer;Landroid/database/sqlite/SQLiteDatabase;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 1799
    const-string/jumbo v0, "key_is_open_prevent_mode"

    const-string v1, "false"

    const-string/jumbo v2, "system"

    invoke-static {p0, v5, v2, v0, v1}, Lapp/aemu/core/TreeFixer;->noScreenSleep$lambda$0$0$put(Lapp/aemu/core/TreeFixer;Landroid/database/sqlite/SQLiteDatabase;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 1799
"""
must(tf.count(a) == 1, "P1a anchor x%d" % tf.count(a))
tf = tf.replace(a, b)
done.append("P1a sqlite: system/key_is_open_prevent_mode=false")

# ---------------- P1b: xmlSettings 分支（Triple 6→7） ----------------
a = """    const/4 v0, 0x6

    .line 1811
    new-array v0, v0, [Lkotlin/Triple;"""
b = """    const/4 v0, 0x7

    .line 1811
    new-array v0, v0, [Lkotlin/Triple;"""
must(tf.count(a) == 1, "P1b size anchor x%d" % tf.count(a))
tf = tf.replace(a, b)

a = """    const-string/jumbo v6, "install_non_market_apps"

    invoke-direct {v2, v7, v6, v8}, Lkotlin/Triple;-><init>(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V

    const/4 v6, 0x5

    aput-object v2, v0, v6
"""
b = """    const-string/jumbo v6, "install_non_market_apps"

    invoke-direct {v2, v7, v6, v8}, Lkotlin/Triple;-><init>(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V

    const/4 v6, 0x5

    aput-object v2, v0, v6

    .line 1817
    new-instance v2, Lkotlin/Triple;

    const-string v4, "false"

    const-string/jumbo v5, "key_is_open_prevent_mode"

    const-string/jumbo v6, "system"

    invoke-direct {v2, v6, v5, v4}, Lkotlin/Triple;-><init>(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V

    const/4 v4, 0x6

    aput-object v2, v0, v4
"""
must(tf.count(a) == 1, "P1b item anchor x%d" % tf.count(a))
tf = tf.replace(a, b)
done.append("P1b xml: system/key_is_open_prevent_mode=false")

# ---------------- P4: fixup 里提前写入（时序关键） ----------------
a = """    .line 121
    invoke-direct {p0}, Lapp/aemu/core/TreeFixer;->makeDataDirs()V
"""
b = """    .line 121
    invoke-direct {p0}, Lapp/aemu/core/TreeFixer;->makeDataDirs()V

    invoke-virtual {p0}, Lapp/aemu/core/TreeFixer;->noScreenSleep()V
"""
must(tf.count(a) == 1, "P4 anchor x%d" % tf.count(a))
tf = tf.replace(a, b)
done.append("P4 fixup: noScreenSleep() before boot (SystemUI crashes during bootanim)")

io.open(TF, "w", encoding="utf-8").write(tf)

# ---------------- P2: 撤掉运行期 wm density/size（崩溃扳机） ----------------
a = """    const-string/jumbo v0, "wm density 240; wm size 540x960; getprop persist.sys.display_density"
"""
b = """    const-string/jumbo v0, "getprop persist.sys.display_density"
"""
must(gv.count(a) == 1, "P2 anchor x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P2 runtime wm density/size removed")

# ---------------- P3: 开机自检 + 补拉 SystemUI ----------------
a = """    invoke-virtual {v0}, Lapp/aemu/core/TreeFixer;->noScreenSleep()V

    .line 951
    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->disableBrokenComponents()V
"""
b = """    invoke-virtual {v0}, Lapp/aemu/core/TreeFixer;->noScreenSleep()V

    :try_start_sui
    const-string/jumbo v0, "settings put system key_is_open_prevent_mode false; settings get system key_is_open_prevent_mode; if [ -z \\"$(pidof com.android.systemui)\\" ]; then am start-service -n com.android.systemui/.SystemUIService; fi; echo \\"SUI=$(pidof com.android.systemui) AEMU-SUI-CHECK\\""

    const-wide/16 v2, 0x7530

    invoke-virtual {v1, v0, v2, v3}, Lapp/aemu/core/GuestVm;->guestShell(Ljava/lang/String;J)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V
    :try_end_sui
    .catchall {:try_start_sui .. :try_end_sui} :catchall_sui

    goto :goto_sui

    :catchall_sui
    move-exception v0

    :goto_sui

    .line 951
    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->disableBrokenComponents()V
"""
must(gv.count(a) == 1, "P3 anchor x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P3 afterBoot: rewrite setting + ensure SystemUI + log AEMU-SUI-CHECK")

io.open(GV, "w", encoding="utf-8").write(gv)


# ---------------- P5: 开机动画期间轮询写 prevent-mode=false（覆盖首启） ----------------
gv = io.open(GV, encoding="utf-8").read()

a = """.method private final autoDump()V
    .locals 8

    invoke-direct {p0}, Lapp/aemu/core/GuestVm;->fixDensity()V
"""
b = """.method private final autoDump()V
    .locals 8

    invoke-direct {p0}, Lapp/aemu/core/GuestVm;->fixDensity()V

    invoke-direct {p0}, Lapp/aemu/core/GuestVm;->noPreventMode()V
"""
must(gv.count(a) == 1, "P5 call anchor x%d" % gv.count(a))
gv = gv.replace(a, b)

must(".method private final noPreventMode()V" not in gv, "P5 already present")
gv += """
.method private final noPreventMode()V
    .locals 6

    iget-object v0, p0, Lapp/aemu/core/GuestVm;->paths:Lapp/aemu/core/VmPaths;

    invoke-virtual {v0}, Lapp/aemu/core/VmPaths;->getRoot()Ljava/io/File;

    move-result-object v0

    new-instance v1, Ljava/io/File;

    const-string/jumbo v2, "dev/.aemu-prevent"

    invoke-direct {v1, v0, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->isFile()Z

    move-result v2

    if-nez v2, :np_go

    return-void

    :np_go
    iget-wide v2, p0, Lapp/aemu/core/GuestVm;->bootAt:J

    const-wide/16 v4, 0x0

    cmp-long v2, v2, v4

    if-gtz v2, :np_done

    :try_start_np
    const-string/jumbo v0, "settings put system key_is_open_prevent_mode false; settings get system key_is_open_prevent_mode"

    const-wide/16 v2, 0x7530

    invoke-virtual {p0, v0, v2, v3}, Lapp/aemu/core/GuestVm;->guestShell(Ljava/lang/String;J)Ljava/lang/String;

    move-result-object v0
    :try_end_np
    .catchall {:try_start_np .. :try_end_np} :catchall_np

    if-nez v0, :np_done

    const-string/jumbo v2, "false"

    invoke-virtual {v0, v2}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v2

    if-nez v2, :np_done

    invoke-virtual {v1}, Ljava/io/File;->createNewFile()Z

    const-string/jumbo v0, "prevent-mode: key_is_open_prevent_mode=false confirmed (SystemUI crash chain broken)"

    invoke-virtual {p0, v0}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V

    goto :np_done

    :catchall_np
    move-exception v0

    :np_done
    return-void
.end method
"""
io.open(GV, "w", encoding="utf-8").write(gv)
done.append("P5 watchdog: poll-write prevent-mode=false until confirmed (covers first boot)")

for d in done:
    print(" *", d)
print("OK")
