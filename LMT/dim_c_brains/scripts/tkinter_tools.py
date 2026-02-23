import tkinter as tk
from tkinter import filedialog

from pathlib import Path


def select_sqlite_file():
    root = tk.Tk()
    root.withdraw()
    file_str = filedialog.askopenfilename(
        title="Select SQLite file",
        filetypes=[("SQLite files", "*.sqlite"), ("All files", "*.*")],
    )
    root.destroy()
    if not file_str:
        print("No file selected.")
        return None
    return Path(file_str)


def select_folder():
    root = tk.Tk()
    root.withdraw()
    dir_str = filedialog.askdirectory(title="Select Folder")
    root.destroy()
    if not dir_str:
        print("No folder selected.")
        return None
    return Path(dir_str)
