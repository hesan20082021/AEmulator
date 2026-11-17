<div dir="rtl">

<div align="center">

<img src="../../docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**فرم‌ویرهای کلاسیک اندروید — HTC Sense، TouchWiz، MIUI، AOSP — روی گوشی مدرن. بدون روت و بدون رایانه.**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](../../LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

[🇬🇧 English](../../README.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇩🇪 Deutsch](README.de.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇧🇷 Português](README.pt-BR.md) · [🇮🇹 Italiano](README.it.md) · [🇵🇱 Polski](README.pl.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · **🇮🇷 فارسی** · [🇮🇳 हिन्दी](README.hi.md) · [🇮🇩 Indonesia](README.id.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md)

</div>

---

AEmulator یک سیستم واقعی اندروید 2.3 تا 17 را مستقیم از فایل فرم‌ویر بوت می‌کند: ZIP ریکاوری، آرشیو Odin یا ایمیج کارخانهٔ گوگل یا GSI. فرم‌ویرهای قدیمی ۳۲ بیتی (2.3 تا 4.4) با QEMU اصلاح‌شده اجرا می‌شوند و اندروید 5.0 تا 17 مستقیم روی هسته‌های arm64 گوشی اجرا می‌شود؛ binder هسته شبیه‌سازی می‌شود، گرافیک با GPU گوشی و صدا با سامانهٔ صوتی اندروید پخش می‌شود — همه درون یک برنامهٔ معمولی.

## ✨ ویژگی‌ها

- درون‌ریزی تقریباً همهٔ قالب‌ها: ‏ZIP ‏CWM/TWRP، ‏Odin ‏`.tar.md5` سامسونگ، ایمیج کارخانهٔ گوگل ‏`.tgz`، ‏`system.img`، ‏OTA ‏`system.new.dat.br`
- رابط‌های سازندگان همان‌طور که هستند کار می‌کنند: HTC Sense، Samsung TouchWiz، MIUI، AOSP
- گرافیک سخت‌افزاری از طریق پل GL، صدا، لمس و چندلمسی، شبکه با پراکسی TLS مدرن
- پوشهٔ مشترک کارت حافظه برای APK، موسیقی و عکس
- رابط Material 3 Expressive به 18 زبان
- رایگان و متن‌باز (GPL-3.0)

## 🚀 شروع سریع

1. فایل APK را از [Releases](https://github.com/hesan20082021/AEmulator/releases) دانلود و نصب کنید.
2. یک فایل فرم‌ویر را روی گوشی دانلود کنید.
3. AEmulator را باز کنید ← **افزودن فرم‌ویر** و فایل را انتخاب کنید. درون‌ریزی چند دقیقه طول می‌کشد.
4. **اجرا** را بزنید. بوت اول کندتر است: سیستم برنامه‌ها را بهینه می‌کند.
5. منوی ⋮ برای صدا، دکمهٔ پاور و گزارش؛ دکمهٔ ⚙️ برای تنظیمات و زبان.

## 📋 نیازمندی‌ها

- اندروید 8.0+ روی گوشی ARM ‏64 بیتی (arm64-v8a)
- حدود 1 تا 3 گیگابایت فضای آزاد برای هر فرم‌ویر
- پیشنهاد: Snapdragon / Dimensity / Tensor جدید

## ⚙️ چگونه کار می‌کند

در اندروید 2.3 تا 4.4 هر فرایند مهمان زیر یک QEMU اصلاح‌شده در حالت کاربر اجرا می‌شود؛ در 5.0 تا 17 برنامه‌های arm64 خود فرم‌ویر مستقیم اجرا می‌شوند و یک هستهٔ موتور جداگانه برای هر نسخهٔ اندروید فراخوانی‌های سیستمی آن‌ها را می‌گیرد. سرویس binder جای درایور هسته را می‌گیرد، پل GL فراخوانی‌های OpenGL ES را به GPU می‌فرستد و کتابخانه‌های کوچک مهمان (HAL صوتی، پوشش audio policy، لایهٔ LD_PRELOAD) کد سازندگان را با شبیه‌ساز سازگار می‌کنند. درون‌ریز فرم‌ویر را می‌خواند، اسکریپت‌های init را در ایمیج boot پیدا می‌کند و برنامهٔ اجرای سرویس‌ها را می‌سازد.

## 🛠️ ساخت از کد منبع

به JDK 17، Android SDK 36 و NDK r28 نیاز دارید. کتابخانه‌های مهمان با `native/*/build.sh` ساخته می‌شوند.

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 مجوز

GPL-3.0. اندروید، نشان‌های تجاری و فرم‌ویرها متعلق به صاحبانشان‌اند.

</div>
