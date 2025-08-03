# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['bot_ui.py'],
    pathex=[],
    binaries=[],
    datas=[('ittifak', 'ittifak'), ('anaekran', 'anaekran'), ('dunyaheal', 'dunyaheal'), ('heal', 'heal'), ('kutu', 'kutu'), ('anahtar', 'anahtar'), ('asker', 'asker'), ('bekcikulesi', 'bekcikulesi'), ('geri', 'geri'), ('mesaj', 'mesaj'), ('savas', 'savas'), ('suadasi', 'suadasi'), ('askerbas', 'askerbas')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='bot_ui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app_icon.ico'],
)
