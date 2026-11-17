<div align="center">

<img src="../../docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**पुराने Android फ़र्मवेयर — HTC Sense, TouchWiz, MIUI, AOSP — आधुनिक फ़ोन पर। बिना root, बिना PC।**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](../../LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

[🇬🇧 English](../../README.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇩🇪 Deutsch](README.de.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇧🇷 Português](README.pt-BR.md) · [🇮🇹 Italiano](README.it.md) · [🇵🇱 Polski](README.pl.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇷 فارسی](README.fa.md) · **🇮🇳 हिन्दी** · [🇮🇩 Indonesia](README.id.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md)

</div>

---

AEmulator सीधे फ़र्मवेयर फ़ाइल से असली Android 2.3–17 सिस्टम बूट करता है: रिकवरी ZIP, Odin आर्काइव या Google फ़ैक्टरी इमेज या GSI। पुराने 32-बिट फ़र्मवेयर (2.3–4.4) संशोधित QEMU से चलते हैं, Android 5.0–17 सीधे फ़ोन के arm64 कोर पर चलता है; कर्नेल का binder एमुलेट होता है, ग्राफ़िक्स फ़ोन के GPU से और आवाज़ Android के ऑडियो सिस्टम से चलती है — सब कुछ एक सामान्य ऐप के भीतर।

## ✨ विशेषताएँ

- लगभग हर फ़ॉर्मेट आयात करें: CWM/TWRP ZIP, Samsung Odin `.tar.md5`, Google फ़ैक्टरी `.tgz`, `system.img`, OTA `system.new.dat.br`
- कंपनियों के स्किन जैसे हैं वैसे चलते हैं: HTC Sense, Samsung TouchWiz, MIUI, AOSP
- GL ब्रिज से हार्डवेयर ग्राफ़िक्स, आवाज़, टच और मल्टीटच, आधुनिक TLS प्रॉक्सी के साथ नेटवर्क
- APK, संगीत और फ़ोटो के लिए साझा मेमोरी कार्ड फ़ोल्डर
- 18 भाषाओं में Material 3 Expressive इंटरफ़ेस
- मुफ़्त और ओपन सोर्स (GPL-3.0)

## 🚀 जल्दी शुरुआत

1. [Releases](https://github.com/hesan20082021/AEmulator/releases) से APK डाउनलोड करके इंस्टॉल करें।
2. फ़र्मवेयर फ़ाइल फ़ोन पर डाउनलोड करें।
3. AEmulator खोलें → **फ़र्मवेयर जोड़ें** और फ़ाइल चुनें। आयात में कुछ मिनट लगते हैं।
4. **चलाएँ** दबाएँ। पहला बूट धीमा होता है: सिस्टम ऐप्स ऑप्टिमाइज़ करता है।
5. ⋮ मेनू में वॉल्यूम, पावर बटन और लॉग; ⚙️ से सेटिंग्स और भाषा।

## 📋 आवश्यकताएँ

- 64-बिट ARM फ़ोन (arm64-v8a) पर Android 8.0+
- प्रति फ़र्मवेयर लगभग 1–3 GB खाली जगह
- नया Snapdragon / Dimensity / Tensor सुझाया जाता है

## ⚙️ यह कैसे काम करता है

Android 2.3–4.4 पर हर गेस्ट प्रोसेस संशोधित यूज़र-मोड QEMU में चलता है; 5.0–17 पर फ़र्मवेयर के अपने arm64 प्रोग्राम सीधे चलते हैं, और हर Android संस्करण के लिए अलग इंजन कर्नेल उनके सिस्टम कॉल पकड़ता है। एक binder डेमन कर्नेल ड्राइवर की जगह लेता है, GL ब्रिज OpenGL ES कॉल GPU तक भेजता है, और छोटी गेस्ट लाइब्रेरी (ऑडियो HAL, audio policy रैपर, LD_PRELOAD शिम) निर्माताओं के कोड को एमुलेटर के अनुकूल बनाती हैं। इम्पोर्टर फ़र्मवेयर पढ़ता है, boot इमेज में init स्क्रिप्ट ढूँढता है और सेवाओं की शुरुआत की योजना बनाता है।

## 🛠️ सोर्स से बनाएँ

JDK 17, Android SDK 36 और NDK r28 चाहिए। गेस्ट लाइब्रेरी `native/*/build.sh` से बनती हैं।

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 लाइसेंस

GPL-3.0। Android, ट्रेडमार्क और फ़र्मवेयर उनके स्वामियों के हैं।
