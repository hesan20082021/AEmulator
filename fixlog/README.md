# p35/p36 补丁镜像（源仓库：aemu-android14-vm，暂存于此）

> aemu-android14-vm 是私有仓库，当前 MCP token 白名单里没有它（404），先镜像到主仓库 fixlog 分支保数据；白名单加好后迁回。

## 文件清单

- `patches/scripts/p35_netfix.py` —— p35 补丁：Settings.Global 关 captive portal 验证 + hicloud 探针（网络修复，已实测 VALIDATED）
- `patches/scripts/p36_reorder.py` —— p36 补丁：afterBoot 尾部顺序对调修完整版黑屏回归 + 命令瘦身 + 取证落盘
- `patches/rounds/p35/README.md` —— p35 轮次文档（含实测结果补记）
- `patches/rounds/p36/README.md` —— p36 轮次文档（含黑屏回归差分推理）
- `patches/p34-to-p36-GuestVm.diff` —— p34 → p36 GuestVm.smali 完整差分
- `patches/p34-TreeFixer-my-partitions.diff` —— TreeFixer my_* 分区适配差分（对应 AEmulator 源码仓 b665e58）

## 实测结论摘要

- **网络修复成功**：captive_portal_mode 0 + hicloud 探针写入生效，dumpsys 出现 `EVER_VALIDATED & IS_VALIDATED`。
- **p35 引入完整版黑屏回归**：netFix 在 SystemUI 重启最脆弱窗口连写 9 条 global 设置触发广播风暴；精简版 SystemUI 轻扛住了。
- **p36 修法**：netFix 挪到 restartSystemUi 之前（恢复 p34 已验证终态），去掉不存在的 reprobe/缺失的 wget/会崩的 grep 管道，logcat/dumpsys/window 落盘共享 sdcard 供下一轮零猜测。
- 测试包：`AEmulator-p36-netfix.apk`（证书与 p34/p35 一致，可直接覆盖安装）。
