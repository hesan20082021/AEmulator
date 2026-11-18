# p35 — 修「ROM 无法联网」+ 现场取证包

## 一、根因（四条实证，不靠猜）

| # | 证据 | 结论 |
|---|---|---|
| 1 | p34 现场日志：amap / heytap 域名**全部解析成功** | IP + DNS 层是通的，不是路由/NAT 断了 |
| 2 | 全项目 grep `captive_portal` / `validation` / `generate_204` / `connectivitycheck` / `gstatic` → **一处都没有** | AEmulator 从来没处理过连通性验证 |
| 3 | `native/guest64/34/run64.c:1067`：`bpf(280)` 是用 `/dev/.aemu-bpf` 空表模拟的 | Android 14 netd 的 eBPF 验证路径不完整，探测拿不到 204 |
| 4 | guest 默认探针 = `clients3.google.com` / `connectivitycheck.gstatic.com`，国内不可达 | NetworkMonitor 判 `VALIDATION_FAILED` |

**结果链**：网络注册成功 → 验证失败 → 系统标记该网络「无 internet」→ Chrome 和各家 App 的网络层整条拒用 → 表现就是「DNS 通但无法联网」。
realme UI 5.0 还叠了自己的 `setting_validate_*` 检测，同样失败。

> 所以这**不是 ROM 精简的责任**，也不是 guest 没网卡 —— socket 本来就透传宿主内核（`NetStub.java` 注释原话），卡在框架的验证判定层。

## 二、修法（不改 ROM 一个字节，走系统自带开关）

在 `afterBoot()` 之后新增独立方法 `netFix()`，通过 `guestShell` 写 `Settings.Global`：

- **治本**：探针换成国内必定 204 的地址
  - `captive_portal_http_url` / `_https_url` / `_fallback_url` → `connectivitycheck.platform.hicloud.com/generate_204`
  - `captive_portal_use_https 0` → 走明文探针，顺带避开 guest 的 TLS 证书链问题
- **保险丝**：`captive_portal_mode 0`（`CAPTIVE_PORTAL_MODE_IGNORE`，彻底关掉门户检测）
- **顺带修**：`dns_servers 223.5.5.5,119.29.29.29`（原代码硬编码 8.8.8.8/1.1.1.1，国内易不可达）
- **厂商开关**：`setting_validate_wifi_enable` / `setting_validate_mobile_enable` 置 false（不存在就 `|| true` 兜住）
- 写完 `cmd connectivity reprobe` / `cmd network_stack reprobe` 触发立即重探

**时机说明**：设置必须写在 `afterBoot` 之后 —— p29 那次写在 zygote 起来之前，`settings` 命令跑不了、异常被 catchall 吞掉，白干一轮。

**为什么不会再 VerifyError**：完全照 p31 验证过的形式 —— 新逻辑在自己的独立方法里（`.registers 8`，寄存器全在自己帧内），调用点只加一行无参 `invoke-direct {v1}`，不碰任何既有寄存器赋值。已用 d8/R8（RC=0 无 error）复核。

## 三、装配与验收

```
基包   patch/p34/p34-signed.apk
补丁   patch/p35_netfix.py          （锚点唯一性 x1 已校验）
产物   patch/p35/p35-signed.apk     70,799,474 字节
```

| 验收项 | 结果 |
|---|---|
| 证书 SHA-256 | `a572ecc5…732d4d`，**与 p34 一致** → 可直接覆盖安装，不用卸载 |
| 签名方案 | v2 + v3 均 true |
| 字节码回读 | `netFix` 定义 + 调用点各 1 处，注入命令串完整 |
| 与 p34 差异 | 只有 4 条：`classes.dex` + 3 条 META-INF（签名必然变化） |

## 四、怎么测（按顺序做）

1. 覆盖安装 p35（同签名，直接装），**启动实例后等开机完成**（`netFix` 在 afterBoot 之后跑，约 1 分钟）。
2. 装好后在 guest 里**开飞行模式再关掉**，强制重连一次，让 NetworkMonitor 用新设置重探。
3. 看状态栏 WiFi/Ethernet 图标：感叹号消失 = 验证过了。
4. 打开浏览器或任一 App 实测。
5. 把宿主日志里 `===NETFIX-DIAG===` 到 `AEMU-NET-FIX-END` 那段贴给我。

## 五、日志判读表（一次定生死）

| 现象 | 结论 | 下一步 |
|---|---|---|
| `ping 223.5.5.5` 通 + `WGET_OK` + `VALIDATED` | 修复成功，纯验证层问题 | 收工 |
| ping 通 + `WGET_OK`，但仍无 `VALIDATED` | 设置没生效（SettingsProvider 写入失败或 realme 覆盖） | 查 `settings get` 回显值 |
| ping 通但 `WGET_FAIL` | **真断在 HTTP 层**，不是验证 | 查 netd/eBPF 转发，走下一轮 |
| `ping 223.5.5.5` 就不通 | IP 层断了（与 p34「DNS 通」矛盾，需重看） | 查路由与 socket 透传 |
| 出现 `AEMU-NET-FIX failed` | `guestShell` 整个抛异常（时机或权限） | 看该时刻 zygote 是否活着 |

## 六、已知保留

- `cmd connectivity reprobe` 在不同 AOSP 版本子命令名可能不同，失败由 `|| true` 兜住，不影响设置写入本身。
- 探针域名走的是华为 hicloud；若该 guest 里 hosts 解析异常，可临时把 `captive_portal_mode 0` 单独当主方案（它已经包含在包里）。
- 本轮**只动 `classes.dex`**，引擎二进制与 ROM 树一个字节没碰，可随时回退到 p34。

## 七、实测结果（p36 补记）

- **网络修复验证成功**：`captive_portal_mode 0` / 探针 URL / 全部写入生效；探针域名解析成功（116.162.127.89）；ping 223.5.5.5 与探针域名全通；`dumpsys` Provider Score 出现 `EVER_VALIDATED & IS_VALIDATED` —— 连通性验证层断点证实并修掉。
- **日志噪音定性**：`toybox: Unknown command wget`（这版 toybox 无 wget，`WGET_FAIL` 是误报）；`Unknown command: reprobe`（子命令不存在，`||true` 兜住）。
- **引入回归**：完整版 ROM 黑屏（精简版正常）—— 原因是 netFix 在 SystemUI 重启的最脆弱窗口连写 9 条 global 设置触发广播风暴，详见 `../p36/README.md`。p36 已修：顺序对调 + 命令瘦身。
- 附带发现：完整版上 `aemu-net exited, code 0`（boot_completed 后 NetStub 退出，疑似注册异常被吞），但真蜂窝栈照样拿到 validated 网络。待 p36 的 `aemu-logcat.txt` 定性。
