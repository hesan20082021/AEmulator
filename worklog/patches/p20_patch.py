import io, re, sys

TF = "/root/apkx/p19smali/app/aemu/core/TreeFixer.smali"
GV = "/root/apkx/p19smali/app/aemu/core/GuestVm.smali"

src = io.open(TF, encoding="utf-8").read()

a = '''    const/4 v12, 0x2

    .line 647
    new-array v0, v12, [Ljava/lang/String;

    const-string/jumbo v3, "system/etc/permissions"

    const/16 v21, 0x0

    aput-object v3, v0, v21

    const-string/jumbo v3, "vendor/etc/permissions"

    const/16 v17, 0x1

    aput-object v3, v0, v17
'''
assert src.count(a) == 1, src.count(a)

dirs = [
    "system/etc/permissions",
    "vendor/etc/permissions",
    "odm/etc/permissions",
    "product/etc/permissions",
    "system_ext/etc/permissions",
    "system/product/etc/permissions",
    "system/system_ext/etc/permissions",
    "my_product/etc/permissions",
    "my_stock/etc/permissions",
    "my_bigball/etc/permissions",
    "my_heytap/etc/permissions",
    "my_engineering/etc/permissions",
    "my_region/etc/permissions",
    "my_carrier/etc/permissions",
    "my_manifest/etc/permissions",
]

parts = ["    const/16 v12, 0x%x" % len(dirs), "", "    .line 647", "    new-array v0, v12, [Ljava/lang/String;", ""]
for i, d in enumerate(dirs):
    parts += ['    const-string/jumbo v3, "%s"' % d, "", "    const/16 v21, 0x%x" % i, "", "    aput-object v3, v0, v21", ""]
b = "\n".join(parts)
src = src.replace(a, b)
patched = ["TreeFixer: permission roots x%d" % len(dirs)]

io.open(TF, "w", encoding="utf-8").write(src)

gv = io.open(GV, encoding="utf-8").read()
assert "dumpAnrLogs" not in gv
method = '''
.method public final dumpAnrLogs()Ljava/lang/String;
    .locals 6

    :try_start_0
    const-string/jumbo v0, "ls -l /data/anr 2>/dev/null; cat /data/anr/* 2>/dev/null; echo ==== tombstones; ls -l /data/tombstones 2>/dev/null"

    const-wide/16 v1, 0x7530

    invoke-virtual {p0, v0, v1, v2}, Lapp/aemu/core/GuestVm;->guestShell(Ljava/lang/String;J)Ljava/lang/String;

    move-result-object v0

    return-object v0
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    move-exception v0

    const-string v0, "anr: unavailable"

    return-object v0

    :catch_0
    move-exception v0

    const-string v0, "anr: unavailable"

    return-object v0
.end method
'''
# unreachable move-exception before try_end is invalid; build a clean version instead
method = '''
.method public final dumpAnrLogs()Ljava/lang/String;
    .locals 6

    :try_start_0
    const-string/jumbo v0, "ls -l /data/anr 2>/dev/null; cat /data/anr/* 2>/dev/null; echo ==== tombstones; ls -l /data/tombstones 2>/dev/null"

    const-wide/16 v1, 0x7530

    invoke-virtual {p0, v0, v1, v2}, Lapp/aemu/core/GuestVm;->guestShell(Ljava/lang/String;J)Ljava/lang/String;

    move-result-object v0
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    return-object v0

    :catch_0
    move-exception v0

    const-string v0, "anr: unavailable"

    return-object v0
.end method
'''
gv = gv + method
io.open(GV, "w", encoding="utf-8").write(gv)
patched.append("GuestVm: +dumpAnrLogs()")

print("\n".join(patched))
