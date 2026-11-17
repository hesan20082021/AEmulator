# p34 构建产物说明

本目录保存 p34 轮次验证过的构建产物。

## 文件

| 文件 | 大小 | 说明 |
|---|---|---|
| `p34-signed.apk` | 70,799,474 字节 | 已签名安装包，可在宿主设备安装 |
| `classes_p34.dex` | 30,928,440 字节 | p34 的 classes.dex，可替换进 base.apk 重新打包 |
| `p34-build-notes.md` | 本文件 | 构建与验证记录 |

## 签名信息

| 项 | 值 |
|---|---|
| 签名工具 | `/root/android-sdk/build-tools/37.0.0/apksigner`（aarch64） |
| 对齐工具 | `zipalign -p -f 4` |
| 签名方案 | v1 / v2 / v3（minSdk 26，v2/v3 生效） |
| 密钥库 | `/sdcard/DSH_ai/VM/patch_keep/keys/aemu.keystore` |
| 别名 | `aemu` |
| 证书 SHA-256 | `a572ecc52e67e8fa82839276879928f25cb398116f9048aaea8ffae731732d4d` |

覆盖安装要求签名一致；签名不同则需先卸载（会清除客户机数据）。

## 构建方法

以 `patch_keep/base.apk` 为基底，替换其中的 `classes.dex`：

```python
# 逐条目复制 base.apk，仅替换 classes.dex，保留 date_time / external_attr / compress_type
# 见 worklog/patches/repack.py
```

随后：
```bash
zipalign -p -f 4 unsigned.apk aligned.apk
apksigner sign --ks <keystore> --out signed.apk aligned.apk
apksigner verify --verbose signed.apk
```

## 镜像来源与精简核对

客户机镜像为 `RMX3888_14.0.0.228(CN01)_slim.zip` 的精简版。原始清单位于
`/sdcard/DSH_ai/rom/lists/`，依赖核对结果见
`worklog/diagnostics/RMX3888报告核验结论.md`。

核对要点：

- 删除清单 `delete_list.json` 含 68 个包；`delete_dirs.json` 按分区记录删除目录。
- `PackageInstaller`、`DocumentsUI`、`PermissionController`、`WebViewGoogle64CN`、
  `TrichromeLibrary64CN`、`pm`、`app_process` 均保留。
- `dep_check_results.json` 记录 62 个被删包仍被保留配置引用（共 488 处）。典型：
  - `com.heytap.openid` → `my_heytap/etc/permissions/privapp-permissions-oplus.xml:113`
  - `com.coloros.shortcuts` → `startup_manager.xml:790`
  - `com.oplus.metis` → `default_grant_permissions_list.xml` 及两处 privapp 权限

## 验证标记

日志中用于确认改动执行的标记：`AEMU-SUI-RESTART`、`AEMU-DIAG-END`、
`framebuffer: 720x1600`、`Physical size: 720x1600`。

早期故障期间日志出现：
`UnsupportedOperationException: Can't convert value at index 2 to dimension: type=0x1`、
`has crashed too many times, killing!`、
`Input dispatching timed out (Application does not have a focused window)`。
