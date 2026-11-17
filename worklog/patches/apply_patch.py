#!/usr/bin/env python3
"""对 app.aemu.v0003 (classes.dex) 的 smali 打补丁：
P1 韧性：首启 zygote 死亡不再直接 FAILED，走退避重试（重试上限由引擎自带
   的 1 分钟 5 次 / 10 分钟 6 次熔断兜底）。
P2 取证：每次 zygote 死亡先把 guest 侧 /dev/log + getprop 导出到
   /storage/sdcard/aemu-debug/（= 宿主共享文件夹 AEmulator/<实例>/），宿主可直接读。
P3 止血：startService 入口加 36 项精确名单，跳过已证实 SIGABRT/SIGSEGV 的
   vendor HAL，消灭崩溃重启风暴。
"""
import re, sys, io

SM = "/sdcard/DSH_ai/VM/patch/d1/app/aemu/core/GuestVm.smali"
src = io.open(SM, encoding="utf-8").read()
orig_len = len(src)
patched = []

def must(cond, msg):
    if not cond:
        print("FATAL:", msg); sys.exit(1)

# ---------------- P1a: 删除 (!everBooted -> 失败) 的短路跳转 ----------------
a = """    iget-boolean v4, v1, Lapp/aemu/core/GuestVm;->everBooted:Z

    if-eqz v4, :cond_32e

    iget v4, v1, Lapp/aemu/core/GuestVm;->zygoteRestarts:I
"""
b = """    iget-boolean v4, v1, Lapp/aemu/core/GuestVm;->everBooted:Z

    iget v4, v1, Lapp/aemu/core/GuestVm;->zygoteRestarts:I
"""
assert src.count(a) == 1, f"P1a anchor x{src.count(a)}"
src = src.replace(a, b); patched.append("P1a everBooted short-circuit removed")

# ---------------- P1b: 首启也进入重启路径 ----------------
a = """    iget-boolean v4, v1, Lapp/aemu/core/GuestVm;->everBooted:Z

    if-eqz v4, :cond_4bb

    .line 1067
    :cond_3b0
"""
b = """    iget-boolean v4, v1, Lapp/aemu/core/GuestVm;->everBooted:Z

    if-eqz v4, :cond_3b0

    .line 1067
    :cond_3b0
"""
assert src.count(a) == 1, f"P1b anchor x{src.count(a)}"
src = src.replace(a, b); patched.append("P1b first-boot falls into restart path")

# ---------------- P2: zygote 死亡点插入取证导出 ----------------
a = """    :cond_315
    :goto_315
"""
assert src.count(a) == 1, f"P2 anchor x{src.count(a)}"
ins = a + """
    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->dumpGuestLogs()Ljava/lang/String;

    move-result-object v4

    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const-string/jumbo v6, "forensics: guest log -> /storage/sdcard/aemu-debug ("

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    const-string/jumbo v6, ")"

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v1, v5}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V
"""
src = src.replace(a, ins); patched.append("P2 forensics dump at zygote death")

# ---------------- P3: startService 入口 denylist ----------------
a = """    invoke-virtual/range {p1 .. p1}, Lapp/aemu/core/GuestService;->getName()Ljava/lang/String;

    move-result-object v1

    const-string/jumbo v2, "zygote_secondary"
"""
assert src.count(a) == 1, f"P3 anchor x{src.count(a)}"
b = """    invoke-virtual/range {p1 .. p1}, Lapp/aemu/core/GuestService;->getName()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Lapp/aemu/core/GuestVm;->denylisted(Ljava/lang/String;)Z

    move-result v2

    if-eqz v2, :aemu_dl_ok

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string/jumbo v3, "aemu: denylist skip service "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v2}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V

    return-void

    :aemu_dl_ok

    const-string/jumbo v2, "zygote_secondary"
"""
src = src.replace(a, b); patched.append("P3 denylist gate in startService")

# ---------------- 新方法 ----------------
DENY = ["vendor.audio-hal","vendor.boot-qti","camera-provider-2-4","vendor.camera-provider",
"vendor.drm-clearkey-service","vendor.identity","mediacodec","vendor.secure_element",
"vendor.sensors-hal-multihal","vendor.thermal-hal","vendor.usb-hal","vendor.wifi_hal_legacy",
"vendor.cas-default","vendor.qti.hardware.memtrack","vendor.qconfig","qvrd_vndr",
"vendor.capabilityconfigstore","vendor.qti.hardware.display.allocator",
"vendor.qti.hardware.display.color-service","vendor.qti.hardware.display.composer",
"vendor.qti.light","vendor.limits-hal","perf2-hal-1-0","qseecom-service",
"vendor.secureprocessor","vendor.qti.hardware.sensorscalibrate-service",
"vendor.servicetrackeraidl","vendor-qti-media-c2-hal-1-0","wfdhdcphalservice",
"vendor.diagcommd","feature_enabler_client","poweropt-service","vendor.qms",
"vendor.qsap.sensors","vendor.qspa-service","qspmhal"]

m = [".method private final denylisted(Ljava/lang/String;)Z",
     "    .registers 8", "",
     "    const/16 v4, 0x%x" % len(DENY), "",
     "    new-array v0, v4, [Ljava/lang/String;", "",
     "    const/4 v1, 0x0", ""]
for s in DENY:
    esc = s.encode("unicode_escape").decode("ascii").replace('"','\\"')
    jumbo = "jumbo" if len(s) >= 0x20 else ""
    m += ["    const-string/%s v2, \"%s\"" % (jumbo, esc),
          "    aput-object v2, v0, v1",
          "    add-int/lit8 v1, v1, 0x1", ""]
m += ["""    const/4 v1, 0x0

    :aemu_dl_loop
    if-ge v1, v4, :aemu_dl_miss

    aget-object v2, v0, v1

    invoke-virtual {v2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :aemu_dl_next

    const/4 v3, 0x1

    return v3

    :aemu_dl_next
    add-int/lit8 v1, v1, 0x1

    goto :aemu_dl_loop

    :aemu_dl_miss
    const/4 v3, 0x0

    return v3
.end method
"""]
src += "\n".join(m); patched.append("new method: denylisted(String)Z")

m = [""".method private final dumpGuestLogs()Ljava/lang/String;
    .registers 8

    :try_start_0
    const-string/jumbo v0, "mkdir -p /storage/sdcard/aemu-debug; cp -a /dev/log/* /storage/sdcard/aemu-debug/; getprop > /storage/sdcard/aemu-debug/env.txt 2>&1; echo AEMU-DIAG-DONE"

    const-wide/16 v1, 0x7530

    invoke-virtual {p0, v0, v1, v2}, Lapp/aemu/core/GuestVm;->guestShell(Ljava/lang/String;J)Ljava/lang/String;

    move-result-object v0
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    return-object v0

    :catch_0
    move-exception v0

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string/jumbo v2, "forensics dump failed: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v0}, Ljava/lang/Throwable;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {p0, v1}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V

    const/4 v0, 0x0

    return-object v0
.end method
"""]
src += "\n" + "\n".join(m); patched.append("new method: dumpGuestLogs()String")

io.open(SM, "w", encoding="utf-8").write(src)
print("OK len %d -> %d (+%d)" % (orig_len, len(src), len(src)-orig_len))
for p in patched: print("  *", p)
