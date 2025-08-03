import ctypes
import sys

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()