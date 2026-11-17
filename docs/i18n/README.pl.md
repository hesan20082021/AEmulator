<div align="center">

<img src="../../docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**Klasyczne firmware Androida — HTC Sense, TouchWiz, MIUI, AOSP — na nowoczesnym telefonie. Bez roota, bez PC.**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](../../LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

[🇬🇧 English](../../README.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇩🇪 Deutsch](README.de.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇧🇷 Português](README.pt-BR.md) · [🇮🇹 Italiano](README.it.md) · **🇵🇱 Polski** · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇷 فارسی](README.fa.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇮🇩 Indonesia](README.id.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md)

</div>

---

AEmulator uruchamia prawdziwy system Android 2.3–17 prosto z pliku firmware: ZIP do recovery, archiwum Odin lub obraz fabryczny Google albo GSI. Stare 32-bitowe firmware (2.3–4.4) działa przez zmodyfikowane QEMU, Android 5.0–17 natywnie na rdzeniach arm64 telefonu; binder jądra jest emulowany, grafika korzysta z GPU telefonu, a dźwięk z systemu audio Androida — wszystko w zwykłej aplikacji.

## ✨ Funkcje

- Import niemal każdego formatu: ZIP CWM/TWRP, Odin `.tar.md5` Samsunga, obraz fabryczny Google `.tgz`, `system.img`, OTA `system.new.dat.br`
- Nakładki producentów działają bez zmian: HTC Sense, Samsung TouchWiz, MIUI, AOSP
- Sprzętowa grafika przez mostek GL, dźwięk, dotyk i multitouch, sieć z nowoczesnym proxy TLS
- Wspólny folder karty pamięci na APK, muzykę i zdjęcia
- Interfejs Material 3 Expressive w 18 językach
- Za darmo i open source (GPL-3.0)

## 🚀 Szybki start

1. Pobierz APK z [Releases](https://github.com/hesan20082021/AEmulator/releases) i zainstaluj.
2. Pobierz plik firmware na telefon.
3. Otwórz AEmulator → **Dodaj firmware** i wybierz plik. Import trwa kilka minut.
4. Naciśnij **Uruchom**. Pierwszy start trwa dłużej: system optymalizuje aplikacje.
5. Menu ⋮ — głośność, przycisk zasilania i dziennik; ⚙️ — ustawienia i język.

## 📋 Wymagania

- Android 8.0+ na 64-bitowym telefonie ARM (arm64-v8a)
- Około 1–3 GB wolnego miejsca na firmware
- Zalecany nowy Snapdragon / Dimensity / Tensor

## ⚙️ Jak to działa

Na Androidzie 2.3–4.4 każdy proces gościa działa pod zmodyfikowanym QEMU w trybie użytkownika; na 5.0–17 programy arm64 z firmware działają natywnie, a ich wywołania systemowe przechwytuje osobne jądro silnika dla każdej wersji Androida. Demon binder zastępuje sterownik jądra, mostek GL przekazuje wywołania OpenGL ES do GPU, a małe biblioteki gościa (HAL audio, nakładka audio policy, shim LD_PRELOAD) dopasowują kod producentów do emulatora. Importer czyta firmware, znajduje skrypty init w obrazie boot i tworzy plan startu usług.

## 🛠️ Budowanie ze źródeł

Potrzebne są JDK 17, Android SDK 36 i NDK r28. Biblioteki gościa buduje się skryptami `native/*/build.sh`.

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 Licencja

GPL-3.0. Android, znaki towarowe i firmware należą do ich właścicieli.
