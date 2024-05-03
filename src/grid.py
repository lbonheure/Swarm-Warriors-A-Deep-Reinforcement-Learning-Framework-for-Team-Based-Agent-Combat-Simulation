import tkinter as tk


class Grid:
    def __init__(self, master, width, height) -> None:
        self.width = width
        self.height = height
        self.canvas = tk.Canvas(master, bg='white')
        self.canvas.bind('<Configure>', self.update_canvas)

        self.current_agents = None


    def show(self):
        self.canvas.pack(fill="both", expand="true", padx=10, pady=10)


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


    def create_grid_nxm(self, event):
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        self.canvas.delete('grid_line') # Will only remove the grid_line

        n_x = w//self.width
        n_y = h//self.height

        # Creates all vertical lines at intevals of 100
        for i in range(0, w, n_x):
            self.canvas.create_line([(i, 0), (i, h)], tag='grid_line')

        # Creates all horizontal lines at intevals of 100
        for i in range(0, h, n_y):
            self.canvas.create_line([(0, i), (w, i)], tag='grid_line')


    def show_agents(self, agents:dict):
        self.current_agents = agents
        for a in agents.keys():
            self.draw_agent(a, agents[a])


    def draw_agent(self, name, params):
        x, y, color = params
        w = self.canvas.winfo_width() # Get current width of canvas
        h = self.canvas.winfo_height() # Get current height of canvas
        self.canvas.delete(name)

        u_x = w//self.width
        u_y = h//self.height

        #print(x, y, h, w, u_x, u_y)

        self.canvas.create_oval(x*u_x+3, y*u_y+3, (x+1)*u_x-3, (y+1)*u_y-3, fill=color, outline=color, tags=name)
        self.canvas.update()
        #print("agent", name, "drawed at position (", x, ",",  y, ") in", color)
        #print(x*u_x+3, y*u_y+3, (x+1)*u_x-3, (y+1)*u_y-3)


    def update_canvas(self, event):
        self.create_grid_nxm(event)
        if self.current_agents:
            self.show_agents(self.current_agents)