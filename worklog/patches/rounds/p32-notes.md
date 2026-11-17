> 原始迭代笔记，保留原文。对话式表述为当时工作记录，非正式结论；客观摘要见 README.md。

# p32 — 黑屏已破，修比例崩坏

## 一、p31 的成果（日志实证）

```
19:28:42 false
Starting service: Intent { cmp=com.android.systemui/.SystemUIService }
AEMU-SUI-RESTART
```

对应关系：
- `false` ← `settings get system key_is_open_prevent_mode` 读回值，**设置写成功了**
- `Starting service: ...SystemUIService` ← SystemUI 被重新拉起
- `AEMU-SUI-RESTART` ← 我们打的标记

**桌面出来了 → 黑屏根因确认无误**：SystemUI 因 `key_is_open_prevent_mode` 读不到（null → 默认 true）
而 inflate 防误触布局失败、每 2 秒崩一次、最后被系统打死，没有焦点窗口 → 黑屏点不动。
p31 里「afterBoot 后写设置 + 重启 SystemUI」这条路是对的，保留不动。

## 二、这一轮修什么：比例崩坏

截图症状：时间「19:26」被裁成「19:2」、图标异常巨大、内容整体放大并溢出。
这是 **density / wm size 被强制**导致的，有两个来源：

### 来源 1：密度被焊死成 240（p27 遗留）

`GuestVm` 写 props 的代码是：
```
invoke-virtual {v9}, Lapp/aemu/core/VmSettings;->getDensity()I
move-result v3
const/16 v3, 0xf0        ← 把上一行的结果直接覆盖成 240
```
`getDensity()` 的返回值被 `const/16 v3, 0xf0` 无条件覆盖，**实例设置多少都没用，永远是 240dpi**。
而 `hwc.c` 里 HWC 上报的密度是 `160000`（=160dpi）。两者差 1.5 倍，正是放大量级。

**修复**：删掉两处 `const/16 v3, 0xf0`，恢复源码原样 `overrides["ro.sf.lcd_density"] = s.density.toString()`。

### 来源 2：p27 的 `wm density 240; wm size 540x960` 已持久化

`wm size 540x960` 会把逻辑分辨率强制成 540×960 并**写进 settings.db**（`display_size_forced`）。
p31 只是不再执行这条命令，但**磁盘上的强制值还在**，所以比例依然是坏的。

**修复**：在 `restartSystemUi()` 开头加 `wm density reset; wm size reset`，清掉残留强制值。

## 三、改动清单（相对 p31）

| 位置 | 改动 |
|---|---|
| `GuestVm` props 写入（两处） | 删除 `const/16 v3, 0xf0`，恢复 `getDensity()` 动态值 |
| `restartSystemUi()` | 开头加 `wm density reset; wm size reset` |
| `restartSystemUi()` | 追加回报 `ro.sf.lcd_density`、`wm size`、`wm density` 实际值 |

## 四、验证方法

装 p32 后启动，宿主日志里 `AEMU-SUI-RESTART` 之后会多出几行实际值：

```
AEMU-SUI-RESTART
<ro.sf.lcd_density 的值>
Physical size: 1080x2400        ← wm size（应是面板真实值，不再是 540x960）
Physical density: 480           ← wm density（不再是 240）
<systemui 的 pid>
```

判定：
- `wm size` 不再显示 `540x960` → 强制值清掉了
- 密度和面板匹配 → 比例恢复正常
- 桌面图标、状态栏文字大小正常

## 五、关于「偶尔黑屏」

比例问题是**稳定复现**的（每次都会），而「偶尔黑屏」是另一回事。目前证据里能看到的关联是：

`19:28:41 memory: killed background process 22340 (adj 12, 107 MB; cached 11, host free 2895 MB)`

宿主内存管理（`GuestLmk`）在杀后台进程。如果 SystemUI 在某个时刻被当成缓存进程杀掉，
又没有东西拉起它，就会再黑一次。p31 的重启逻辑只在 `afterBoot` 跑一次，**杀完不会自动重拉**。

装 p32 后如果「偶尔黑屏」还在，请告诉我黑屏发生的时机（放多久会黑 / 点了什么会黑），
我会加一条「SystemUI 不在就重拉」的周期检查——但需要先确认是它被杀，而不是别的原因，
否则又是我在猜。
