> 原始迭代笔记，保留原文。对话式表述为当时工作记录，非正式结论；客观摘要见 README.md。

# p20 补丁说明（让 realme RMX3888 / Android 14 固件能过 system_server 启动阶段）

## 根因
guest 的 SystemConfig 从 /odm/etc/permissions/android.hardware.consumerir.xml 读到
`android.hardware.consumerir`，于是 SystemServer 去启动 ConsumerIrService；引擎把
vendor 的 consumerir 版 HAL（consumerir.default.so）早按 VENDOR_HALS 停掉了，于是
ConsumerIrService 构造函数抛：
    java.lang.RuntimeException: FEATURE_CONSUMER_IR present, but no IR HAL loaded!
system_server 直接死，zygote 被带走（exit 137），宿主看门狗只能不停重启系统 —— 这就是
aemu-xvu3fa-host.log.txt 里 zygote crashed (code 137) 循环的真正原因。

引擎本来就有"把声明和 HAL 一起收起来"的逻辑（TreeFixer.installNative64），但只扫了
system/etc/permissions 与 vendor/etc/permissions 两个目录；这台机器的权限文件躺在
odm / product / system_ext / my_* 分区里，所以漏掉了。

## 改动
1. TreeFixer：权限目录从 2 个扩到 15 个（system、vendor、odm、product、system_ext、
   system/product、system/system_ext、my_product、my_stock、my_bigball、my_heytap、
   my_engineering、my_region、my_carrier、my_manifest）。
2. GuestVm：补上 dumpAnrLogs()（CrashDumpThread 在 zygote 死亡时调它取证，p19 里
   这个方法缺失，导致 host 日志里的
   `forensics failed: java.lang.NoSuchMethodError: No virtual method dumpAnrLogs()`）。

## 产物
- app.aemu.0003-p20.apk —— 用 patch_keep/keys/aemu.keystore 签名，证书与 p19 相同
  (SHA-256 a572ec…2d4d)，可直接覆盖安装。
- classes_p20.dex —— 打好的 classes.dex。
- p20_patch.py —— 对 classes.dex 反编译出的 smali 所做改动的脚本。

## 安装/验证
1. 手机上安装 app.aemu.0003-p20.apk（覆盖 p19）。
2. 启动该 ROM 实例，看宿主日志：
   - 应出现 `vendor HALs set aside: N`（N 变大），
   - 不应再出现 `FEATURE_CONSUMER_IR present, but no IR HAL loaded!`，
   - 不应再出现 `✖ zygote crashed (code 137)` 循环。
3. guest 侧应在 /dev/log 里看到 system_server 继续往下走（过了 StartConsumerIrService）。
