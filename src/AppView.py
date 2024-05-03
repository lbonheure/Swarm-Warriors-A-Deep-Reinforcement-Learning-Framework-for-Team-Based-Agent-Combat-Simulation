import tkinter as tk

from grid import Grid

class AppView(tk.Tk):

    class Listener:
        def test_show_agents(self):
            pass

    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.geometry("850x750")
        self.configure(cursor="arrow")
        self.minsize(850, 750)
        self.resizable(True, True)
        self.title("Grid")

        self.hello_label = tk.Label(self, text="Hello world!")
        self.show_button = tk.Button(self, text="Show agents", command=self.call_controller_show_agents)
        self.grid = Grid(self, 20, 20)

        self.listener = None


    def setListener(self, l:Listener):
        self.listener = l


    def show(self):
        self.hello_label.pack()
        self.show_button.pack()
        self.grid.show()

    def show_agents(self, agents):
        self.grid.show_agents(agents)


    def call_controller_show_agents(self):
        self.listener.test_show_agents()