import sys

if sys.platform == "win32":
    KEY_BACKSPACE = "\x08"
    KEY_CTRL_BACKSPACE = "\x7f"
elif sys.platform in ("linux", "darwin"):
    KEY_BACKSPACE = "\x7f"
    KEY_CTRL_BACKSPACE = "\x08"

KEY_ESC = "\x1b"
KEY_CTRL_E = "\x05"
KEY_CTRL_W = "\x17"
