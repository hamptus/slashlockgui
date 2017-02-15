import os
import sys
import kivy.input.providers.probesysfs

def _read_line(path):
    try:
        with open(path) as f:
            return f.readline().strip()
    except PermissionError:
        print(os.getenv('SNAP_NAME', 'Not in a snap'))

def update_probesysfs():
    sys.modules['kivy.input.providers.probesysfs'].read_line = _read_line
