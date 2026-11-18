<div align="center">

<img src="docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**Run classic Android firmware — HTC Sense, TouchWiz, MIUI, AOSP — on a modern phone. No root, no PC.**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

**🇬🇧 English** · [🇷🇺 Русский](docs/i18n/README.ru.md) · [🇺🇦 Українська](docs/i18n/README.uk.md) · [🇩🇪 Deutsch](docs/i18n/README.de.md) · [🇫🇷 Français](docs/i18n/README.fr.md) · [🇪🇸 Español](docs/i18n/README.es.md) · [🇧🇷 Português](docs/i18n/README.pt-BR.md) · [🇮🇹 Italiano](docs/i18n/README.it.md) · [🇵🇱 Polski](docs/i18n/README.pl.md) · [🇹🇷 Türkçe](docs/i18n/README.tr.md) · [🇸🇦 العربية](docs/i18n/README.ar.md) · [🇮🇷 فارسی](docs/i18n/README.fa.md) · [🇮🇳 हिन्दी](docs/i18n/README.hi.md) · [🇮🇩 Indonesia](docs/i18n/README.id.md) · [🇻🇳 Tiếng Việt](docs/i18n/README.vi.md) · [🇨🇳 简体中文](docs/i18n/README.zh-CN.md) · [🇯🇵 日本語](docs/i18n/README.ja.md) · [🇰🇷 한국어](docs/i18n/README.ko.md)

</div>

---

> [!NOTE]
> **这个分支做了什么（progress-archive）**
>
> 以 AEmulator 0.0.0.3 为基础，记录把 realme RMX3888 的 Android 14 系统镜像接入 AEmulator 的适配过程。上游 `main` 分支未改动。
>
> 结果概览：
> - 修复了 Oplus / realme UI 客机中 SystemUI 反复崩溃导致的黑屏。
> - 显示调整为 720×1600，并去掉了写死的密度值。
> - 外部 APK 导入、联网、导航键注入三项尚未有确定结论，现状与依据记录在 worklog 中。
>
> 分支关系：`main`（与上游一致） · `oplus-systemui-fix`（黑屏修复的源码改动） · `progress-archive`（本分支，完整工程记录）。
>
> 完整记录见 [worklog/README.md](worklog/README.md)。

AEmulator boots a real Android 2.3–17 system image straight from a firmware file you already have: a recovery ZIP, an Odin archive, a Google factory image or a GSI. Old 32-bit firmware (2.3–4.4) runs through a patched QEMU, Android 5.0–17 runs natively on the phone’s arm64 cores. The kernel’s binder is emulated, graphics use your phone’s GPU and sound goes through Android’s audio stack — everything runs inside a normal app.

## ✨ Features

- Import almost any firmware format: CWM/TWRP ZIP, Samsung Odin `.tar.md5`, Google factory `.tgz`, `system.img`, OTA `system.new.dat.br`
- Vendor skins work as shipped: HTC Sense, Samsung TouchWiz, MIUI, AOSP
- Hardware graphics through the GL bridge, sound, touch and multitouch, network with a modern TLS proxy
- Shared memory-card folder for APKs, music and photos
- Material 3 Expressive interface in 18 languages
- Free and open source (GPL-3.0)

## 🚀 Quick start

1. Download the APK from [Releases](https://github.com/hesan20082021/AEmulator/releases) and install it.
2. Download a firmware file to your phone.
3. Open AEmulator → **Add firmware** and pick the file. Import takes a few minutes.
4. Press **Start**. The first boot is slower: the system optimises its apps.
5. Use the ⋮ menu for volume, power button and logs; the ⚙️ button opens app settings and language.

## 📋 Requirements

- Android 8.0+ on a 64-bit ARM phone (arm64-v8a)
- About 1–3 GB of free space per firmware
- A recent Snapdragon / Dimensity / Tensor chip is recommended

## ⚙️ How it works

On Android 2.3–4.4 each guest process runs under a patched user-mode QEMU; on 5.0–17 the firmware’s own arm64 programs run natively, with one engine kernel per Android version catching their system calls. A binder daemon replaces the kernel driver, a GL bridge forwards OpenGL ES calls to the phone’s GPU, and small guest libraries (audio HAL, audio policy wrapper, LD_PRELOAD shim) adapt vendor code to the emulator. The importer reads the firmware, finds the init scripts in its boot image and builds a start plan for system services.

## 🛠️ Build from source

You need JDK 17, Android SDK 36 and NDK r28. Native guest parts are built with the scripts in `native/*/build.sh`.

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 License

GPL-3.0. Android, trademarks and firmware belong to their owners.
