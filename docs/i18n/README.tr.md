<div align="center">

<img src="../../docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**Klasik Android yazılımları — HTC Sense, TouchWiz, MIUI, AOSP — modern bir telefonda. Root ve PC gerekmez.**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](../../LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

[🇬🇧 English](../../README.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇩🇪 Deutsch](README.de.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇧🇷 Português](README.pt-BR.md) · [🇮🇹 Italiano](README.it.md) · [🇵🇱 Polski](README.pl.md) · **🇹🇷 Türkçe** · [🇸🇦 العربية](README.ar.md) · [🇮🇷 فارسی](README.fa.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇮🇩 Indonesia](README.id.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md)

</div>

---

AEmulator gerçek bir Android 2.3–17 sistemini doğrudan yazılım dosyasından başlatır: recovery ZIP, Odin arşivi veya Google fabrika imajı veya GSI. Eski 32 bit yazılımlar (2.3–4.4) değiştirilmiş QEMU ile çevrilir, Android 5.0–17 telefonun arm64 çekirdeklerinde doğrudan çalışır; çekirdeğin binder’ı taklit edilir, grafikler telefonun GPU’sunu, ses Android’in ses altyapısını kullanır — hepsi sıradan bir uygulamanın içinde.

## ✨ Özellikler

- Neredeyse her biçimi içe aktarma: CWM/TWRP ZIP, Samsung Odin `.tar.md5`, Google fabrika `.tgz`, `system.img`, OTA `system.new.dat.br`
- Üretici arayüzleri olduğu gibi çalışır: HTC Sense, Samsung TouchWiz, MIUI, AOSP
- GL köprüsüyle donanım grafikleri, ses, dokunma ve çoklu dokunma, modern TLS vekilli ağ
- APK, müzik ve fotoğraflar için ortak hafıza kartı klasörü
- 18 dilde Material 3 Expressive arayüz
- Ücretsiz ve açık kaynak (GPL-3.0)

## 🚀 Hızlı başlangıç

1. APK’yı [Releases](https://github.com/hesan20082021/AEmulator/releases) sayfasından indirip kurun.
2. Telefonuna bir yazılım dosyası indir.
3. AEmulator’ı açın → **Yazılım ekle** ve dosyayı seçin. İçe aktarma birkaç dakika sürer.
4. **Başlat**’a basın. İlk açılış daha uzundur: sistem uygulamaları optimize eder.
5. ⋮ menüsü: ses, güç düğmesi ve günlük; ⚙️ ayarları ve dili açar.

## 📋 Gereksinimler

- 64 bit ARM telefonda Android 8.0+ (arm64-v8a)
- Yazılım başına yaklaşık 1–3 GB boş alan
- Önerilen: yeni bir Snapdragon / Dimensity / Tensor

## ⚙️ Nasıl çalışır

Android 2.3–4.4’te her misafir süreç değiştirilmiş kullanıcı kipi QEMU altında çalışır; 5.0–17’de yazılımın arm64 programları doğrudan çalışır ve her Android sürümü için ayrı bir motor çekirdeği sistem çağrılarını yakalar. Bir binder arka plan programı çekirdek sürücüsünün yerini alır, GL köprüsü OpenGL ES çağrılarını GPU’ya iletir, küçük misafir kütüphaneleri (ses HAL’i, audio policy sarmalayıcısı, LD_PRELOAD katmanı) üretici kodunu emülatöre uyarlar. İçe aktarıcı yazılımı okur, boot imajındaki init betiklerini bulur ve servislerin başlama planını kurar.

## 🛠️ Kaynaktan derleme

JDK 17, Android SDK 36 ve NDK r28 gerekir. Misafir kütüphaneleri `native/*/build.sh` betikleriyle derlenir.

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 Lisans

GPL-3.0. Android, markalar ve yazılımlar sahiplerine aittir.
