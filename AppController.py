import tkinter as tk

from AppView import AppView

class AppController:
    def __init__(self) -> None:
        self.appView = AppView()

    def run(self):
        self.appView.show()
        self.appView.mainloop()