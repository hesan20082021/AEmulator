#!/usr/bin/env python3
"""把打完补丁的 classes.dex 装回 APK 并重签名。
保留其余条目的原始压缩属性；丢弃原 v2/v3 签名块（zipfile 重写即自动丢弃）。
"""
import zipfile, shutil, os, sys

BASE = "/sdcard/DSH_ai/VM/patch/work/base.apk"
NEWDEX = sys.argv[1] if len(sys.argv) > 1 else "/sdcard/DSH_ai/VM/patch/work/classes_patched.dex"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/sdcard/DSH_ai/VM/patch/out/app.aemu.0003-p1-unsigned.apk"

os.makedirs(os.path.dirname(OUT), exist_ok=True)
zin = zipfile.ZipFile(BASE)
zout = zipfile.ZipFile(OUT, "w")
replaced = 0
for zi in zin.infolist():
    if zi.filename == "classes.dex":
        data = open(NEWDEX, "rb").read()
        zi2 = zipfile.ZipInfo(zi.filename, date_time=zi.date_time)
        zi2.compress_type = zipfile.ZIP_DEFLATED
        zi2.external_attr = zi.external_attr
        zout.writestr(zi2, data)
        replaced += 1
    else:
        # 原样搬运（保持压缩方式与元数据，不解压不重压大文件）
        zi2 = zipfile.ZipInfo(zi.filename, date_time=zi.date_time)
        zi2.compress_type = zi.compress_type
        zi2.external_attr = zi.external_attr
        zi2.internal_attr = zi.internal_attr
        zi2.create_system = zi.create_system
        with zin.open(zi.filename) as f:
            zout.writestr(zi2, f.read())
zout.close(); zin.close()
print("entries copied, dex replaced x%d" % replaced)
print("size:", os.path.getsize(OUT))
