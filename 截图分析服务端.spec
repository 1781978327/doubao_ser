# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # 1. 添加数据文件（本地目录和配置文件）
    datas=[
        ('received_screenshots', 'received_screenshots'),  # 截图目录
        ('config.py', '.'),  # 配置文件
        ('image_server.py', '.')  # 关键补充：包含 image_server.py
    ],
    # 2. 补充隐藏导入（自定义模块和可能遗漏的依赖）
    hiddenimports=[
        'watchdog.observers', 
        'watchdog.events', 
        'PyQt5.QtWidgets', 
        'PyQt5.QtCore', 
        'PyQt5.QtGui', 
        'openai',
        'pybase64',
        'markdown',
        # 补充你的自定义模块
        'ai_handler',
        'monitor_handler',
        'ui_components',
        'image_server',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='截图分析服务端',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 保持控制台模式，方便查看报错
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)