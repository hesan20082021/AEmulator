#!/usr/bin/env python3
"""从 data.py + texts.py 生成 README.md（英文）和 docs/i18n/README.<code>.md。
在仓库根目录运行：python docs/readme/gen.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from data import *  # noqa
from texts import T  # noqa

RTL = {"ar", "fa"}


def path_of(code, from_code):
    """从 from_code 语言文件指向 code 语言 README 的相对链接。"""
    if code == "en":
        return "README.md" if from_code == "en" else "../../README.md"
    return f"docs/i18n/README.{code}.md" if from_code == "en" else f"README.{code}.md"


def render(code):
    t = T[code]
    up = "" if code == "en" else "../../"
    L = []
    if code in RTL:
        L.append('<div dir="rtl">\n')
    L.append('<div align="center">\n')
    L.append(f'<img src="{up}docs/assets/logo.png" width="128" alt="AEmulator logo"/>\n')
    L.append("# AEmulator\n")
    L.append(f"**{t['tagline']}**\n")
    L.append(
        f'[![Version](https://img.shields.io/badge/version-{VERSION}-3D5AFE?style=for-the-badge)]({REPO}/releases) '
        f'[![License](https://img.shields.io/badge/license-GPL--3.0-3D5AFE?style=for-the-badge)]({up}LICENSE) '
        f'[![Android](https://img.shields.io/badge/Android-8.0%2B-3DDC84?style=for-the-badge&logo=android&logoColor=white)]({REPO})\n')
    L.append(" · ".join(
        (f"**{flag} {name}**" if c == code else f"[{flag} {name}]({path_of(c, code)})") for c, name, flag in LANGS) + "\n")
    L.append("</div>\n")
    L.append("---\n")
    L.append(t["about"] + "\n")
    L.append(f"## ✨ {t['feat_title']}\n")
    L += [f"- {f}" for f in t["feats"]]
    L.append("")
    L.append(f"## 🚀 {t['start_title']}\n")
    L += [f"{i + 1}. {s.format(repo=REPO)}" for i, s in enumerate(t["steps"])]
    L.append("")
    L.append(f"## 📋 {t['req_title']}\n")
    L += [f"- {r}" for r in t["reqs"]]
    L.append("")
    L.append(f"## ⚙️ {t['how_title']}\n")
    L.append(t["how_text"] + "\n")
    L.append(f"## 🛠️ {t['build_title']}\n")
    L.append(t["build_text"] + "\n")
    L.append(f"```bash\ngit clone {REPO}.git\ncd AEmulator\n./gradlew assembleRelease\n```\n")
    L.append(f"## 📄 {t['license_title']}\n")
    L.append(t["license_text"] + "\n")
    if code in RTL:
        L.append("</div>\n")
    return "\n".join(L)


def main():
    for code, _, _ in LANGS:
        assert code in T, code
        out = os.path.join(ROOT, "README.md") if code == "en" else os.path.join(ROOT, "docs", "i18n", f"README.{code}.md")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(render(code))
    print(f"README: {len(LANGS)} 种语言")


if __name__ == "__main__":
    main()
