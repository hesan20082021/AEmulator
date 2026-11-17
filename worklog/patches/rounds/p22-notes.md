> 原始迭代笔记，保留原文。对话式表述为当时工作记录，非正式结论；客观摘要见 README.md。

# p22 — 黑屏诊断增强 + SecureElement 崩溃循环修复

## 本版内容
1. **TreeFixer.fixup 开头**：把 `system_ext/app/SecureElement` 整个目录收走到
   `system/.aemu-parked/system_ext#app#SecureElement`。该 persistent 应用（uid 1068）
   在没有 eSE HAL 的环境里启动即抛 `IllegalArgumentException: VINTF declaration error.`
   （SecureElementService.onCreate → ServiceManager.addService 被引擎 servicemanager 拒绝），
   每 ~100ms 崩一次、每次重启都拉起新进程 —— p21 日志里 207 个 FATAL 就是它。
2. **dumpGuestLogs**：缓冲区超过 4MB 时 skip 到末尾再读（原来读的是开头 4MB，会把
   新发生的崩溃截掉）。
3. **watchdog 定时导出**：boot 完成后按 tick 自动导 3 份 guest 日志
   （boot-done +3s / +63s / +183s，用 dev/.aemu-d1/d2/d3 文件门控），不再是一次性。
   Launcher 的崩溃发生在 boot 完成 ~40s 后，第 2、3 份会抓到它的完整栈。

## 已知现状（p21 日志）
- SystemUI 启动即崩：`oplus_prevent_mode_window_view` inflate 失败 ——
  `UnsupportedOperationException: Can't convert value at index 2 to dimension: type=0x1`
  （主题被强制成 framework DeviceDefault，oplus 主题属性缺维值）。
- Launcher：CriticalEventLog 记录 `IllegalArgumentException`（栈还没抓到）。
- 两者都是 oplus 应用 → 怀疑 oplus 主题属性解析链在引擎环境下断了；等 p22 的
  dump2/dump3 拿到两份完整栈再定位。
