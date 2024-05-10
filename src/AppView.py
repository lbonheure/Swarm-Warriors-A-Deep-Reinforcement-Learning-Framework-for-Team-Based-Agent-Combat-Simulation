import tkinter as tk

from grid import Grid

class AppView(tk.Tk):

    class Listener:
        def test_show_agents(self):
            pass
        def random_move(self):
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
        self.move_button = tk.Button(self, text="Random Move", command=self.call_controller_random_move)
        self.grid = None
        self.listener = None


    def setListener(self, l:Listener):
        self.listener = l


    def createGrid(self, row_number, column_number):
        if self.grid:
            self.grid.destroy()
        self.grid = Grid(self, row_number, column_number)
        return self.grid


    def show(self):
        self.hello_label.pack(side="top")
        self.show_button.pack(side="top")
        self.move_button.pack(side="top")
        self.grid.show()


    def call_controller_show_agents(self):
        self.listener.test_show_agents()


    def call_controller_random_move(self):
        self.listener.random_move()