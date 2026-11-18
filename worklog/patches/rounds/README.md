# 补丁迭代记录 p20–p34

按轮次记录客户机适配过程中每次改动的目标、内容、验证方式与可观察结果。
各轮对应的脚本见 `worklog/patches/`，最终产物见 `worklog/releases/`。

---

## p20 — system_server 启动阶段适配

**目标**：使 realme RMX3888 / Android 14 固件通过 system_server 启动阶段。
**内容**：反编译 `classes.dex` 后修改 smali 层，重新打包并签名。
**产物**：classes_p20.dex、app.aemu.0003-p20.apk。
**验证**：观察客户机是否越过 system_server 阶段继续启动。

---

## p21 / p22 — 黑屏诊断增强与 SecureElement 崩溃处理

**内容**：增加开机阶段的日志输出；处理 SecureElement 相关组件的崩溃循环。
**日志观察（p21）**：黑屏期间 SystemUI 进程反复重启。

---

## p27 — 基线

**说明**：干净基线，未包含 prevent-mode 相关改动。
`grep -c "key_is_open_prevent_mode|noPreventMode"` 结果为 0。
`TreeFixer.noScreenSleep()` 与 `InputService` 均保持上游原样。

---

## p28 — SystemUI 崩溃循环修复尝试（已撤回）

**目标**：处理 SystemUI 反复崩溃导致的黑屏。
**改动**：在 `TreeFixer.xmlSettings()` 中插入 prevent-mode 相关代码。
**结果**：验证阶段发现该方法复用了已赋值为 int 的寄存器 `v5`，ART 在类验证阶段拒绝整个类：

```
java.lang.VerifyError: Verifier rejected class app.aemu.core.TreeFixer:
  xmlSettings() failed to verify:
  [0x110] register v5 has type String but expected Integer
```

`GuestVm` 构造时触发该类加载，导致点击启动即闪退。
**处置**：该轮改动整体撤回；后续轮次改为在独立方法中添加逻辑，调用点只加入无参 invoke。

---

## p29 — 修复 p28 引起的 VerifyError

**目标**：消除 p28 引入的启动闪退。
**根因**：p28 在 `xmlSettings()` 数组中插入 Triple 时复用了 `v4/v5/v6`，其中 `v5` 已为 int 类型。
**改动**：新增独立方法 `noPreventMode()`，在 `doBoot()` 中 `fixup` 之后调用。
**结果**：闪退消失，黑屏未消失。`noPreventMode()` 在 zygote 尚未启动时调用 `guestShell(...)`，命令未执行，异常被 `catchall` 吞掉，未产生日志。

---

## p30（未交付）— 写入时机分析

查明的三点事实：

1. p27 基线中 `TreeFixer.fixup()` 不调用 `noScreenSleep()`，仅 `afterBoot()` 调用。
2. `noScreenSleep()` 开头判断 `data/data/com.android.providers.settings/databases/settings.db` 是否存在；不存在则直接 `return-void`。首次开机时该文件不存在。
3. `Kernel64.kt` 中 `xmlSettings = true` 仅对 API 23/24/25 设置；API 34 为 false，xml 分支不执行。

据此，设置写入安排在 `afterBoot`。

---

## p31 — 黑屏修复（afterBoot 重启 SystemUI）

**目标**：在设置写入后重启已崩溃的 SystemUI。
**改动**（独立方法 + 单点无参调用，避开 p28 的寄存器类型冲突）：

- 新增 `restartSystemUi()`（`.locals 6`），执行：
  ```
  settings put system key_is_open_prevent_mode false
  am force-stop com.android.systemui
  am start-service -n com.android.systemui/.SystemUIService
  echo AEMU-SUI-RESTART
  ```
- 在 `afterBoot()` 末尾 `return-void` 前加入一条 `invoke-direct {v1}`（`v1` 为 this）。

**寄存器处理**：`const-string` 不能用 v16+；`vm density` 相关的 `move-result v3` 后紧跟 `const/16 v3, 0xf0` 会覆盖动态取值，需删除。
**日志证据**：

```
AEMU-DIAG-BEGIN
false
Starting service: Intent { cmp=com.android.systemui/.SystemUIService }
AEMU-SUI-RESTART
```

随后出现桌面。
**验证方式**：baksmali 往返 + 寄存器类型审计 + 字节级 diff。

---

## p32 — 比例修正

**目标**：修正状态栏时间被裁切、图标放大等比例问题。
**根因**：

1. `GuestVm` 写 props 处 `invoke-virtual getDensity()` 后紧跟 `const/16 v3, 0xf0`，将密度固定为 240，设置中的密度值无效。
2. 客户机分辨率 540×960（9:16）与宿主面板（约 9:20）比例不一致。

**改动**：删除两处 `const/16 v3, 0xf0`；移除 `wm density 240; wm size 540x960` 的持久化写入。
**验证结果**：`wm size reset` / `wm density reset` 仅回退到 framebuffer 值，无法改变比例；需在实例设置中调整分辨率。

---

## p33 — 诊断版

**内容**：加入 `===NET===`、`===PM===`、`===SVC===`、`===WEBVIEW===`、`===SD===`、`AEMU-DIAG-END` 等诊断输出。
**导航键调查**：

- `qemu.hw.mainkeys` 在 `showNavBar=true` 且 `navBarRequired=false`（A14 默认）时为 `"1"`，禁用客户机自带导航栏。
- App 注入按键中 BACK 有效，其余失效。
- 给 `.kl` 键位加 `FUNCTION` 标记（11 处）的尝试经与本机 Android 14 `Generic.kl` 对照后确认不适用，已撤回。

**规避方式**：关闭 App 内按键栏，使用客户机原生三键导航。

---

## p34 — 诊断包与依赖核对

**内容**：在 afterBoot shell 命令中追加诊断项，导出网络、包管理、服务、WebView、SD 卡信息。
**ROM 精简核对**：见 `worklog/ROM精简与依赖核对.md` 与 `worklog/releases/p34-build-notes.md`。关键事实：68 个包被删；62 个被删包仍被保留配置引用（488 处）；核心组件（PackageInstaller、DocumentsUI、PermissionController、WebView 相关、pm、app_process）均保留。
**未决问题**：外部 APK 导入、联网、导航键注入，见 `worklog/README.md`「结果概览」。
