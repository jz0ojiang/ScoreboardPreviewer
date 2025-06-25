# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/index.html', 'src'),
        ('src/assets/alpine.js', 'src/assets'),
        ('src/assets/style.css', 'src/assets'),
        ('src/assets/icon.ico', 'src/assets'),
        ('parser', 'parser'),
    ],
    hiddenimports=[
        'parser',
        'parser.scoreboard_parser',
        'parser.version_parsers',
        'nbtlib',
        'webview',
    ],
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
    name='ScoreboardPreviewer',
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
    icon=['src\\assets\\icon.ico'],
)
