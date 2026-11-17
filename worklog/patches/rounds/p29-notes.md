> 原始迭代笔记，保留原文。对话式表述为当时工作记录，非正式结论；客观摘要见 README.md。

# p29 — 修复 p28 引起的启动闪退（VerifyError）

## 一、闪退根因（真实栈，来自 `Download/aemu-crash-latest.txt`）

```
java.lang.VerifyError: Verifier rejected class app.aemu.core.TreeFixer:
  void app.aemu.core.TreeFixer.xmlSettings() failed to verify:
  [0x110] register v5 has type Precise Reference: java.lang.String
          but expected Integer
  at app.aemu.core.GuestVm.<init>(GuestVm.kt:100)
  at app.aemu.ui.VmActivity.onCreate(VmActivity.kt:180)
```

**是我 p28 补丁自己的 bug，跟 ROM、跟引擎都无关。**

p28 的 P1b 往 `TreeFixer.xmlSettings()` 的 `Triple[]` 数组里插了一个新元素，复用了
`v4 / v5 / v6`。但该处 `v5` 在此之前已经被赋成 **int**（字符串拼接的索引）。
ART 的验证器要求「同一寄存器在一个方法内只能有一种类型」，于是：

- 类验证阶段直接拒收**整个 `TreeFixer` 类**
- `GuestVm.<init>` 一构造就要 new TreeFixer → 立刻抛 `VerifyError`
- `VmActivity.onCreate` 崩 → **点启动就闪退**

而且查了 `Kernel64.kt`：只有 API 23/24/25（A6/A7_0/A7_1）开了 `xmlSettings`，
**A14（API 34）是 `false`**。所以那段补丁对本机根本用不上——白加，还炸了。

## 二、p29 怎么改的

原则：**不再往任何既有方法里插代码**，所有新逻辑放进独立方法。

| # | 改动 | 是否改既有寄存器类型 |
|---|------|---------------------|
| P1 | 新增 `GuestVm.noPreventMode()`，寄存器自用 | 否（新方法） |
| P2 | `doBoot()` 在 `fixup` 后加一行 `invoke-direct {v1}` | **否**（v1 在该方法里本就是 `this`，实测作 this 读字段 133 次） |
| P3 | `autoDump()` 加一行 `invoke-direct {p0}` | **否**（p0 就是 `this`） |
| P4 | 撤掉 p27 的 `wm density 240; wm size 540x960` | 否（只换常量字符串内容，寄存器不变） |

**`TreeFixer.smali` 一个字节都没动**——已用 `diff` 确认与 p27 基线完全一致。

### noPreventMode() 干什么

```
/dev/.aemu-prevent 已存在 → 直接返回（只做一次）
否则:
  settings put system key_is_open_prevent_mode false
  settings get system key_is_open_prevent_mode
  读回等于 "false" → 落标记文件 + 打日志
                    → "prevent-mode: key_is_open_prevent_mode=false confirmed"
```

这条设置是黑屏的**总开关**：SystemUI 读不到它就默认按「开启」处理，
进而 inflate 防误触布局失败、每 2 秒崩一次、最后被系统打死 —— 没有 SystemUI
就没有焦点窗口，表现为黑屏且点不动（详见 p28/README.md 的完整链条）。

## 三、这轮做过的验证（以及哪些验证不可用）

**做了：**
1. **寄存器分型检查**：新方法里 `v0/v1/v2/v6/v7` 全是引用、`v3/v4/v5` 全是整数，无跨类型 ✔
2. **插入点 this 寄存器确认**：`doBoot` 用 `v1`（133 次作 this）、`autoDump` 用 `p0`（3 次作 this），与插入的 invoke 一致 ✔
3. **baksmali 反解析**：新方法结构完整，分支极性正确（文件存在→返回；读回为 null 或非 "false"→跳过）✔
4. **往返装配**：dex → smali → dex，字节数完全一致（30928036），无畸形指令 ✔
5. **对照组**：把 p28 的错误补丁重建出来，确认「复用已赋 int 的寄存器」正是崩溃成因 ✔

**不可用（如实说明）：**
- 本地 `dex2oat --compiler-filter=verify` 跑不起来：沙箱里缺 linker 配置，
  且子进程被 SELinux 拒绝（strace 显示 `exited with 1` 后 SIGABRT）。
  所以**没能**在装机前用官方验证器跑一遍。
- 我写的通用类型流检查器对干净基线 `p27` 也报冲突（误报），因此**不作为判据**，
  只用于对照崩溃成因。

## 四、产物

| 文件 | 说明 |
|------|------|
| `p29-signed.apk` | 已签名，证书 SHA-256 `a572ecc5…731732d4d`（与 p20~p28 同一把） |
| `classes_p29.dex` | 打好的 classes.dex |
| `p29_patch.py` | 补丁脚本（从干净 `p27smali` 一次跑完 P1~P4） |
| `d1_smali_p29.tar.gz` | 完整 smali 树 |

## 五、安装与验证

```
adb install -r p29-signed.apk
```

或手机点安装（覆盖 p28，签名相同，不用卸载）。

**应当不再闪退**，并在宿主日志看到：
```
prevent-mode: key_is_open_prevent_mode=false confirmed (SystemUI crash chain broken)
```

**如果还闪退**，引擎会自动把栈写到 `Download/aemu-crash-latest.txt`，
把那个文件给我 —— 这轮的根因就是从那里来的，路径可靠。

## 六、我的责任

p28 是我交付的，崩了是我的错。教训很具体：
**往 smali 既有方法里插代码时，必须逐个确认被复用寄存器的既有类型**，
而我 p28 只看了「逻辑对不对」，没查「类型流干不干净」。
这轮改成不动既有方法，从结构上杜绝同类错误。
