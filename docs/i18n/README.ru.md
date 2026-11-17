<div align="center">

<img src="../../docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**Старые прошивки Android — HTC Sense, TouchWiz, MIUI, AOSP — на современном телефоне. Без root и без ПК.**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](../../LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

[🇬🇧 English](../../README.md) · **🇷🇺 Русский** · [🇺🇦 Українська](README.uk.md) · [🇩🇪 Deutsch](README.de.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇧🇷 Português](README.pt-BR.md) · [🇮🇹 Italiano](README.it.md) · [🇵🇱 Polski](README.pl.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇷 فارسی](README.fa.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇮🇩 Indonesia](README.id.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md)

</div>

---

AEmulator загружает настоящую систему Android 2.3–17 прямо из файла прошивки: ZIP для рекавери, архива Odin или factory-образа Google, а также GSI. Старые 32-битные прошивки (2.3–4.4) идут через доработанный QEMU, Android 5.0–17 — нативно на arm64-ядрах телефона. Binder ядра эмулируется, графика идёт через GPU телефона, звук — через аудиосистему Android. Всё работает внутри обычного приложения.

## ✨ Возможности

- Импорт почти любых форматов: ZIP для CWM/TWRP, Odin `.tar.md5` от Samsung, factory `.tgz` от Google, `system.img`, OTA `system.new.dat.br`
- Оболочки производителей работают как есть: HTC Sense, Samsung TouchWiz, MIUI, AOSP
- Аппаратная графика через GL-мост, звук, касания и мультитач, сеть с современным TLS-прокси
- Общая папка «карты памяти» для APK, музыки и фото
- Интерфейс Material 3 Expressive на 18 языках
- Бесплатно и с открытым кодом (GPL-3.0)

## 🚀 Быстрый старт

1. Скачайте APK из [Releases](https://github.com/hesan20082021/AEmulator/releases) и установите.
2. Скачайте файл прошивки на телефон.
3. Откройте AEmulator → **Добавить прошивку** и выберите файл. Импорт занимает несколько минут.
4. Нажмите **Запустить**. Первая загрузка дольше: система оптимизирует приложения.
5. Меню ⋮ — громкость, кнопка питания и журнал; кнопка ⚙️ — настройки приложения и язык.

## 📋 Требования

- Android 8.0+ на 64-битном ARM-телефоне (arm64-v8a)
- Около 1–3 ГБ свободного места на прошивку
- Рекомендуется современный Snapdragon / Dimensity / Tensor

## ⚙️ Как это устроено

На Android 2.3–4.4 каждый процесс гостя работает под доработанным QEMU в режиме пользователя; на 5.0–17 собственные arm64-программы прошивки работают напрямую, а их системные вызовы перехватывает отдельное ядро движка для каждой версии Android. Демон binder заменяет драйвер ядра, GL-мост передаёт вызовы OpenGL ES на GPU телефона, а небольшие гостевые библиотеки (звуковой HAL, обёртка audio policy, прослойка LD_PRELOAD) подгоняют код производителей под эмулятор. Импортёр читает прошивку, находит init-скрипты в boot-образе и строит план запуска системных служб.

## 🛠️ Сборка из исходников

Нужны JDK 17, Android SDK 36 и NDK r28. Гостевые библиотеки собираются скриптами `native/*/build.sh`.

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 Лицензия

GPL-3.0. Android, товарные знаки и прошивки принадлежат их владельцам.
