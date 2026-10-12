# -*- mode: python ; coding: utf-8 -*-
"""
project.spec — шаблон сборки exe через PyInstaller (onedir).

ВАЖНО: перед использованием скопируй этот файл под своим именем
и замени плейсхолдер <ProjectName> на имя проекта.

    Пример: MyApp.spec
        - имя файла:  MyApp.spec
        - в EXE:      name="MyApp"
        - в COLLECT:  name="MyApp"
        - в build.bat: set PROJECT_NAME=MyApp

Использование:
    pyinstaller MyApp.spec --clean --noconfirm
Результат:
    dist/MyApp/MyApp.exe   (onedir-режим, портативно)

Папка dist/MyApp/ переносится целиком на другой компьютер.
Папка данных создаётся приложением при первом запуске (рядом с exe
или в любом другом месте — решает само приложение).
"""
import sys
from pathlib import Path

# Корень проекта = папка, где лежит этот spec
ROOT = Path(SPECPATH).resolve()

# ---------------------------------------------------------------
# 1. Что пакуем с собой (datas)
#    Ключ — папка/файл в проекте; значение — путь внутри сборки.
# ---------------------------------------------------------------
datas = [
    (str(ROOT / "assets"), "assets"),
    (str(ROOT / "config.json"), "."),          # опционально
]

# Если в проекте есть заводские шаблоны/справочники — добавь:
# datas.append((str(ROOT / "templates"), "templates"))
# datas.append((str(ROOT / "references"), "references"))

# PDF-инструкция: включаем, только если она сгенерирована.
_manual_pdf = ROOT / "project_info" / "manuals" / "USER_MANUAL.pdf"
if _manual_pdf.exists():
    datas.append((str(_manual_pdf), "project_info/manuals"))
    print(f"📄 Инструкция включена: {_manual_pdf}")
else:
    print("⚠️ USER_MANUAL.pdf не найден — не включаем в сборку. "
          "Сначала: python service/docs/make_docs.py")

# ---------------------------------------------------------------
# 2. Скрытые импорты (то, что PyInstaller не видит)
#    Раскомментируй нужные.
# ---------------------------------------------------------------
hiddenimports = [
    # "win32com", "win32com.client", "pythoncom",   # Word через COM
    # "docx",                                        # python-docx
    # "openpyxl",                                    # xlsx
    # "PIL",                                         # Pillow
]

# ---------------------------------------------------------------
# 3. Что точно не нужно в сборке
# ---------------------------------------------------------------
excludes = [
    "matplotlib", "scipy", "pandas",
    "PyQt5", "PyQt6", "PySide2",                     # только PySide6, если GUI
    "tkinter", "test", "unittest",
]

# ---------------------------------------------------------------
# 4. Точка входа
#    Если main.py отсутствует — замени на свой файл.
# ---------------------------------------------------------------
entry_script = str(ROOT / "main.py")

a = Analysis(
    [entry_script],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    # ↓ ЗАМЕНИ <ProjectName> на имя проекта (например "MyApp")
    name="<ProjectName>",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                       # UPX отключён — с Qt бывают глюки
    console=False,                   # GUI без окна консоли; для CLI: True
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Иконка: если файла нет — сборка не упадёт.
    icon=[str(ROOT / "assets" / "icons" / "project_logo.ico")]
         if (ROOT / "assets" / "icons" / "project_logo.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    # ↓ ЗАМЕНИ <ProjectName> на имя проекта (то же, что в EXE выше)
    name="<ProjectName>",
)