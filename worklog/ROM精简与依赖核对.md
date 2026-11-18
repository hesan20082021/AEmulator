# ROM 精简与依赖核对

客户机镜像 `RMX3888_14.0.0.228(CN01)_slim.zip` 是官方 OTA 包的精简版。本节记录精简范围与依赖核对结果。

## 精简范围

- 删除 68 个应用包、56 个目录。
- 保留的核心组件：`PackageInstaller`（system_ext）、`DocumentsUI`、`PermissionController`、`WebViewGoogle64CN` 与 `TrichromeLibrary64CN`（my_bigball/app）、`pm`、`app_process`。
- 浏览器类应用中 `my_heytap/app/Browser/Browser.apk` 未删除。

## 依赖断裂

精简后仍有配置指向被删除的包：62 个被删包被引用，合计 488 处。典型条目：

| 被删包 | 引用位置 | 影响 |
|---|---|---|
| `com.heytap.openid` | `my_heytap/etc/permissions/privapp-permissions-oplus.xml:113` | 依赖 OpenID 的应用取不到身份 |
| `com.heytap.tas` | `nfcee_access.xml` / `default_app_list.xml`（owallet 角色） | 钱包类无法启动 |
| `com.oplus.metis` | `default_grant_permissions_list.xml` 及两处 privapp 权限 | 权限授予缺失 |
| `com.coloros.shortcuts` | `startup_manager.xml:790`（提供 provider） | 启动链引用了不存在的 provider |
| `com.coloros.filemanager` | `appplatform_sau_list.xml:8` | 文件选择器相关 |

## 核对范围说明

以上为镜像精简本身带来的影响。外部 APK 导入、联网两项的成因需结合客机实测确定，不在此处下结论。
