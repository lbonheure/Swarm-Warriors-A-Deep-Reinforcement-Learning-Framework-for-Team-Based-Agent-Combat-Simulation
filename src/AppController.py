import tkinter as tk
import random
import threading as thr
import time

from AppView import AppView


class AppController(AppView.Listener):
    def __init__(self) -> None:
        # Create the view
        self.appView = AppView()
        self.appView.setListener(self)

        # Create the grid and the gameState
        self.grid = self.appView.createGrid(random=True)
        self.gameState = self.grid.get_state()
        self.agents = {"agent1": (0, 0, "blue"), "agent2": (19, 19, "green")}
        self.gameState.set_agents(agents=self.agents)
        self.gameState.set_bases(self.agents)

        # Simulation parameters
        self.running = False
        self.speed_simu = self.appView.get_speed_simu()

    def run(self):
        """Launch the application
        """
        self.appView.show()
        self.appView.mainloop()

    def show_agents(self):
        """Show the agents on the grid
        """
        self.grid.show_agents(self.agents)

    def random_move(self):
        """Perform a random movement for all agents. (the movement may fail)
        """
        actions = {}
        moves = ["N", "S", "O", "E"]
        for a in self.agents:
            d = random.choice(moves)
            actions[a] = ["Move", d]
        self.gameState.update_state(actions)
        """
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

        self.show_agents()
        """

    def new_map(self):
        """Change the map (randomly)
        """
        self.grid.reset_map()

    def run_simu(self):
        """Launch the simulation
        """
        self.running = True
        while self.running:
            self.random_move()
            time.sleep(1 / self.speed_simu.get())

    def stop_simu(self):
        """Stop the simulation
        """
        self.running = False