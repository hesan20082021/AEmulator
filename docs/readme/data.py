# README 数据来自 site/config.js —— 站点与 GitHub 使用同一来源。
# 各语言文本在 texts.py。
import json, os

_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "site", "config.js")
_src = open(_cfg_path, encoding="utf-8").read()
_cfg = json.loads(_src[_src.index("window.AEMU_CONFIG =") + len("window.AEMU_CONFIG ="):].strip().rstrip(";"))

VERSION = _cfg["version"]
REPO = _cfg["links"]["repo"]

LANGS = [  # 代码、自称、旗帜
    ("en", "English", "🇬🇧"), ("ru", "Русский", "🇷🇺"), ("uk", "Українська", "🇺🇦"), ("de", "Deutsch", "🇩🇪"),
    ("fr", "Français", "🇫🇷"), ("es", "Español", "🇪🇸"), ("pt-BR", "Português", "🇧🇷"), ("it", "Italiano", "🇮🇹"),
    ("pl", "Polski", "🇵🇱"), ("tr", "Türkçe", "🇹🇷"), ("ar", "العربية", "🇸🇦"), ("fa", "فارسی", "🇮🇷"),
    ("hi", "हिन्दी", "🇮🇳"), ("id", "Indonesia", "🇮🇩"), ("vi", "Tiếng Việt", "🇻🇳"), ("zh-CN", "简体中文", "🇨🇳"),
    ("ja", "日本語", "🇯🇵"), ("ko", "한국어", "🇰🇷"),
]
