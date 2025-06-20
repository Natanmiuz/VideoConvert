import tkinter as tk
from gui.ui import VideoConverterApp

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)  
except ImportError:
    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()