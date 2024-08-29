# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, copy_metadata
import os

# Define paths
path_to_program = os.path.abspath(".")
path_to_libraries = "C:\\Users\\Colifast\\anaconda3\\envs\\colifast\\"

a = Analysis(
    ['Colifast_ALARM_manager.py'],
    pathex=[],  # Set pathex if needed for module searching
    binaries=[
        (os.path.join(path_to_libraries, 'python.exe'), '.'),  # Python binary
    ],
    datas=[
        (os.path.join(path_to_program, 'python_designer_files'), 'python_designer_files'),
        (os.path.join(path_to_program, 'components'), 'components'),
        (os.path.join(path_to_program, 'Images'), 'Images'),
        (os.path.join(path_to_program, 'icons'), 'icons'),
        (os.path.join(path_to_program, 'Styles'), 'Styles'),
        (os.path.join(path_to_program, '__init__.py'), '.'),
        (os.path.join(path_to_program, 'method_helper.py'), '.'),
        (os.path.join(path_to_program, 'PumpCommServer.dll'), '.'),
        (os.path.join(path_to_program, 'settings.py'), '.'),
        (os.path.join(path_to_program, 'resource_path.py'), '.'),
        (os.path.join(path_to_program, 'Icons_rc.py'), '.'),
        (os.path.join(path_to_program, 'Colifast_ALARM_manager.py'), '.'),
        (os.path.join(path_to_libraries, 'Lib', 'site-packages', 'seabreeze'), 'seabreeze'),
        (os.path.join(path_to_program, 'AduHid64.dll'), '.'),
        (os.path.join(path_to_program, 'AduHid.dll'), '.'),
        (os.path.join(path_to_program, 'run_seabreeze_setup.bat'), '.'),
        (os.path.join(path_to_program, 'manual.md'), '.'),
        (os.path.join(sys.exec_prefix, 'Lib'), 'Lib'),

        # Include any additional directories or files necessary
    ],
    hiddenimports=[
        'serial', 'seabreeze', 'seabreeze.spectrometers',
        'seabreeze.os_setup', 'PyQt5.Qsci', 'PyQt5', 'Colifast_ALARM_manager', 
        'Colifast_ALARM_manager.TimeSelectorDialog', 'Colifast_ALARM_manager.PDFReport',
        'Colifast_ALARM_manager.LogIn', 'Colifast_ALARM_manager.SFMadv',
        'Colifast_ALARM_manager.LiquidHandling','Colifast_ALARM_manager.AD', 
        'python_designer_files.ADUadv', 'python_designer_files.ADUadv_generator.ADUadv', 
        'python_designer_files.ADUadv_generator', 'python_designer_files.editor'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    console=True, 
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ColifastALARM',  # The name of the executable
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for a GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=False,  # Set onefile to False to ensure separate files
    icon='icon.ico',  # Specify your icon file if applicable
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ColifastALARM',
    dir="."  # Place output files in the same directory as the executable
)
