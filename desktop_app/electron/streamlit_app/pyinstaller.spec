# PyInstaller spec file for Fiber Maintenance Analytics Streamlit app
# This will bundle Python, Streamlit, and all dependencies into one executable

block_cipher = None

import sys
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('components') + collect_submodules('pages')

a = Analysis([
    'main.py',
],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('auth.py', '.'),
        ('data_loader.py', '.'),
        ('utils.py', '.'),
        ('components', 'components'),
        ('pages', 'pages'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='fiber_maintenance_analytics',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='fiber_maintenance_analytics'
)
