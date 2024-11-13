# -*- mode: python ; coding: utf-8 -*-
import platform
from dotenv import load_dotenv
import os

# read in settings.env
load_dotenv(dotenv_path="config.env")
app_name = os.environ.get('APP_NAME')


app_icon_path = None
if platform.system() == 'Darwin':
    app_icon_path = 'assets/app_logo.icns'
elif platform.system() == 'Windows':
    app_icon_path = 'assets/app_logo.ico'


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('config.env', '.')],
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
    [],
    exclude_binaries=True,
    name=app_name,
    icon=app_icon_path,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
app = BUNDLE(
    coll,
    name=f'{app_name}.app',
    icon=app_icon_path,
    bundle_identifier=None,
)
