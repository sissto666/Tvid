import ctypes
from ctypes.wintypes import MSG
from PySide6.QtCore import QThread, Signal

MOD_MAP = {
    "Alt": 0x0001,
    "Ctrl": 0x0002,
    "Shift": 0x0004,
    "Win": 0x0008,
}

VK_MAP = {
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,
    "`": 0xC0,
}

class GlobalHotkey(QThread):
    hotkey_triggered = Signal()

    def __init__(self,MOD,VK):
        super().__init__()
        self.user32 = ctypes.windll.user32
        self.running = True
        self.MOD = MOD_MAP[MOD]
        self.VK = VK_MAP[VK]


    def run(self):
        if not self.user32.RegisterHotKey(None, 1, self.MOD, self.VK):
            return

        try:
            msg = MSG()
            while self.running:
                if self.user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, self.MOD):
                    if msg.message == 0x0312:
                        if msg.wParam == 1:
                            self.hotkey_triggered.emit()
                    self.user32.TranslateMessage(ctypes.byref(msg))
                    self.user32.DispatchMessageW(ctypes.byref(msg))
                self.msleep(200)
        finally:
            self.user32.UnregisterHotKey(None, 1)

    def stop(self):
        self.running = False
        self.wait()