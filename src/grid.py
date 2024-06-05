import tkinter as tk
from math import (sin, cos, pi)

from map import Map
from gameState import GameState


class Grid:
    def __init__(self, master, map: Map=None) -> None:
        self.map = map
        self.map_drawed = False
        self.agents = {}
        self.canvas = tk.Canvas(master, bg='white')
        self.canvas.bind('<Configure>', self._update_canvas)

    def show(self):
        self.canvas.pack(side="top", fill="both", expand="true", padx=10, pady=10)

    def destroy(self):
        self.canvas.destroy()
        
    def update(self, gameState: GameState):
        if self.map is None or self.map != gameState.map:
            self.map = gameState.map
            self._draw_map()
        self.agents = gameState.agents
        self._show_agents()
        
    def set_map(self, map: Map):
        self.map = map
        self._draw_map()
        
        
    def _update_canvas(self, event=None):
        self._draw_map()
        self._show_agents()

    def _create_grid(self, event=None):
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        self.canvas.delete('grid_line')  # Will only remove the grid_line

        # Creates all vertical lines at intevals of 100
        for i in range(0, w, 100):
            self.canvas.create_line([(i, 0), (i, h)], tag='grid_line')

        # Creates all horizontal lines at intevals of 100
        for i in range(0, h, 100):
            self.canvas.create_line([(0, i), (w, i)], tag='grid_line')

    def _create_grid_nxm(self, event=None):
        if self.map is None:
            raise MapIsNoneError
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        self.canvas.delete('grid_line')  # Will only remove the grid_line

        u_x = w / self.map.width
        u_y = h / self.map.height

        for i in range(self.map.width):
            self.canvas.create_line([(i * u_x, 0), (i * u_x, h)], tag='grid_line')

        for i in range(self.map.height):
            self.canvas.create_line([(0, i * u_y), (w, i * u_y)], tag='grid_line')

    def _draw_map(self, event=None):
        if self.map is None:
            raise MapIsNoneError
        self.map_drawed = True
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        u_x = w / self.map.width
        u_y = h / self.map.height
        
        # Draw grid
        self._create_grid_nxm(event)
        
        # Draw walls
        self.canvas.delete("wall")
        for (x, y) in self.map.walls_positions:
            self.canvas.create_rectangle(x * u_x, y * u_y, (x + 1) * u_x, (y + 1) * u_y, fill="grey", outline="grey", tags="wall")
        
        # Draw ores
        self.canvas.delete("ore")
        for (x, y) in self.map.resources_positions:
            self._draw_hexagon(x, y, u_x, u_y)
            
        # Draw bases
        if self.map.agents_bases:
            for b in self.map.agents_bases.keys():
                self._draw_base(b, self.map.agents_bases[b])

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

    def _show_agents(self):
        for a in self.agents.keys():
            self._draw_agent(a, self.agents[a])

    def _draw_agent(self, name, params):
        if self.map is None:
            raise MapIsNoneError
        (x, y) = params["position"]
        color = params["AI"].color
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        self.canvas.delete(name)

        u_x = w / self.map.width
        u_y = h / self.map.height

        u = min(u_x, u_y) - 4

        x0 = (x * u_x) + (u_x / 2) - (u / 2)
        x1 = (x * u_x) + (u_x / 2) + (u / 2)
        y0 = (y * u_y) + (u_y / 2) - (u / 2)
        y1 = (y * u_y) + (u_y / 2) + (u / 2)

        self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline=color, tags=name)
        self.canvas.update()
        # print("agent", name, "drawed at position (", x, ",",  y, ") in", color)

    def _draw_base(self, name, params):
        if self.map is None:
            raise MapIsNoneError
        (x, y) = params["position"]
        color = params["AI"].color
        w = self.canvas.winfo_width()  # Get current width of canvas
        h = self.canvas.winfo_height()  # Get current height of canvas
        self.canvas.delete("b:" + name)

        u_x = w / self.map.width
        u_y = h / self.map.height
        self.canvas.create_rectangle(x * u_x + 1, y * u_y + 1, (x + 1) * u_x - 1, (y + 1) * u_y - 1, fill=None,
                                     outline=color, width=3, tags="b:" + name)
    
    
class MapIsNoneError(Exception):
    pass