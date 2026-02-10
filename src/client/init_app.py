from tkinter import *
from tkinter import messagebox
from src.client.url_client import URLClient
from src.tools.singleton import Singleton
from src.client.client import Client
import sys
import os

def resource_path(relative_path):
    try:
        # PyInstaller's temporary folder
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class App(metaclass=Singleton):

    def __init__(self) -> None:
        try:
            self.frame = Tk()
            self.frame.attributes('-topmost', 'false')
            self.frame.iconbitmap(resource_path("logo.ico"))
            self.frame.title('Data Convert')
            self.frame.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.frames = {
                "Select": Client(self, self.frame),
                "URL": URLClient(self, self.frame),
            }
            self.current = None
            self.show_frame('Select')
            # show the UI to user
            self.frame.mainloop()
        except KeyboardInterrupt:
            pass
        except TclError as err:
            pass

    def show_frame(self, name: str) -> None:
        if self.current:
            self.current.pack_forget()
        self.current = self.frames[name]
        self.current.pipeline_frame()

    def on_closing(self) -> None:
        result = messagebox.askquestion(title='Quit', message='Do you want to quit?')
        if result == 'yes':
            self.frame.destroy()
