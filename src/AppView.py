import tkinter as tk

class AppView(tk.Tk):
    def __init__(self, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.geometry("850x750")
        self.configure(cursor="arrow")
        self.minsize(850, 750)
        self.resizable(True, True)
        self.title("Grid")

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.bind('<Configure>', self.create_grid_nxm)


    def show(self):
        self.canvas.pack(fill="both", expand="true")


    def create_grid(self, event=None):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        self.canvas.delete('grid_line') # Will only remove the grid_line

        # Creates all vertical lines at intevals of 100
        for i in range(0, w, 100):
            self.canvas.create_line([(i, 0), (i, h)], tag='grid_line')

        # Creates all horizontal lines at intevals of 100
        for i in range(0, h, 100):
            self.canvas.create_line([(0, i), (w, i)], tag='grid_line')


    def create_grid_nxm(self, event, n=20, m=20):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        self.canvas.delete('grid_line') # Will only remove the grid_line

        n_x = w//n
        n_y = h//m

        # Creates all vertical lines at intevals of 100
        for i in range(0, w, n_x):
            self.canvas.create_line([(i, 0), (i, h)], tag='grid_line')

        # Creates all horizontal lines at intevals of 100
        for i in range(0, h, n_y):
            self.canvas.create_line([(0, i), (w, i)], tag='grid_line')