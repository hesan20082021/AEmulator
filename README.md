<div align="center">

<img src="docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**在现代手机上运行经典 Android 固件——HTC Sense、TouchWiz、MIUI、AOSP。无需 root，无需电脑。**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

**🇬🇧 English** · [🇷🇺 Русский](docs/i18n/README.ru.md) · [🇺🇦 Українська](docs/i18n/README.uk.md) · [🇩🇪 Deutsch](docs/i18n/README.de.md) · [🇫🇷 Français](docs/i18n/README.fr.md) · [🇪🇸 Español](docs/i18n/README.es.md) · [🇧🇷 Português](docs/i18n/README.pt-BR.md) · [🇮🇹 Italiano](docs/i18n/README.it.md) · [🇵🇱 Polski](docs/i18n/README.pl.md) · [🇹🇷 Türkçe](docs/i18n/README.tr.md) · [🇸🇦 العربية](docs/i18n/README.ar.md) · [🇮🇷 فارسی](docs/i18n/README.fa.md) · [🇮🇳 हिन्दी](docs/i18n/README.hi.md) · [🇮🇩 Indonesia](docs/i18n/README.id.md) · [🇻🇳 Tiếng Việt](docs/i18n/README.vi.md) · [🇨🇳 简体中文](docs/i18n/README.zh-CN.md) · [🇯🇵 日本語](docs/i18n/README.ja.md) · [🇰🇷 한국어](docs/i18n/README.ko.md)

</div>

---

## 这个项目做了什么

AEmulator 让经典安卓系统镜像直接跑在现代安卓手机上，无需 root、无需电脑。它从你已有的固件文件（卡刷 ZIP、Odin 包、Google 出厂镜像、GSI）启动真实的 Android 2.3–17 系统：老固件走补丁版 QEMU，Android 5.0 以上在手机的 arm64 核心上原生运行。内核 binder 被模拟，图形走手机 GPU，声音走安卓音频栈，全部装在一个普通 App 里。

本项目是 AEmulator 0.0.0.3 的一个 fork，在此基础上做了 realme RMX3888 / realme UI 5.0（Android 14）客机的适配：

- 修复 Oplus / realme UI 客机 SystemUI 反复崩溃导致的黑屏。
- 显示调整为 720×1600，并去掉写死的密度值。
- 外部 APK 导入、联网、导航键注入三项尚未有确定结论。

分支说明：`main` 与上游一致；`oplus-systemui-fix` 存放适配源码；`progress-archive`（当前分支）保存完整的工程记录。适配细节见 [worklog/README.md](worklog/README.md)。

最新版 APK 由 GitHub Actions 自动打包，可在 [Releases](https://github.com/hesan20082021/AEmulator/releases) 下载。

## ✨ 功能

- 导入几乎所有固件格式：CWM/TWRP 卡刷 ZIP、三星 Odin `.tar.md5`、Google 出厂 `.tgz`、`system.img`、OTA `system.new.dat.br`
- 厂商系统原样运行：HTC Sense、三星 TouchWiz、MIUI、AOSP
- 经 GL 桥的硬件图形、声音、触控与多点触控，带现代 TLS 代理的网络
- 共享存储卡文件夹，方便放 APK、音乐和照片
- Material 3 Expressive 界面，支持 18 种语言
- 免费开源（GPL-3.0）

## 🚀 快速开始

1. 从 [Releases](https://github.com/hesan20082021/AEmulator/releases) 下载并安装 APK。
2. 将固件文件下载到手机。
3. 打开 AEmulator →**添加固件**并选择文件。导入需要几分钟。
4. 点击**启动**。首次启动较慢：系统正在优化应用。
5. ⋮ 菜单可调音量、电源键和日志；⚙️ 打开设置与语言。

## 📋 要求

- 64 位 ARM 手机（arm64-v8a）上的 Android 8.0+
- 每个固件约需 1–3 GB 空间
- 推荐较新的骁龙 / 天玑 / Tensor 芯片

## ⚙️ 工作原理

在 Android 2.3–4.4 上，每个客户机进程运行在改进的用户态 QEMU 中；在 5.0–17 上，固件自带的 arm64 程序原生运行，由每个 Android 版本各自的引擎内核拦截其系统调用。binder 守护进程取代内核驱动，GL 桥把 OpenGL ES 调用转发给 GPU，小型客户机库（音频 HAL、audio policy 包装、LD_PRELOAD 垫片）让厂商代码适配模拟器。导入器读取固件，在 boot 镜像中找到 init 脚本，并生成系统服务的启动计划。

## 🛠️ 从源码构建

需要 JDK 17、Android SDK 36 和 NDK r28。客户机库通过 `native/*/build.sh` 构建。

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 许可证

GPL-3.0。Android、商标及固件归其所有者所有。
