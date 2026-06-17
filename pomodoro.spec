# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_all

datas = [
    ("assets/icon.png", "assets"),
    ("assets/icon.ico", "assets"),
]

# qtawesome (ícones Phosphor)
datas += collect_data_files("qtawesome")

# matplotlib — coleta dados, binários e imports ocultos de uma vez
mpl_datas, mpl_binaries, mpl_hidden = collect_all("matplotlib")
datas += mpl_datas

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=mpl_binaries,
    datas=datas,
    hiddenimports=mpl_hidden + [
        "PyQt6.QtSvg",
        "PyQt6.QtPrintSupport",
        "matplotlib.backends.backend_qtagg",
        "matplotlib.backends.backend_agg",
    ],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PomodoroAssistant",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon="assets/icon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="PomodoroAssistant",
)
