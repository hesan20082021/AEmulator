# 工程记录：Android 14 客机适配（realme RMX3888 / realme UI 5.0）

本目录记录以 AEmulator 0.0.0.3 为基础，对 Android 14（API 34）客户机做适配的过程。
改动针对 Oplus / realme UI 客机的启动与显示问题。

## 基地与分支

- 上游：`https://github.com/uxazu/AEmulator.git`，0.0.0.3（commit `3b97ed5`）。
- `main`：与上游一致。
- `oplus-systemui-fix`：黑屏修复的源码改动分支（`GuestVm.kt`，+24 行）。
- `progress-archive`（本分支）：汇总全部工程记录、补丁与构建产物，源码树与上游相同。

## 环境

| 项 | 值 |
|---|---|
| 宿主设备 | realme RMX3888，realme UI 5.0 |
| 宿主系统 | Android 14，arm64 |
| 客户机 | Android 14（API 34），引擎 `libaemu64_34.so` |
| 客户机镜像 | `RMX3888_14.0.0.228(CN01)_slim.zip`（官方包精简版，7,040,835,911 字节） |
| 构建要求 | Gradle 8.14.2，JDK 17，compileSdk 36，minSdk 26，targetSdk 28，abiFilters arm64-v8a |

## 改动内容

### 1. 源码改动（`oplus-systemui-fix` 分支，`GuestVm.kt`）

新增 `oplusSystemUi()`，由 `afterBoot()` 调用：

- 检测条件：客户机 `my_product/build.prop`、`system/build.prop`、`vendor/build.prop` 任一包含 `ro.build.version.oplusrom` 或 `ro.oplus.`。
- 命中后执行：
  ```
  settings put system key_is_open_prevent_mode false
  am force-stop com.android.systemui
  am start-service -n com.android.systemui/.SystemUIService
  ```
- 未命中时不执行任何操作。
- 写入时机放在 `afterBoot()`：客机 `settings.db` 在更早的启动阶段尚不存在。

对应补丁脚本：`patches/p31_patch.py`；基线到最终状态的差异：`patches/p27-to-p34-GuestVm.diff`。

### 2. 客户机镜像侧（早期 smali 方案）

早期直接改写反编译后的 `classes.dex`，历经 p20–p34 多轮迭代。最终有效改动与源码改动等价（写 prevent-mode 键 + 重启 SystemUI），另外两处为：

- 移除两处 `const/16 v3, 0xf0` 密度硬编码，恢复 `getDensity()` 动态取值。
- 客机分辨率由 540×960 调整为 720×1600。

`GuestVm.smali` 是唯一需要修改的 smali 文件；`TreeFixer.smali`、`InputService.smali` 与基线 p27 一致。逐轮摘要见 `patches/rounds/README.md`。

## 结果概览

| 项目 | 状态 | 依据 |
|---|---|---|
| 黑屏（SystemUI 反复崩溃） | 已修复 | 日志出现 `AEMU-SUI-RESTART` 后进入桌面 |
| 显示比例 | 已调整 | 日志 `framebuffer: 720x1600`、`Physical size: 720x1600` |
| 外部 APK 导入 | 未确定 | 待客机 `pm list packages` 结果 |
| 联网 | 未确定 | DNS 解析正常，HTTP/HTTPS 层待实测 |
| 导航键 | 规避方式 | 关闭应用内按键栏，使用客机原生三键导航 |
| 部分系统应用无法启动 | ROM 精简所致 | 62 个被删包仍被配置引用，见 `ROM精简与依赖核对.md` |

## 验证标记

| 日志标记 | 含义 |
|---|---|
| `AEMU-SUI-RESTART` | SystemUI 重启命令已执行 |
| `false` | `settings get system key_is_open_prevent_mode` 读回值 |
| `Starting service: Intent { cmp=com.android.systemui/.SystemUIService }` | SystemUI 服务启动 |
| `framebuffer: 720x1600` / `Physical size: 720x1600` | 分辨率与密度配置生效 |

黑屏期间的典型日志：`UnsupportedOperationException: Can't convert value at index 2 to dimension: type=0x1`、`has crashed too many times, killing!`、`Input dispatching timed out (Application does not have a focused window)`。

## 目录

```
patches/                 补丁脚本、逐轮摘要、基线到最终的 diff
releases/                已签名 APK、classes.dex、构建说明
ROM精简与依赖核对.md      镜像精简范围与依赖核对结果
README.md                本文件
```

## 重建

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
git checkout oplus-systemui-fix
./gradlew assembleRelease
```

也可直接使用已验证产物 `releases/p34-signed.apk`。

复现 smali 层改动：

```bash
baksmali d base.apk -o work/ -j 8
python3 worklog/patches/p31_patch.py     # 幂等，锚点缺失则非零退出
smali assemble -a 34 -j 8 -o classes.dex work/
python3 worklog/patches/repack.py
zipalign -p -f 4 unsigned.apk aligned.apk
apksigner sign --ks <keystore> --out signed.apk aligned.apk
```
