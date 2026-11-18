# p36 — 修 p35 在完整版 ROM 上的黑屏回归

> 状态：已构建待测。网络修复沿用 p35（已验证生效），本轮只动「执行顺序 + 命令内容」。
> 产物：`AEmulator-p36-netfix.apk`（sha256 前 20 位 `d2303a5389c56e4a65cc`）

## 一、现象（用户实测）

| 组合 | 结果 |
|---|---|
| p34 + 完整版 ROM | 正常启动显示 ✅ |
| p35 + 完整版 ROM（g8u78x） | 开机完成（105s）后**黑屏** ❌ |
| p35 + 精简版 ROM | 正常启动显示 ✅ |

p35 相对 p34 的**唯一 delta 是 `afterBoot()` 尾部新增的 `netFix()`**，这是干净的 A/B —— 回归责任就在它。

## 二、为什么 p34 可以、p35 不可以（差分推理）

**p34 的 afterBoot 结尾**：

```
…ImageStore.save → restartSystemUi() → return
```

SystemUI 重启是**最后一个动作**，起来之后系统一片安静 → 完整版验证过稳定。

**p35 的 afterBoot 结尾**：

```
…restartSystemUi() → netFix() → return
```

SystemUI 刚被 force-stop、正在重启的最脆弱窗口里，netFix **连写 9 条 global 设置**。

**现场证据（用户日志，逐条可查）**：

1. `18:03:12 Starting service: Intent { cmp=com.android.systemui/.SystemUIService }` —— SystemUI 刚拉起；
2. `18:03:14 dns: gethostbyname 0 connectivitycheck.platform.hicloud.com` —— **写入后 2 秒**，NetworkMonitor 已经拿新探针 URL 重估网络。证明每条 `settings put global` 都立刻触发 ConnectivityService 重估 + 广播，9 条连写 = 广播风暴；
3. `dumpsys connectivity` 显示完整版网络栈远 rich 于精简版：真蜂窝 Provider（Id 2 CELLULAR，含 IMS/MMS 等）、多个 WIFI offer（Id 4–8，含 OEM_PAID）—— 每条写入的 churn 在完整版上大好几倍；
4. OplusSystemUI 带一堆网络状态监听器，刚重启就被风暴糊脸 → 崩/卡 → 黑屏；精简版 SystemUI 轻，扛过去了。

**两个放大器（既有问题，非本轮回归根因，但加重 churn）**：

- `dumpsys connectivity | grep` 里 grep 触发引擎 fdsan bug（`double-close of fd 0` → SIGABRT），本轮日志出现 3 次，每次都拉 tombstoned 写 tombstone。此 bug p34 亦有（`===NET===` 段同样崩），非回归原因。
- `cmd connectivity reprobe` / `cmd network_stack reprobe` 本版不存在（`Unknown command` / `No shell command implementation`），纯噪音。

## 三、p36 改动（最小且可验证）

| # | 改动 | 理由 |
|---|---|---|
| P1 | `afterBoot()` 尾部顺序对调：**netFix() 先跑，restartSystemUi() 恢复为最后一个动作** | 设置在系统稳定期写完（系统还没 force-stop SystemUI），SystemUI 起来时网络已 settled —— 精确恢复 p34 的已验证终态 |
| P2 | netFix 命令瘦身 | 去掉 `cmd reprobe`（不存在）、`toybox wget`（没有）、`dumpsys\|grep`（grep 会崩）、`dns_servers`/`fallback_url`（mode=0 下无效，白增 churn） |

**保留的已验证网络修复**（p35 实测成功，一条不动）：

- `captive_portal_mode 0`（回显确认写入成功）
- `captive_portal_http_url/_https_url` → `connectivitycheck.platform.hicloud.com/generate_204`（解析成功 116.162.127.89）
- `captive_portal_use_https 0`
- `setting_validate_wifi_enable/mobile_enable false`（Oplus 层）

**新增取证落盘**（经 `/storage/sdcard/`，宿主实例目录直接可读，不经过会崩的 grep）：

- `aemu-logcat.txt`（logcat -d -t 2000）→ **下一轮若仍黑屏，SystemUI 崩溃栈直接在里面**
- `aemu-net-dump.txt`（dumpsys connectivity 全文）
- `aemu-window.txt`（dumpsys window，窗口/焦点状态）

**为什么不会再 VerifyError**：netFix 方法整体重写仍是独立帧（`.registers 8`）；调用点只交换两行 invoke 的先后，不新增、不删减、不碰任何寄存器赋值。d8/R8 复核 RC=0。

## 四、p35 网络修复的验证结论（本轮日志实证，继续有效）

- `===NETFIX-DIAG===` 回显 `captive_portal_mode 0`、探针 URL、DNS 全部写入成功；
- 探针域名解析成功（116.162.127.89），ping 223.5.5.5 / 探针域名全通；
- `dumpsys` 的 Provider Score 出现 **`EVER_VALIDATED & IS_VALIDATED`** —— 网络已被系统判为已验证；
- 日志噪音定性：`toybox: Unknown command wget`（这版 toybox 无 wget，`WGET_FAIL` 是误报）；`Unknown command: reprobe`（子命令不存在，`||true` 兜住）。
- 附带发现：`18:03:07 · aemu-net exited, code 0` —— 完整版上 NetStub 在 boot_completed 后退出（疑似注册失败被 catch 吞掉），但完整版靠真蜂窝栈（RIL 替身 10.0.2.15）照样拿到 validated 网络；精简版无蜂窝则依赖 aemu-net。**此项待下一轮从 aemu-logcat.txt 里拿 NetStub 的异常栈定性。**

## 五、测试步骤

1. 覆盖安装 p36（证书与 p34/p35 一致，直接装）；
2. **完整版 ROM** 启动，等开机完成（约 105s）+ 1 分钟（netFix 在 afterBoot 内跑完）；
3. 看是否还黑屏；网络连通性照 p35 方法验证（状态栏感叹号 + 浏览器）；
4. 回传宿主实例目录里三个文件：`aemu-logcat.txt` / `aemu-net-dump.txt` / `aemu-window.txt`，以及宿主日志里 `===NETFIX-DIAG===` 到 `AEMU-NET-FIX-END` 段。

## 六、判读表

| 现象 | 结论 |
|---|---|
| 完整版不再黑屏 + 网络可用 | 回归修复成功，收工 |
| 仍黑屏，但 `aemu-logcat.txt` 里有 SystemUI FATAL | 按 crash 栈定位，开 p37 |
| 仍黑屏，logcat 无 FATAL | 查 WindowManager/SurfaceFlinger 状态（`aemu-window.txt`） |
| 网络又不行了 | 检查 `aemu-net-dump.txt` 里 IS_VALIDATED 是否还在；顺带看 aemu-net 是否退出 |
