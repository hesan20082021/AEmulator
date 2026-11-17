# 工程进度记录：Android 14 客户机适配（Realme RMX3888 / realme UI 5.0）

本目录记录以官方 `uxazu/AEmulator` 为基地，对 Android 14（API 34）客户机做适配时
产生的改动、验证记录与构建产物。内容按事实陈述组织，不含推测性结论。

## 基地

- 上游：`https://github.com/uxazu/AEmulator.git`，`main` @ `3b97ed5`（版本 0.0.0.3）。
- 本仓库 fork 自上游；`main` 分支与上游保持一致。
- 适配改动位于 `oplus-systemui-fix` 分支；本分支（`progress-archive`）在官方
  源码基础上汇总全部工程进度。

## 环境

| 项 | 值 |
|---|---|
| 宿主设备 | Realme RMX3888，realme UI 5.0 |
| 宿主系统 | Android 14，arm64 |
| 客户机 | Android 14（API 34），引擎 `libaemu64_34.so` |
| 客户机镜像 | `RMX3888_14.0.0.228(CN01)_slim.zip`（官方包精简版，7,040,835,911 字节） |
| 构建要求 | Gradle 8.14.2，JDK 17，compileSdk 36，minSdk 26，targetSdk 28，abiFilters arm64-v8a |

## 改动清单

### 1. 源码改动（`oplus-systemui-fix`，`GuestVm.kt`，+24 行）

新增 `oplusSystemUi()`，由 `afterBoot()` 调用：

- 检测条件：客户机 `my_product/build.prop`、`system/build.prop`、`vendor/build.prop`
  中任一包含 `ro.build.version.oplusrom` 或 `ro.oplus.`。
- 命中后执行：
  ```
  settings put system key_is_open_prevent_mode false
  am force-stop com.android.systemui
  am start-service -n com.android.systemui/.SystemUIService
  ```
- 未命中时不做任何操作。
- 设置写入放在 `afterBoot()`，原因是客户机 `settings.db` 在更早的启动阶段尚不存在。

对应补丁脚本：`patches/p31_patch.py`；基线到最终状态的差异：`patches/p27-to-p34-GuestVm.diff`。

### 2. 客户机镜像侧改动

早期方案直接改写反编译后的 `classes.dex`（smali 层），历经 p20–p34 多轮迭代。
最终有效的改动与源码改动等价（写 prevent-mode 键 + 重启 SystemUI），另外两处早期改动为：

- 移除两处 `const/16 v3, 0xf0` 密度硬编码，恢复 `getDensity()` 动态取值。
- 客户机分辨率由 540×960 调整为 720×1600（与宿主面板比例一致）。

`GuestVm.smali` 是唯一需要修改的 smali 文件；`TreeFixer.smali`、`InputService.smali`
与基线 p27 完全一致。基线树与最终树保存在本地 `/root/apkx/p27smali`、`/root/apkx/p34smali`。

## 验证记录

以下为日志中出现的原始标记，用于确认改动是否执行：

| 标记 | 含义 |
|---|---|
| `AEMU-SUI-RESTART` | SystemUI 重启命令已执行 |
| `false` | `settings get system key_is_open_prevent_mode` 读回值 |
| `Starting service: Intent { cmp=com.android.systemui/.SystemUIService }` | SystemUI 服务启动 |
| `framebuffer: 720x1600` / `Physical size: 720x1600` | 分辨率与密度配置生效 |

早期黑屏期间日志出现：
`UnsupportedOperationException: Can't convert value at index 2 to dimension: type=0x1`
以及 `has crashed too many times, killing!`，随后出现
`Input dispatching timed out (Application does not have a focused window)`。

## 未决问题

| 问题 | 当前状态 | 已有证据 |
|---|---|---|
| 外部 APK 导入 | 未定性 | `pm install` 路径见 `GuestVm.kt`；需客户机 `pm list packages` 结果 |
| 联网 | 未定性 | DNS 解析日志正常；`GuestVm.kt` 中 `net.dns1=8.8.8.8`、`net.dns2=1.1.1.1` 为硬编码 |
| 导航键 | 现有规避方式 | 关闭应用内按键栏后使用客户机原生导航栏 |

## 目录说明

```
patches/       补丁脚本、基线到最终的 diff
diagnostics/   ROM 精简与依赖核对的原始报告
releases/      验证过的构建产物（签名 APK、classes.dex）
README.md      本文件
```

## 重新构建

```bash
# 1. 获取源码（官方为基地）
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
git checkout oplus-systemui-fix      # 含源码改动的分支

# 2. 编译（需 JDK 17 + Android SDK，compileSdk 36）
./gradlew assembleRelease

# 或直接取已验证产物：releases/p34-signed.apk
```

如需复现 smali 层改动：
```bash
baksmali d base.apk -o work/ -j 8
python3 worklog/patches/p31_patch.py     # 幂等，锚点缺失则非零退出
smali assemble -a 34 -j 8 -o classes.dex work/
python3 worklog/patches/repack.py
zipalign -p -f 4 unsigned.apk aligned.apk
apksigner sign --ks <keystore> --out signed.apk aligned.apk
```
