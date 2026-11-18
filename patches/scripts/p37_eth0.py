#!/usr/bin/env python3
"""p37: 给 API34 的 guest 内核补回 eth0（以太网替身），让系统里有网络接口可用。

== 为什么需要（证据链）==
1. AEmulator 从 API30 起把以太网替身整条砍了：
   - Kernel64.kt: API26+ 全部 ethernetStandIn=false（只有 API22/23/27/28/29 为 true）
   - native/guest64/*/run64.c: API27/28/29 有 nl_links/nl_addrs 两张表（eth0 + 10.0.2.15/24），
     API30/31/33/34/35/36/37 全都没有（grep rmnet|wwan|eth0|10.0.2 零命中）
2. 后果：guest 里 getifaddrs() 返回空，系统看不到任何网络接口；
   NetStub 注册的 LinkProperties 写的是 eth0（接口不存在）→ 注册失败 →
   引擎日志 "aemu-net exited, code 0"（boot_completed 后 1 秒退出）。
3. 没有基带时蜂窝数据通路还可能被 Stubs.kt 的 safeMode 降级（60 秒内 telephony 连 >5 次
   → 全部 RIL 网络请求返回 E_RADIO_NOT_AVAILABLE）→ 只剩以太网替身这一条路。

== 本补丁（只改 native/guest64/34/run64.c）==
P1 g_nl[] 增加 route 标志。
P2 NR_socket 的 netlink 分支：NETLINK_ROUTE(protocol 0) 也建 socketpair 并注册，标记 route。
P3 新增 nl_links/nl_addrs（照搬 API29 的实现：lo + eth0 10.0.2.15/24）。
P4 nl_handle_send 的 DUMP 分支：route socket 按 RTM_GETLINK/RTM_GETADDR 回表。

改的是内核替身本身，编译产物 libaemu64_34.so 覆盖 jniLibs/arm64-v8a/。
"""
import io
import os
import re
import sys

RUN64 = os.environ.get("RUN64", "/sdcard/DSH_ai/VM/AEmulator-main/native/guest64/34/run64.c")
src = io.open(RUN64, encoding="utf-8").read()
done = []


def must(cond, msg):
    if not cond:
        print("FATAL:", msg)
        sys.exit(1)


# ---------------- P1: g_nl[] 增加 route 标志 ----------------
a = "static struct { int fd, peer; } g_nl[MAX_NL];"
b = "static struct { int fd, peer, route; } g_nl[MAX_NL];"
must(src.count(a) == 1, "P1 锚点 x%d" % src.count(a))
src = src.replace(a, b)
done.append("P1 g_nl[] +route 标志")

# nl_register 里初始化 route=0
a = """static void nl_register(int fd, int peer) {
    for (int i = 0; i < MAX_NL; i++) {
        if (!g_nl[i].fd) {
            g_nl[i].fd = fd;
            g_nl[i].peer = peer;
            return;
        }
    }
}"""
b = """static void nl_register(int fd, int peer) {
    for (int i = 0; i < MAX_NL; i++) {
        if (!g_nl[i].fd) {
            g_nl[i].fd = fd;
            g_nl[i].peer = peer;
            g_nl[i].route = 0;
            return;
        }
    }
}"""
must(src.count(a) == 1, "P1b 锚点 x%d" % src.count(a))
src = src.replace(a, b)
done.append("P1b nl_register 初始化 route=0")

# ---------------- P3: 新增 nl_attr/nl_put/nl_links/nl_addrs（照搬 API29）----------------
HELPERS = """
// The guest's network as its programs list it (getifaddrs, java.net.NetworkInterface): the loopback and the one
// interface the engine's network stand-in registers, eth0 with 10.0.2.15/24. Without them libc has no interfaces at
// all and the framework registers no network: ConnectivityService sees nothing, and the apps refuse to use it.
static void nl_attr(char *m, u32 *len, u16 type, const void *data, u16 n) {
    u16 *h = (u16 *)(m + *len);
    h[0] = (u16)(4 + n); h[1] = type;
    memcpy(m + *len + 4, data, n);
    u32 end = *len + 4 + n;
    while (end & 3) m[end++] = 0;
    *len = end;
}
static void nl_put(int peer, const struct aemu_nlmsghdr *req, u16 type, char *m, u32 len) {
    struct aemu_nlmsghdr *h = (struct aemu_nlmsghdr *)m;
    h->len = len; h->type = type; h->flags = 2 /*NLM_F_MULTI*/; h->seq = req->seq; h->pid = req->pid;
    S3(NR_write, peer, m, len);
}
static void nl_links(int peer, const struct aemu_nlmsghdr *req) {
    static const struct { const char *name; u16 type; int index; u32 flags, mtu; u8 mac[6], bc[6]; } L[2] = {
        { "lo", 772, 1, 0x10049, 65536, { 0 }, { 0 } },
        { "eth0", 1, 2, 0x11043, 1500, { 0x52, 0x54, 0x00, 0x12, 0x34, 0x56 }, { 0xff, 0xff, 0xff, 0xff, 0xff, 0xff } },
    };
    for (int i = 0; i < 2; i++) {
        char m[160]; u32 len = 16;
        struct { u8 family, pad; u16 type; int index; u32 flags, change; } *ifi = (void *)(m + len);
        ifi->family = 0; ifi->pad = 0; ifi->type = L[i].type; ifi->index = L[i].index; ifi->flags = L[i].flags; ifi->change = 0;
        len += 16;
        nl_attr(m, &len, 3 /*IFLA_IFNAME*/, L[i].name, (u16)(slen(L[i].name) + 1));
        nl_attr(m, &len, 4 /*IFLA_MTU*/, &L[i].mtu, 4);
        nl_attr(m, &len, 1 /*IFLA_ADDRESS*/, L[i].mac, 6);
        nl_attr(m, &len, 2 /*IFLA_BROADCAST*/, L[i].bc, 6);
        nl_put(peer, req, 16 /*RTM_NEWLINK*/, m, len);
    }
}
static void nl_addrs(int peer, const struct aemu_nlmsghdr *req) {
    static const struct { const char *name; int index; u8 prefix, flags, scope; u8 ip[4], bc[4]; } A[2] = {
        { "lo", 1, 8, 0x80, 254, { 127, 0, 0, 1 }, { 0 } },
        { "eth0", 2, 24, 0x80, 0, { 10, 0, 2, 15 }, { 10, 0, 2, 255 } },
    };
    for (int i = 0; i < 2; i++) {
        char m[128]; u32 len = 16;
        struct { u8 family, prefix, flags, scope; u32 index; } *ifa = (void *)(m + len);
        ifa->family = 2; ifa->prefix = A[i].prefix; ifa->flags = A[i].flags; ifa->scope = A[i].scope; ifa->index = (u32)A[i].index;
        len += 8;
        nl_attr(m, &len, 1 /*IFA_ADDRESS*/, A[i].ip, 4);
        nl_attr(m, &len, 2 /*IFA_LOCAL*/, A[i].ip, 4);
        if (A[i].bc[0]) nl_attr(m, &len, 4 /*IFA_BROADCAST*/, A[i].bc, 4);
        nl_attr(m, &len, 3 /*IFA_LABEL*/, A[i].name, (u16)(slen(A[i].name) + 1));
        nl_put(peer, req, 20 /*RTM_NEWADDR*/, m, len);
    }
}
"""

