> 原始迭代笔记，保留原文。对话式表述为当时工作记录，非正式结论；客观摘要见 README.md。

# p28 — 黑屏（SystemUI 崩溃循环）修复

## 症状
进入 ROM 后黑屏，点不动。宿主日志末行是
`Input dispatching timed out (Application does not have a focused window)`。

## 根因（完整链条，逐层有据可查）

1. `SystemUIApplication.startServicesIfNeeded`
   → `ChargingAnimationImpl.init`（`ChargingAnimationImpl.java:318`）
   → `getOplusPreventMode()`
   → `OplusPreventModeExImpl.<init>`（`OplusPreventModeExImpl.kt:500`）
   → `handlePreventMode()`
2. `handlePreventMode()` 调
   `KeyguardSettingUtil.getPreventModeSettingsForUser()`，
   读 `Settings.System["key_is_open_prevent_mode"]`。
3. **关键**：`KeyguardSettingUtil$Companion.smali` 里
   ```
   if-nez p0, :cond_39     # 读到的值是 null
   const/4 p0, 0x1         # ← 当成 true = 开启
   ```
   日志实证：`getPreventModeSettingsForUser key_is_open_prevent_mode value: null`
4. 值为 true → `start()` → `rebuildController()`
   → inflate `oplus_prevent_mode_window_view_content`（第 27 行 TextView）
   → `UnsupportedOperationException: Can't convert value at index 2 to dimension: type=0x1`
   主题被顶成 `Theme.DeviceDefault.Light.DarkActionBar, forced`（oplus 主题属性没套上）
5. SystemUI 每 ~2 秒崩一次 →
   `Process com.android.systemui has crashed too many times, killing!`
6. 没有 SystemUI → 没有窗口持有焦点 →
   `Input dispatching timed out (no focused window)` → **黑屏 + 点不动**

附带发现：p27 还在开机后执行 `wm density 240; wm size 540x960`。
`ConfigurationControllerImpl.addCallback` → `onDensityOrFontScaleChanged`
会**主动**调 `rebuildController()`，等于每次开机都把上面这条崩溃链硬拉起来一次。

## 改动（5 处，全在 app 侧，不动 ROM 镜像，可整体回滚）

| # | 位置 | 动作 |
|---|------|------|
| P1a | `TreeFixer.noScreenSleep()` sqlite 分支 | 显式写 `system/key_is_open_prevent_mode=false` |
| P1b | `TreeFixer.xmlSettings()` | 同上（xml 设置存储分支，Triple 数组 6→7） |
| P2 | `GuestVm.fixDensity()` | 删掉 `wm density 240; wm size 540x960`，只留 `getprop`（去掉崩溃扳机） |
| P3 | `GuestVm.afterBoot()` | 开机自检：重写设置 → 查 SystemUI 存活 → 不在就拉起 → 日志打 `AEMU-SUI-CHECK` |
| P4 | `TreeFixer.fixup()` | 在 `makeDataDirs()` 之后提前调 `noScreenSleep()`。**关键时序**：原来只在开机完成后写，而 SystemUI 在开机动画期间就崩了 |
| P5 | `GuestVm.noPreventMode()`（新增，watchdog 每 tick 调） | 开机动画期间轮询 `settings put ... false`，**读回 `false` 才落 `dev/.aemu-prevent` 停止重试**；覆盖首次开机（那时 `settings.db` / `settings_system.xml` 都还不存在，P1/P4 落空） |

## 产物（本目录）

| 文件 | 说明 |
|------|------|
| `p28-signed.apk` | 已签名，证书 SHA-256 `a572ecc5…731732d4d`（与 p20~p27 同一把），可直接覆盖安装 |
| `classes_p28.dex` | 打好的 classes.dex |
| `p28_patch.py` | 补丁脚本，`SMALI_ROOT=/root/apkx` 下对 `p28smali`（从 `p27smali` 复制）一次跑完 P1~P5 |
| `d1_smali_p28.tar.gz` | 完整 smali 树 |

已验证：从干净的 `p27smali` 树重跑 `p28_patch.py`，产物与交付树 `diff -rq` **完全一致**。

## 安装

```
adb install -r app.aemu.0003-p28.apk
# 或手机上传到 Download 后点安装（覆盖 p27，签名相同不需卸载）
```

## 验证方法

启动该 ROM 实例，看宿主日志：

**应当出现：**
- `prevent-mode: key_is_open_prevent_mode=false confirmed (SystemUI crash chain broken)`
- `... SUI=<pid> AEMU-SUI-CHECK`

**不应再出现：**
- `getPreventModeSettingsForUser key_is_open_prevent_mode value: null`
- `oplus_prevent_mode_window_view: ... Error inflating class`
- `Can't convert value at index 2 to dimension`
- `Process com.android.systemui has crashed too many times, killing!`
- `Input dispatching timed out (Application does not have a focused window)`

**判定标准**：屏幕停在桌面或锁屏，可以点按、可以滑动。

## 若仍黑屏，下一步取证

在宿主共享目录（`AEmulator/<实例名>/`）放一个空文件 `aemu-dump`，
引擎会立刻把 guest 的 `/dev/log` + `/data/anr` 导出到 `Download/aemu-guestlog-*.txt`。
把最新的那份给我，按同一套方法往下查。
