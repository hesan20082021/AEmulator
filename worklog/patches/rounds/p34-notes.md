> 原始迭代笔记，保留原文。对话式表述为当时工作记录，非正式结论；客观摘要见 README.md。

# p34 — 三个新问题的排查结论 + 诊断包

## 一、先分清：哪些是精简 ROM 造成的，哪些是项目造成的

我用 `/sdcard/DSH_ai/rom/lists/` 里的原始清单做了核对，结论如下。

### 精简删除了什么（68 个包 + 56 个目录）

关键组件**没有**被删：
- `PackageInstaller`（在 system_ext）✅ 在
- `DocumentsUI` ✅ 在
- `PermissionController` ✅ 在
- `WebViewGoogle64CN` + `TrichromeLibrary64CN`（在 my_bigball/app）✅ 在
- `pm` / `app_process` ✅ 在

被删的 68 个包主要是应用：
浏览器相关区域里，`my_heytap/app/Browser/Browser.apk` **没有被删**。

### 但删包会造成依赖断裂（这是 ROM 侧的真实损伤）

`dep_check_results.json` 显示：**62 个被删包仍被保留的配置引用**，共 488 处。
举几个直接影响运行的例子：

| 被删包 | 仍被引用处 | 后果 |
|---|---|---|
| `com.heytap.openid` | `my_heytap/etc/permissions/privapp-permissions-oplus.xml:113` | 依赖 OpenID 的应用取不到身份 |
| `com.heytap.tas` | `nfcee_access.xml` / `default_app_list.xml`（owallet 角色） | 钱包类起不来 |
| `com.oplus.metis` | `default_grant_permissions_list.xml` + 两处 privapp 权限 | 权限授予缺失 |
| `com.coloros.shortcuts` | `startup_manager.xml:790`（提供 provider） | **启动链里引用了一个不存在的 provider** |
| `com.coloros.filemanager` | `appplatform_sau_list.xml:8` | 文件选择器相关 |

`startup_manager.xml` 里指向已删除 provider 的那条最值得怀疑——它会让启动阶段去找一个不存在的组件。

**所以：部分系统应用跑不起来，ROM 精简有直接责任。** 这不是项目的问题。

---

## 二、但「无法导入 APK」和「无法联网」不能都推给 ROM

因为对应的组件都还在。这两件我必须拿到真实报错才能定性。

### 已知线索

**导入 APK**：项目用的是
```kotlin
vm.guestShell("pm install -r " + img.sdcardPath + "/aemu-install.apk", 300_000)
```
（`VmActivity.kt:497`，`sdcardPath` 默认 `/mnt/sdcard`）
这条链路只要 `pm` 或路径映射有一个不对就失败，而 toast 只显示最后一行，信息很容易被吞。

**联网**：日志里 DNS 是通的——
```
20:24:28 之后的 amap/heytap 域名全部解析成功
```
说明「DNS → 宿主代理」这条路没问题。所以断点在 HTTP/HTTPS 层。
另外 `GuestVm.kt:399-400` 把 DNS 硬编码成：
```kotlin
overrides["net.dns1"] = "8.8.8.8"
overrides["net.dns2"] = "1.1.1.1"
```
在国内容易被污染/不可达，这是一个可疑点（但 DNS 代理是另一条路，需实测确认哪条在生效）。

---

## 三、p34 做什么

**只做一件事：把三个问题的现场数据一次带回来。** 不改任何行为逻辑，`TreeFixer.smali` 一个字节没动（已 diff 确认）。

`AEMU-SUI-RESTART` 之后会输出：

```
AEMU-SUI-RESTART
===NET===
<ping 223.5.5.5 的结果>
<net.dns / net.eth0 / net.wlan 相关属性>
<ip addr 前 8 行>
===PM===
<p /system/bin/pm 是否存在>
<pm list packages 前 3 行>      ← 关键：pm 能不能跑
===SVC===
<init.svc.installd>
<init.svc.zygote>
===WEBVIEW===
<pm list packages | grep webview>   ← WebView 是否注册成功
===SD===
</sdcard/ 前 3 项>                   ← 共享目录在 guest 里能不能读
AEMU-DIAG-END
```

### 怎么判读

| 现象 | 结论 |
|---|---|
| `pm list packages` 有输出 | pm 正常 → 导入失败是路径/权限问题 |
| `pm list packages` 报错或无输出 | **pm 坏了 → 这就是无法导入 APK 的根因** |
| `===NET===` ping 不通但 DNS 通 | 是路由/NAT 问题，不是 DNS |
| `grep webview` 为空 | **WebView 没注册 → 浏览器必然打不开** |
| `/sdcard/` 列不出文件 | 共享目录映射断了 → 导入 APK 必然失败 |

---

## 四、你现在可以先自己试的两步

1. **导入 APK**：把 APK 直接复制到
   `/storage/emulated/0/AEmulator/Realme RMX3888 _ realme UI 5.0 (xvu3fa)/`
   然后在 guest 的「文件」里点它安装。这条绕过 `pm install`，能直接区分是「安装器坏了」还是「pm 命令坏了」。
   （注意：`com.coloros.filemanager` 被精简掉了，可能没有文件管理器可点——那就说明问题在这。）

2. **联网**：先开飞行模式再关，让 guest 重新拿一次网络；如果还是不行，看 guest 的 WiFi 图标是否显示已连接。

---

## 五、我的判断（等你数据验证）

- **比例**：已解决（720×1600 / 320dpi 生效，日志确认 `framebuffer: 720x1600`）
- **黑屏**：已解决（`AEMU-SUI-RESTART` 后桌面正常）
- **按键**：关掉 App 按键栏用 guest 原生导航栏，这条路可行
- **部分系统应用跑不起来**：**ROM 精简的责任**，62 个包存在断裂引用
- **无法导入 APK**：待 p34 数据定性（`pm` 能否执行）
- **无法联网**：待 p34 数据定性（ping 通不通）

把 `AEMU-SUI-RESTART` 到 `AEMU-DIAG-END` 之间那段贴给我，这三项我能一次给结论。
