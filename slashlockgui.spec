# -*- mode: python -*-

try:
    from kivy.deps import sdl2, glew
except ImportError:
    pass

block_cipher = None


a = Analysis(['slashlockgui/gui.py'],
             pathex=['./slashlockgui'],
             binaries=None,
             datas=[('slashlockgui/kvs/*.kv', 'kvs')],
             hiddenimports=['cffi'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

try:
    deps = [Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)]
except:
    deps = []

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          *deps,
          name='slashlockgui',
          debug=False,
          strip=False,
          upx=True,
          console=True )