# 插在 nl_handle_send 之前（它要用 nl_links/nl_addrs）
anchor = "// Every request gets the answer that lets its sender go on: a dump ends at once (nothing to list), a request that"
must(src.count(anchor) == 1, "P3 插入锚点 x%d" % src.count(anchor))
src = src.replace(anchor, HELPERS.lstrip("\n") + "\n" + anchor)
done.append("P3 新增 nl_attr/nl_put/nl_links/nl_addrs（lo + eth0 10.0.2.15/24）")

# ---------------- P4: DUMP 分支回表 ----------------
a = """        if ((req->flags & 0x300) == 0x300) {        // NLM_F_DUMP
            m.hdr.len = sizeof m.hdr + 4; m.hdr.type = 3 /*NLMSG_DONE*/; m.hdr.flags = 2 /*NLM_F_MULTI*/;
            m.err.error = 0;
        } else {"""
b = """        if ((req->flags & 0x300) == 0x300) {        // NLM_F_DUMP
            if (route && req->type == 18 /*RTM_GETLINK*/) nl_links(peer, req);
            if (route && req->type == 22 /*RTM_GETADDR*/) nl_addrs(peer, req);
            m.hdr.len = sizeof m.hdr + 4; m.hdr.type = 3 /*NLMSG_DONE*/; m.hdr.flags = 2 /*NLM_F_MULTI*/;
            m.err.error = 0;
        } else {"""
must(src.count(a) == 1, "P4 锚点 x%d" % src.count(a))
src = src.replace(a, b)
done.append("P4 DUMP 分支：route socket 回 RTM_NEWLINK/RTM_NEWADDR")

# nl_handle_send 开头取 route 标志（照搬 API29）
a = """static void nl_handle_send(int fd, const void *buf, u64 len) {
    int peer = nl_find_peer(fd);
    if (!buf || peer < 0) return;"""
b = """static void nl_handle_send(int fd, const void *buf, u64 len) {
    int peer = nl_find_peer(fd);
    int route = 0;
    for (int i = 0; i < MAX_NL; i++) if (g_nl[i].fd == fd) route = g_nl[i].route;
    if (!buf || peer < 0) return;"""
must(src.count(a) == 1, "P4b 锚点 x%d" % src.count(a))
src = src.replace(a, b)
done.append("P4b nl_handle_send 取 route 标志")

# ---------------- P2: NR_socket 的路由分支也建 socketpair 并注册 ----------------
a = """            if (S4(NR_socketpair, 1 /*AF_UNIX*/, 2 /*SOCK_DGRAM*/ | (a[1] & 02004000), 0, (long)sv) == 0) {
                nl_register(sv[0], sv[1]);"""
b = """            if (S4(NR_socketpair, 1 /*AF_UNIX*/, 2 /*SOCK_DGRAM*/ | (a[1] & 02004000), 0, (long)sv) == 0) {
                nl_register(sv[0], sv[1]);
                // a routing socket (NETLINK_ROUTE, protocol 0) is the one the framework lists the interfaces with:
                // the engine answers its two dumps (the links and the addresses) with the stand-in's eth0.
                if (a[2] == 0) for (int i = 0; i < MAX_NL; i++) if (g_nl[i].fd == sv[0]) g_nl[i].route = 1;"""
must(src.count(a) == 1, "P2 锚点 x%d" % src.count(a))
src = src.replace(a, b)
done.append("P2 NR_socket: NETLINK_ROUTE 建 socketpair 并标 route")

io.open(RUN64, "w", encoding="utf-8").write(src)
for d in done:
    print(" *", d)
print("OK")
