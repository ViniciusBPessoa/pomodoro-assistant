# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [
    ("assets/sons",  "assets/sons"),
    ("assets/icon.png", "assets"),
    ("assets/icon.ico", "assets"),
]
# Fontes e dados do qtawesome (ícones Phosphor) — obrigatório incluir
datas += collect_data_files("qtawesome")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "PyQt6.QtSvg",
        "PyQt6.QtPrintSupport",
    ],
    excludes=["tkinter", "unittest", "email", "html", "http", "urllib", "xml"],
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
