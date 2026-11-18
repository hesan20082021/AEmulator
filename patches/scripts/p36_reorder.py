#!/usr/bin/env python3
"""p36: 修 p35 在完整版 ROM 上的黑屏回归 —— 调整 afterBoot 尾部执行顺序 + 净化命令。

== 为什么 p34 可以、p35 不可以（差分推理）==
p34 afterBoot 结尾：…ImageStore.save → restartSystemUi() → return
  ⇒ SystemUI 重启是最后一个动作，起来后系统安静 ⇒ 完整版验证过稳定。
p35 afterBoot 结尾：…restartSystemUi() → netFix() → return
  ⇒ SystemUI 刚 force-stop 重启的最脆弱窗口里，netFix 连写 9 条 global 设置。
  现场证据：18:03:12 am start-service SystemUIService；
           18:03:14 引擎日志出现新探针域名的 DNS 解析
           ⇒ 写入后 2 秒 NetworkMonitor 已重估网络 = 每条写入都触发重估+广播。
  完整版网络栈 rich（真蜂窝 Provider + 多 WIFI offer + OEM_PAID，见 dumpsys），
  OplusSystemUI 网络监听器多，广播风暴糊脸 → 崩/卡 → 黑屏；精简版 SystemUI 轻，扛住。

== p36 改动（最小且可验证）==
P1 afterBoot 尾部顺序对调：netFix() 先跑（系统稳定期写设置），
   restartSystemUi() 恢复为最后一个动作（p34 已验证终态）。
P2 netFix 命令瘦身：
   - 去掉 cmd connectivity/network_stack reprobe（本版不存在，纯噪音）
   - 去掉 toybox wget（这版 toybox 没有，WGET_FAIL 是误报）
   - 去掉 dumpsys|grep（grep 触发引擎 fdsan bug SIGABRT）
   - 去掉 dns_servers / captive_portal_fallback_url（mode=0 下无效，白增churn）
   - 保留已验证生效的全部网络修复（captive_portal_mode 0 + hicloud 探针 + use_https 0 + Oplus 开关）
   - 新增取证落盘：logcat / dumpsys connectivity / dumpsys window → 共享 sdcard 文件，
     下一轮若仍黑屏，SystemUI 崩溃栈直接在文件里，零猜测。
== 不再 VerifyError ==
netFix 方法整体重写，仍是独立帧（.registers 8）；调用点只交换两行 invoke 的先后，
不新增、不删减、不碰任何寄存器赋值。
"""
import io
import os
import sys

GV = os.environ.get("GV", "/tmp/p35s/smali/app/aemu/core/GuestVm.smali")
gv = io.open(GV, encoding="utf-8").read()
done = []

# ---------------- P1: 对调 afterBoot 尾部两行 invoke 的顺序 ----------------
a = ("    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->restartSystemUi()V\n"
     "\n"
     "    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->netFix()V\n")
b = ("    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->netFix()V\n"
     "\n"
     "    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->restartSystemUi()V\n")
if gv.count(a) != 1:
    print("FATAL: P1 锚点 x%d（p35 的两行 invoke 必须恰好存在一处）" % gv.count(a))
    sys.exit(1)
gv = gv.replace(a, b)
done.append("P1 afterBoot: netFix 先于 restartSystemUi（SystemUI 恢复为最后动作）")

# ---------------- P2: 重写 netFix 方法体（瘦身 + 取证落盘）----------------
start = gv.find(".method private final netFix()V")
if start < 0:
    print("FATAL: netFix 方法不存在")
    sys.exit(1)
end = gv.find(".end method", start)
if end < 0:
    print("FATAL: netFix 方法没有 .end method")
    sys.exit(1)
end += len(".end method")

PROBE = "http://connectivitycheck.platform.hicloud.com/generate_204"
PROBE_S = "https://connectivitycheck.platform.hicloud.com/generate_204"

CMD = "; ".join([
    # ---- 已验证生效的网络修复（原样保留）----
    "settings put global captive_portal_mode 0",
    "settings put global captive_portal_use_https 0",
    "settings put global captive_portal_http_url " + PROBE,
    "settings put global captive_portal_https_url " + PROBE_S,
    "settings put global setting_validate_wifi_enable false || true",
    "settings put global setting_validate_mobile_enable false || true",
    # ---- 取证段（写共享 sdcard，宿主直接可读；不经过会崩的 grep）----
    "echo ===NETFIX-DIAG===",
    "settings get global captive_portal_mode",
    "settings get global captive_portal_http_url",
    "ping -c 1 -W 2 223.5.5.5 2>&1 | tail -2",
    "pidof com.android.systemui",
    "getprop init.svc.zygote",
    "dumpsys connectivity > /storage/sdcard/aemu-net-dump.txt 2>&1",
    "dumpsys window > /storage/sdcard/aemu-window.txt 2>&1",
    "logcat -d -t 2000 > /storage/sdcard/aemu-logcat.txt 2>&1",
    "echo AEMU-NET-FIX-END",
])

assert '"' not in CMD and "\\" not in CMD, "CMD 含 smali 需转义字符"

BODY = (
    "\n.method private final netFix()V\n"
    "    .registers 8\n"
    "\n"
    "    :try_start_nf\n"
    '    const-string/jumbo v0, "' + CMD + '"\n'
    "\n"
    "    const-wide/32 v1, 0x186a0        # 100 秒超时\n"
    "\n"
    "    invoke-virtual {p0, v0, v1, v2}, Lapp/aemu/core/GuestVm;->guestShell(Ljava/lang/String;J)Ljava/lang/String;\n"
    "\n"
    "    move-result-object v0\n"
    "\n"
    "    invoke-virtual {p0, v0}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V\n"
    "    :try_end_nf\n"
    "    .catchall {:try_start_nf .. :try_end_nf} :catchall_nf\n"
    "\n"
    "    goto :nf_done\n"
    "\n"
    "    :catchall_nf\n"
    "    move-exception v3\n"
    "\n"
    '    const-string/jumbo v3, "AEMU-NET-FIX failed"\n'
    "\n"
    "    invoke-virtual {p0, v3}, Lapp/aemu/core/GuestVm;->log(Ljava/lang/String;)V\n"
    "\n"
    "    :nf_done\n"
    "    return-void\n"
    ".end method"
)

gv = gv[:start] + BODY + gv[end:]
done.append("P2 netFix 重写：瘦身 + logcat/dumpsys/window 落盘共享 sdcard")

io.open(GV, "w", encoding="utf-8").write(gv)
for d in done:
    print(" *", d)
print("OK 命令长度:", len(CMD))
