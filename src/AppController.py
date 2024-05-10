import tkinter as tk
import random

from AppView import AppView

class AppController(AppView.Listener):
    def __init__(self) -> None:
        self.appView = AppView()
        self.appView.setListener(self)
        self.grid = self.appView.createGrid(20, 20)
        self.agents = {"agent1": (3,3,"blue"), "agent2": (5,10,"green")}

    def run(self):
        self.appView.show()
        self.appView.mainloop()


    def test_show_agents(self):
        # test
        self.grid.show_agents(self.agents)


    def random_move(self):
        external, internal = self.grid.get_forbiden_cases()
        for a in self.agents.keys():
            moves = []
            x, y, c = self.agents[a]
            if x - 1 >= external[0] and (x-1, y) not in internal:
                moves.append("O")
            if x + 1 < external[1] and (x+1, y) not in internal:
                moves.append("E")
            if y - 1 >= external[2] and (x, y-1) not in internal:
                moves.append("N")
            if y + 1 < external[3] and (x, y+1) not in internal:
                moves.append("S")

            m = random.choice(moves)
            match m:
                case "O":
                    x -= 1
                case "E":
                    x += 1
                case "N":
                    y -= 1
                case "S":
                    y += 1
            self.agents[a] = (x, y, c)
        
        self.test_show_agents()
