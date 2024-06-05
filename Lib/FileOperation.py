import tkinter as tk
from tkinter import filedialog
import os


class FileHandling:
    def __init__(self):
        pass

    @staticmethod
    def file_choose(is_folder=False):
        """
        Opens file/folder selection window in windows.
        :param is_folder: If set true will choose a folder (default is ``False``)
        :return: The selected file/folder path
        """
        root = tk.Tk()
        root.lift()
        root.attributes('-topmost', True)
        root.withdraw()
        # take user home
        u_home = os.path.expanduser("~")
        if is_folder:
            fp = filedialog.askdirectory(initialdir=u_home)
        else:
            fp = filedialog.askopenfilename(initialdir=u_home)
        root.destroy()
        if not fp:
            raise Exception("No file or folder selected.")
        return fp

