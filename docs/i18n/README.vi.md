<div align="center">

<img src="../../docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**Firmware Android cổ điển — HTC Sense, TouchWiz, MIUI, AOSP — trên điện thoại hiện đại. Không root, không cần PC.**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](../../LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

[🇬🇧 English](../../README.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇩🇪 Deutsch](README.de.md) · [🇫🇷 Français](README.fr.md) · [🇪🇸 Español](README.es.md) · [🇧🇷 Português](README.pt-BR.md) · [🇮🇹 Italiano](README.it.md) · [🇵🇱 Polski](README.pl.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇷 فارسی](README.fa.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇮🇩 Indonesia](README.id.md) · **🇻🇳 Tiếng Việt** · [🇨🇳 简体中文](README.zh-CN.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md)

</div>

---

AEmulator khởi động một hệ thống Android 2.3–17 thật trực tiếp từ tệp firmware: ZIP recovery, gói Odin factory image của Google hoặc GSI. Firmware 32-bit cũ (2.3–4.4) chạy qua QEMU đã chỉnh sửa, Android 5.0–17 chạy trực tiếp trên các nhân arm64 của điện thoại; binder của nhân được giả lập, đồ họa dùng GPU điện thoại và âm thanh đi qua hệ thống âm thanh Android — tất cả trong một ứng dụng bình thường.

## ✨ Tính năng

- Nhập gần như mọi định dạng: ZIP CWM/TWRP, Odin `.tar.md5` của Samsung, factory `.tgz` của Google, `system.img`, OTA `system.new.dat.br`
- Giao diện hãng chạy nguyên bản: HTC Sense, Samsung TouchWiz, MIUI, AOSP
- Đồ họa phần cứng qua cầu GL, âm thanh, cảm ứng và đa điểm, mạng với proxy TLS hiện đại
- Thư mục thẻ nhớ dùng chung cho APK, nhạc và ảnh
- Giao diện Material 3 Expressive với 18 ngôn ngữ
- Miễn phí và mã nguồn mở (GPL-3.0)

## 🚀 Bắt đầu nhanh

1. Tải APK từ [Releases](https://github.com/hesan20082021/AEmulator/releases) và cài đặt.
2. Tải một tệp firmware về điện thoại.
3. Mở AEmulator → **Thêm firmware** và chọn tệp. Việc nhập mất vài phút.
4. Nhấn **Chạy**. Lần khởi động đầu chậm hơn: hệ thống tối ưu ứng dụng.
5. Menu ⋮ để chỉnh âm lượng, nút nguồn và nhật ký; ⚙️ mở cài đặt và ngôn ngữ.

## 📋 Yêu cầu

- Android 8.0+ trên điện thoại ARM 64-bit (arm64-v8a)
- Khoảng 1–3 GB trống cho mỗi firmware
- Nên dùng Snapdragon / Dimensity / Tensor đời mới

## ⚙️ Cách hoạt động

Trên Android 2.3–4.4 mỗi tiến trình khách chạy dưới QEMU chế độ người dùng đã chỉnh sửa; trên 5.0–17 các chương trình arm64 của firmware chạy trực tiếp, và một nhân động cơ riêng cho từng phiên bản Android bắt các lời gọi hệ thống của chúng. Một daemon binder thay cho driver nhân, cầu GL chuyển lệnh OpenGL ES tới GPU và các thư viện khách nhỏ (HAL âm thanh, lớp bọc audio policy, shim LD_PRELOAD) điều chỉnh mã của hãng cho hợp với trình giả lập. Trình nhập đọc firmware, tìm script init trong image boot và lập kế hoạch khởi động dịch vụ.

## 🛠️ Biên dịch từ mã nguồn

Cần JDK 17, Android SDK 36 và NDK r28. Thư viện khách được dựng bằng `native/*/build.sh`.

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 Giấy phép

GPL-3.0. Android, nhãn hiệu và firmware thuộc về chủ sở hữu.
