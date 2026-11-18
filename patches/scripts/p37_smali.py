#!/usr/bin/env python3
"""p37: 给 API34 补回以太网替身 —— smali 侧：让 NetStub 无条件注册 Ethernet service。

== 为什么 ==
API30 起 AEmulator 砍掉了以太网替身（Kernel64: API26+ 全部 ethernetStandIn=false，
native/guest64/3x 的 run64.c 也不再伪造 eth0）。没有基带的机器上：
  蜂窝数据通路随时可能被 Stubs.kt 的 safeMode 降级（60 秒内 telephony 连 >5 次
  → 所有 RIL 网络请求 E_RADIO_NOT_AVAILABLE）
  ⇒ 只剩以太网替身这一条路，而它被关着 ⇒ 系统里一条网络都没有。

本轮（与引擎补丁 p37_eth0.py 配套）：
  P1 afterBoot：netFix 不再被首启的 skipWizardNow 早退吞掉
     —— 首启有 setup wizard 时它会重启系统，整个 afterBoot 被 return 掉了，
        netFix 从没执行过（p36 的取证文件零落盘就是证据）。
        改法：在 skipWizardNow 早退之前先跑 netFix（网络设置与重启无关）。
  P2 aemu-net 的命令列表：无条件加上 "ethernet" 参数
     —— 原本是 if (Kernel64.forApi(api).ethernetStandIn)，API34 为 false，
        于是 NetStub 走 run(false)，不注册 Ethernet service 替身。
        改法：把条件值恒为真（const/4 v7, 0x1），分支结构与标签一概不动。
"""
import io
import os
import sys

GV = os.environ.get("GV", "/tmp/p35s/smali/app/aemu/core/GuestVm.smali")
gv = io.open(GV, encoding="utf-8").read()
done = []


def must(cond, msg):
    if not cond:
        print("FATAL:", msg)
        sys.exit(1)


# ---------------- P2: aemu-net 无条件加 "ethernet" ----------------
a = """    invoke-virtual {v7}, Lapp/aemu/core/Kernel64;->getEthernetStandIn()Z

    move-result v7

    if-eqz v7, :cond_1710

    const-string/jumbo v7, "ethernet"
"""
b = """    invoke-virtual {v7}, Lapp/aemu/core/Kernel64;->getEthernetStandIn()Z

    move-result v7

    const/4 v7, 0x1                     # p37: the stand-in registers the ethernet service on every release

    if-eqz v7, :cond_1710

    const-string/jumbo v7, "ethernet"
"""
must(gv.count(a) == 1, "P2 锚点 x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P2 aemu-net 命令列表：无条件加 ethernet 参数")

# ---------------- P1: afterBoot 里 netFix 挪到 skipWizardNow 早退之前 ----------------
# 现状（p36）：afterBoot 第一句 skipWizardNow() 为 true 时 return，netFix 从没跑过。
# 改法：把 netFix 的 invoke 提到 skipWizardNow 之前；afterBoot 末尾不再重复调用。
a = """    .line 937
    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->skipWizardNow()Z

    move-result v0

    if-eqz v0, :cond_d

    return-void
"""
b = """    .line 937
    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->netFix()V

    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->skipWizardNow()Z

    move-result v0

    if-eqz v0, :cond_d

    return-void
"""
must(gv.count(a) == 1, "P1 锚点 x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P1 afterBoot: netFix 提到 skipWizardNow 早退之前（首启也执行）")

# afterBoot 末尾那次 invoke 去掉（避免跑两遍）
a = """    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->netFix()V

    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->restartSystemUi()V
"""
b = """    invoke-direct {v1}, Lapp/aemu/core/GuestVm;->restartSystemUi()V
"""
must(gv.count(a) == 1, "P1b 锚点 x%d" % gv.count(a))
gv = gv.replace(a, b)
done.append("P1b afterBoot 末尾去掉重复的 netFix 调用")

io.open(GV, "w", encoding="utf-8").write(gv)
for d in done:
    print(" *", d)
print("OK")
