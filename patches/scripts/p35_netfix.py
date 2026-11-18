#!/usr/bin/env python3
"""p35: 修「ROM 无法联网」。

== 证据链 ==
1. guest socket 直接透传宿主内核，p34 现场日志 DNS 全部解析成功 ⇒ IP/DNS 层通。
2. AEmulator 全项目 grep：captive_portal / validation / generate_204 /
   connectivitycheck / gstatic ⇒ 一处都没有 ⇒ 完全没处理连通性验证。
3. guest 的 bpf(280) 是 /dev/.aemu-bpf 空表模拟（run64.c:1067），
   Android 14 netd 的 eBPF 验证路径不完整 ⇒ NetworkMonitor 拿不到 204。
4. 默认探针是 clients3.google.com / gstatic，国内不可达 ⇒
   网络被判 VALIDATION_FAILED ⇒ Chrome 与各家 App 网络层整条拒用
   ＝ 「DNS 通但无法联网」。

== 修法（不改 ROM 一个字节，走系统自带开关）==
Settings.Global:
  captive_portal_http_url / _https_url  → 华为 hicloud 的 generate_204（国内可达）
  captive_portal_mode = 0               → 关闭门户检测（IGNORE，保险丝）
  captive_portal_use_https = 0          → 走明文探针，避开 guest TLS 证书链问题
  dns_servers = 223.5.5.5,119.29.29.29  → 换国内 DNS（8.8.8.8 硬编码是 p34 点名的可疑点）
  setting_validate_* （Oplus 私有）     → 存在就关，不存在 ||true 兜住
时机：afterBoot 之后（zygote 与 SettingsProvider 已就绪，p29 的教训）。

== 不再 VerifyError 的保证 ==
新增独立方法 netFix()，寄存器全在自己帧内；afterBoot 调用点只加一行
无参 invoke-direct {v1}，不碰任何既有寄存器赋值（p31 验证过的形式）。
"""
import io
import os
import sys

GV = os.environ.get("GV", "/tmp/p35s/smali/app/aemu/core/GuestVm.smali")
done = []

gv = io.open(GV, encoding="utf-8").read()

PROBE = "http://connectivitycheck.platform.hicloud.com/generate_204"
PROBE_S = "https://connectivitycheck.platform.hicloud.com/generate_204"

# 只用 guest 必定存在的工具（toybox / ping / dumpsys / settings），不赌 curl
CMD = "; ".join([
    # ---- 治本：探针换国内可达的 204 ----
    "settings put global captive_portal_http_url " + PROBE,
    "settings put global captive_portal_https_url " + PROBE_S,
    "settings put global captive_portal_fallback_url " + PROBE,
    "settings put global captive_portal_use_https 0",
    # ---- 保险：彻底关闭门户检测 ----
    "settings put global captive_portal_mode 0",
    # ---- 顺带：国内 DNS ----
    "settings put global dns_servers 223.5.5.5,119.29.29.29",
    # ---- Oplus/realme 自家验证开关 ----
    "settings put global setting_validate_wifi_enable false || true",
    "settings put global setting_validate_mobile_enable false || true",
    # ---- 让 NetworkStack 立刻重探一次 ----
    "cmd connectivity reprobe || true",
    "cmd network_stack reprobe || true",
    # ================= 取证段（写进宿主日志）=================
    "echo ===NETFIX-DIAG===",
    "settings get global captive_portal_mode",
    "settings get global captive_portal_http_url",
    "settings get global dns_servers",
    "ping -c 2 -W 2 223.5.5.5 2>&1 | tail -3",
    "ping -c 2 -W 2 " + PROBE.replace("http://", "").replace("/generate_204", "") + " 2>&1 | tail -3",
    "toybox wget -q -O /dev/null " + PROBE + " && echo WGET_OK || echo WGET_FAIL",
    "dumpsys connectivity 2>&1 | grep -i -E 'VALIDATED|VALIDATION|captive|AEmuNet' | head -24",
    "echo AEMU-NET-FIX-END",
])

# smali 字符串里唯一需要转义的是双引号与反斜杠；CMD 已保证不含这两者
assert '"' not in CMD and "\\" not in CMD, "CMD 含 smali 需转义字符"

# ---------------- P1: afterBoot 里 restartSystemUi 之后插一行无参 invoke ----------------
a = "    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->restartSystemUi()V\n"
b = a + "\n    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->netFix()V\n"
if gv.count(a) != 1:
    print("FATAL: P1 锚点 x%d（restartSystemUi 调用点必须唯一）" % gv.count(a))
    sys.exit(1)
gv = gv.replace(a, b)
done.append("P1 afterBoot: +1 无参 invoke netFix()")

# ---------------- P2: 追加独立方法 netFix() ----------------
if "netFix" in gv[len(gv) - len(gv) + 0:] and ".method private final netFix()V" in gv:
    print("FATAL: P2 已存在，别重复打")
    sys.exit(1)

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
    ".end method\n"
)

gv += BODY
done.append("P2 新增独立方法 netFix()（自带帧 .registers 8）")

io.open(GV, "w", encoding="utf-8").write(gv)
for d in done:
    print(" *", d)
print("OK 注入命令长度:", len(CMD))
