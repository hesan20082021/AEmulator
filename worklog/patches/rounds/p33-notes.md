> 原始迭代笔记，保留原文。对话式表述为当时工作记录，非正式结论；客观摘要见 README.md。

# p33 — 诊断版：拿证据，不再猜

## 一、先说两条我查到的事实（都有本地实证）

### 你的猜测方向对了一半

你问「是不是全面屏手势的原因」，方向是对的——**问题确实出在 guest 的导航键处理**，
但具体不是全面屏手势，而是 `qemu.hw.mainkeys` 把 guest 自带导航栏藏了。

`GuestVm.kt:389`：
```kotlin
overrides["qemu.hw.mainkeys"] = if (s.showNavBar && !(engine == Engine.N64 && kernel.navBarRequired)) "1" else "0"
```
- `showNavBar = true`（App 的按键栏开着）
- `navBarRequired` 在 `Kernel64.kt` 里默认 `false`，A14 不显式设它
- ⇒ `qemu.hw.mainkeys = "1"` ⇒ **guest 自己的导航栏被禁用**

于是只能用 App 注入的按键，而注入在 Android 14 上除 BACK 之外都失效。

### 我犯的一个错（已撤回）

我先怀疑是 `.kl` 缺 `FUNCTION` 标记，动手加了 11 处。然后拿本机 Android 14 的
`/system/usr/keylayout/Generic.kl` 对照，发现：

```
key 102   MOVE_HOME          ← 官方：102 是 MOVE_HOME
key 172   HOME               ← 官方：HOME 是 172
key 139   MENU
key 158   BACK
key 580   APP_SWITCH
```

`FUNCTION` 在官方文件里**只用于 464-481 的多媒体键**，HOME/MENU/APP_SWITCH 都没有。
我那个改法是错的，**已全部回滚**（p33 树从 p31 重新复制）。

## 二、一个你现在就能用的解法（不用装包）

设置里把 **「导航栏」开关关掉**（`showNavBar = false`）。

这样 `qemu.hw.mainkeys = "0"` → guest 显示它自己的三键导航栏 →
返回、主页、多任务**原生可用**，完全不依赖注入。

这是目前最稳的路，因为它绕开了整个「注入是否生效」的问题。

## 三、p33 做了什么

这一版**不夹带未经验证的修改**，只做一件事：**把现场数据带回来**。

`restartSystemUi()` 里的诊断命令会输出：

```
AEMU-DIAG-BEGIN
<key_is_open_prevent_mode 的值>
<ro.sf.lcd_density>
Physical size: ...
Physical density: ...
---kl---
<dhd-touch.kl 的实际内容>
---vendor---
<vendor 下的同名文件>
---generic---
<Generic.kl 里 102/158/139/580/172 的真实映射>
AEMU-DIAG-END
AEMU-SUI-RESTART
<systemui pid>
```

装 p33 后把这整段贴给我，我就能确定：
1. `dhd-touch.kl` 到底写没写进去、内容对不对
2. guest 自己的 `Generic.kl` 里 102 是 HOME 还是 MOVE_HOME
3. 该改 kl、还是该改注入方式

## 四、比例问题

日志已确认：`wm size = 540x960`、`density = 240`。
这是实例设置本身的值（`VmSettings` 默认 `width=540, height=960, density=240`），
`wm size reset` 只是回到 framebuffer 尺寸，所以没法靠 reset 改。

宿主面板约 9:20，guest 是 9:16，**宽高比不一致** → 系统 UI 布局按 9:16 排，
放进 9:20 的框里就被拉长/裁切。

你说要「设置页能自由设置」——**这个功能本来就有**：
设置 → 显示器 → 三个预设按钮下面有 **宽 / 高 / DPI 三个输入框**
（宽 240–2160，高 320–3840，DPI 96–640）。

想要和主屏同比例，填：

| 宽 | 高 | DPI |
|---|---|---|
| 1080 | 2400 | 480 |

或者省资源一点：**720 × 1600 / 320**

改完重启实例即可。这个不需要打补丁，你自己在设置里调就行。

## 五、下一步顺序（建议）

1. **先关掉 App 导航栏开关** → 看 home/多任务能不能用（最快验证方向对不对）
2. **再把分辨率改成 1080×2400 或 720×1600** → 看比例是否正常
3. **如果第 1 步有效**，那按键问题就到此为止，不用再修注入
4. 装 p33 把 `AEMU-DIAG` 那段给我，我据此决定要不要动 kl

第 1、2 步都不用改代码，你在设置里点几下就行。
