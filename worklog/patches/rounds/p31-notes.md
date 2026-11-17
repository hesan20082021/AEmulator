> 原始迭代笔记，保留原文。对话式表述为当时工作记录，非正式结论；客观摘要见 README.md。

# p31 — 黑屏第四轮（含前三轮为什么没修好）

## 一、先认账：前三轮各自错在哪

### p28 —— 点启动即闪退（我的 bug）
```
java.lang.VerifyError: Verifier rejected class app.aemu.core.TreeFixer:
  xmlSettings() failed to verify:
  [0x110] register v5 has type String but expected Integer
```
往既有方法 `xmlSettings()` 里插代码，复用了已被赋成 int 的 `v5`。ART 拒收整个类 → 构造 `GuestVm` 就崩。

### p29 —— 不闪退了，但黑屏照旧
`noPreventMode()` 放在 `doBoot()` 里、`fixup` 之后**立刻**调 `guestShell("settings put …")`。
那一刻 **zygote 还没起来**，命令跑不了；异常被我自己的 `catchall` 吞掉，**日志一行没留**。
教训：我连续两轮不给自己留证据。

### p30（未交付）—— 想通了一部分，但方向仍不够
查到两件关键事实：

1. **`fixup()` 在 p27 基线里根本不调 `noScreenSleep()`**，只有 `afterBoot()` 调。
2. **`noScreenSleep()` 开头就判断 `settings.db` 是否存在，不存在直接 `return-void`**。
   首次开机时该文件不存在 → 所有「开机前写设置」的尝试**全部落空**。
3. `Kernel64.kt` 里 API 34（A14）的 `xmlSettings = false`，xml 分支也不走。

所以设置**只能在 `afterBoot`（约开机后 101 秒）才真正写进数据库**。

## 二、p31 做了什么

设置写入时机无法再提前（db 之前不存在），但 **`afterBoot` 写完设置之后，可以把已经崩死的 SystemUI 重新拉起来**。

| 改动 | 内容 |
|---|---|
| P0 | 撤掉 p27 的运行期 `wm density 240; wm size 540x960`（它会触发 `onDensityOrFontScaleChanged` → `rebuildController`，正是崩溃链的扳机） |
| P1 | 新增独立方法 `restartSystemUi()`：写设置 → 读回 → `am force-stop com.android.systemui` → `am start-service`，输出 `AEMU-SUI-RESTART` |
| P2 | `afterBoot()` 末尾只加**一行无参 invoke** |

### 为什么这次结构上不会再 VerifyError

- `TreeFixer.smali` **一个字节没动**（`diff` 已确认）——p28 崩的就是这个类
- 所有新逻辑都在**独立方法**里，寄存器在它自己的栈帧分配（`v0`=String、`v1/v2`=long、`v3`=String）
- 调用点只加 `invoke-direct {v1}`，而 `v1` 在 `afterBoot` 里就是 `this`（实测：插入点前最后一条赋值是 `move-object/from16 v1, p0`，其后被当作 this 读字段 9 次）

**这轮我在找寄存器上连撞三次墙**（`v2` 是 ref 却当 long、`v11` 后段被赋 int、`v12/v13` 多类型），
最后才确认「只有独立方法 + 无参调用」是唯一稳妥形式 —— 这就是 p28 该做的事。

## 三、这一步能解决什么、不能解决什么

**能：** 如果黑屏只是因为 SystemUI 崩死没人接管，重启它就能恢复画面和触摸。

**不能保证：** SystemUI 在开机动画期间就崩了，`afterBoot` 要等到约 101 秒。
如果重启后它**再次**崩（说明设置没真正生效，或崩溃原因不止防误触这一处），
画面会再黑回去。

所以 p31 还带了一个**验证信号**，这次一定会出现在宿主日志里：

```
AEMU-SUI-RESTART
<pidof 输出，空 = 没起来>
```

- 看到 `AEMU-SUI-RESTART` 后面**有 pid** → SystemUI 起来了，看屏幕是否恢复
- **pid 为空** → SystemUI 起不来，说明还有别的崩溃原因，需要看 guest 日志
- 看到 `AEMU-SUI-RESTART failed` → 命令本身没执行成功

不管哪种，**这次都有据可查**，不再是我猜。

## 四、安装

`p31-signed.apk`，签名与 p20~p29 同一把（`a572ecc5…731732d4d`），覆盖安装即可。

## 五、如果还黑屏，请给我这两样

1. 宿主日志里 `AEMU-SUI-RESTART` 那一行（有 pid / 空 / failed）
2. 在 `AEmulator/Realme RMX3888 _ realme UI 5.0 (xvu3fa)/` 里放个空文件 `aemu-dump`，
   引擎会把 guest 日志导到 `Download/aemu-guestlog-*.txt`
   （注意：这个触发要 VM 正在运行时才生效，我这边试的时候 VM 已退出，所以没导出来）

有这两样，我能直接定位到底是「SystemUI 没起来」还是「起来了又崩」，或者「根本没执行到」。
