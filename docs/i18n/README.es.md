<div align="center">

<img src="../../docs/assets/logo.png" width="128" alt="AEmulator logo"/>

# AEmulator

**Firmware clásico de Android — HTC Sense, TouchWiz, MIUI, AOSP — en un teléfono moderno. Sin root, sin PC.**

[![Version](https://img.shields.io/badge/version-0.0.0.3-3D5AFE?style=for-the-badge)](https://github.com/hesan20082021/AEmulator/releases) [![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)](../../LICENSE) [![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://github.com/hesan20082021/AEmulator)

[🇬🇧 English](../../README.md) · [🇷🇺 Русский](README.ru.md) · [🇺🇦 Українська](README.uk.md) · [🇩🇪 Deutsch](README.de.md) · [🇫🇷 Français](README.fr.md) · **🇪🇸 Español** · [🇧🇷 Português](README.pt-BR.md) · [🇮🇹 Italiano](README.it.md) · [🇵🇱 Polski](README.pl.md) · [🇹🇷 Türkçe](README.tr.md) · [🇸🇦 العربية](README.ar.md) · [🇮🇷 فارسی](README.fa.md) · [🇮🇳 हिन्दी](README.hi.md) · [🇮🇩 Indonesia](README.id.md) · [🇻🇳 Tiếng Việt](README.vi.md) · [🇨🇳 简体中文](README.zh-CN.md) · [🇯🇵 日本語](README.ja.md) · [🇰🇷 한국어](README.ko.md)

</div>

---

AEmulator arranca un sistema Android 2.3–17 real directamente desde un archivo de firmware: ZIP de recovery, archivo de Odin o imagen de fábrica de Google o GSI. El firmware antiguo de 32 bits (2.3–4.4) se traduce con un QEMU modificado, Android 5.0–17 se ejecuta de forma nativa en los núcleos arm64 del teléfono; el binder del kernel se emula, los gráficos usan la GPU del teléfono y el sonido pasa por la pila de audio de Android — todo dentro de una app normal.

## ✨ Características

- Importa casi cualquier formato: ZIP CWM/TWRP, Odin `.tar.md5` de Samsung, imagen de fábrica `.tgz` de Google, `system.img`, OTA `system.new.dat.br`
- Las capas de los fabricantes funcionan tal cual: HTC Sense, Samsung TouchWiz, MIUI, AOSP
- Gráficos por hardware con el puente GL, sonido, táctil y multitáctil, red con proxy TLS moderno
- Carpeta compartida de tarjeta de memoria para APK, música y fotos
- Interfaz Material 3 Expressive en 18 idiomas
- Gratis y de código abierto (GPL-3.0)

## 🚀 Inicio rápido

1. Descarga el APK desde [Releases](https://github.com/hesan20082021/AEmulator/releases) e instálalo.
2. Descarga un archivo de firmware en el teléfono.
3. Abre AEmulator → **Añadir firmware** y elige el archivo. La importación tarda unos minutos.
4. Pulsa **Iniciar**. El primer arranque es más lento: el sistema optimiza las apps.
5. Menú ⋮ para volumen, botón de encendido y registro; ⚙️ abre ajustes e idioma.

## 📋 Requisitos

- Android 8.0+ en un teléfono ARM de 64 bits (arm64-v8a)
- Unos 1–3 GB libres por firmware
- Se recomienda un Snapdragon / Dimensity / Tensor reciente

## ⚙️ Cómo funciona

En Android 2.3–4.4 cada proceso invitado se ejecuta con un QEMU de modo usuario modificado; en 5.0–17 los programas arm64 del firmware se ejecutan de forma nativa y un núcleo del motor propio para cada versión de Android intercepta sus llamadas al sistema. Un demonio binder sustituye al controlador del kernel, un puente GL envía las llamadas OpenGL ES a la GPU y pequeñas bibliotecas invitadas (HAL de audio, envoltorio de audio policy, shim LD_PRELOAD) adaptan el código del fabricante al emulador. El importador lee el firmware, encuentra los scripts init en la imagen boot y crea el plan de arranque de los servicios.

## 🛠️ Compilar desde el código

Necesitas JDK 17, Android SDK 36 y NDK r28. Las bibliotecas del invitado se compilan con `native/*/build.sh`.

```bash
git clone https://github.com/hesan20082021/AEmulator.git
cd AEmulator
./gradlew assembleRelease
```

## 📄 Licencia

GPL-3.0. Android, las marcas y el firmware pertenecen a sus dueños.
