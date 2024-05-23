import tkinter as tk
import random
from math import (sin, cos, pi)
import copy


class Grid:
    def __init__(self, master, random=False, width=20, height=20, num_walls=20, num_resource_ores=2) -> None:
        self.width = width
        self.height = height
        self.random = random
        self.num_walls = num_walls
        self.num_resource_ores = num_resource_ores
        self.map_drawed = False

        self.canvas = tk.Canvas(master, bg='white')
        self.canvas.bind('<Configure>', self.update_canvas)

        self.current_agents = None
        self.walls_pos = []
        self.resource_ores_pos = []

    def show(self):
        self.canvas.pack(side="top", fill="both", expand="true", padx=10, pady=10)

    def destroy(self):
        self.canvas.destroy()

    def create_grid(self, event=None):
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        self.canvas.delete('grid_line')  # Will only remove the grid_line

        # Creates all vertical lines at intevals of 100
        for i in range(0, w, 100):
            self.canvas.create_line([(i, 0), (i, h)], tag='grid_line')

        # Creates all horizontal lines at intevals of 100
        for i in range(0, h, 100):
            self.canvas.create_line([(0, i), (w, i)], tag='grid_line')

    def create_grid_nxm(self, event):
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        self.canvas.delete('grid_line')  # Will only remove the grid_line

        u_x = w / self.width
        u_y = h / self.height

        for i in range(self.width):
            self.canvas.create_line([(i * u_x, 0), (i * u_x, h)], tag='grid_line')

        for i in range(self.height):
            self.canvas.create_line([(0, i * u_y), (w, i * u_y)], tag='grid_line')

    def create_map(self, event):
        self.map_drawed = True
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        u_x = w / self.width
        u_y = h / self.height

        self.walls_pos.clear()
        self.resource_ores_pos.clear()
        if self.random:
            self.canvas.delete("wall")
            for i in range(self.num_walls):
                x, y = self._free_random_pos_wall()
                self.canvas.create_rectangle(x * u_x, y * u_y, (x + 1) * u_x, (y + 1) * u_y, fill="grey",
                                             outline="grey", tags="wall")
            self.canvas.delete("ore")
            for j in range(self.num_resource_ores):
                x, y = self._free_random_pos_ore()
                self._draw_hexagon(x, y, u_x, u_y)
        else:
            if self.width < 20 or self.height < 20:
                raise ValueError
            self.walls_pos = [(7, 9), (8, 9), (9, 9), (11, 9), (13, 9),
                              (7, 10), (9, 10), (11, 10), (13, 10),
                              (7, 11), (9, 11), (11, 11), (12, 11), (13, 11)]
            self.resource_ores_pos = [(8, 10), (12, 10)]
            self.canvas.delete("wall")
            for (x, y) in self.walls_pos:
                self.canvas.create_rectangle(x * u_x, y * u_y, (x + 1) * u_x, (y + 1) * u_y, fill="grey",
                                             outline="grey", tags="wall")
            self.canvas.delete("ore")
            for (x, y) in self.resource_ores_pos:
                self._draw_hexagon(x, y, u_x, u_y)

    def update_map(self, event):
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        u_x = w / self.width
        u_y = h / self.height
        self.canvas.delete("wall")
        self.canvas.delete("ore")
        for (x, y) in self.walls_pos:
            self.canvas.create_rectangle(x * u_x, y * u_y, (x + 1) * u_x, (y + 1) * u_y, fill="grey", outline="grey",
                                         tags="wall")
        for (x, y) in self.resource_ores_pos:
            self._draw_hexagon(x, y, u_x, u_y)

    def _free_random_pos_wall(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        while (x, y) in self.walls_pos:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
        self.walls_pos.append((x, y))
        return x, y

    def _free_random_pos_ore(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        while (x, y) in self.walls_pos or (x, y) in self.resource_ores_pos:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
        self.resource_ores_pos.append((x, y))
        return x, y

    def _draw_hexagon(self, x, y, u_x, u_y):
        u = min(u_x, u_y) - 4
        xc = (x * u_x) + (u_x / 2)
        yc = (y * u_y) + (u_y / 2)
        d = u / 2
        x0 = xc - d * cos(pi / 3)
        y0 = yc + d * sin(pi / 3)
        x1 = xc + d * cos(pi / 3)
        y1 = yc + d * sin(pi / 3)
        x2 = xc + d
        y2 = yc
        x3 = xc + d * cos(pi / 3)
        y3 = yc - d * sin(pi / 3)
        x4 = xc - d * cos(pi / 3)
        y4 = yc - d * sin(pi / 3)
        x5 = xc - d
        y5 = yc
        self.canvas.create_polygon(x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, splinesteps=6, fill="purple",
                                   outline="yellow", tags="ore")

    def show_agents(self, agents: dict):
        self.current_agents = agents
        for a in agents.keys():
            self.draw_agent(a, agents[a])

    def draw_agent(self, name, params):
        x, y, color = params
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        self.canvas.delete(name)

        u_x = w / self.width
        u_y = h / self.height

        u = min(u_x, u_y) - 4

        x0 = (x * u_x) + (u_x / 2) - (u / 2)
        x1 = (x * u_x) + (u_x / 2) + (u / 2)
        y0 = (y * u_y) + (u_y / 2) - (u / 2)
        y1 = (y * u_y) + (u_y / 2) + (u / 2)

        # self.canvas.create_oval(x*u_x+3, y*u_y+3, (x+1)*u_x-3, (y+1)*u_y-3, fill=color, outline=color, tags=name)
        self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline=color, tags=name)
        self.canvas.update()
        # print("agent", name, "drawed at position (", x, ",",  y, ") in", color)
        # print(x*u_x+3, y*u_y+3, (x+1)*u_x-3, (y+1)*u_y-3)

    def reset_map(self):
        self.map_drawed = False
        self.update_canvas()

    def update_canvas(self, event=None):
        self.create_grid_nxm(event)
        if self.map_drawed:
            self.update_map(event)
        else:
            self.create_map(event)
        if self.current_agents:
            self.show_agents(self.current_agents)

    def get_forbiden_cases(self):
        external = (0, self.width, 0, self.height)
        internal = copy.copy(self.walls_pos)
        internal.extend(self.resource_ores_pos)
        return external, internal