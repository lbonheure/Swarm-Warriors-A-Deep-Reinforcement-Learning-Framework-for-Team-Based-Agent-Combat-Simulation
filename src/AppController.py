import tkinter as tk
import random
import threading as thr
import time

from AppView import AppView
from map import Map
from gameState import GameState
from Agent import Agent


class AppController(AppView.Listener):
    def __init__(self) -> None:
        # Create the view
        self.appView = AppView()
        self.appView.setListener(self)

        # Create the map, the grid and the gameState
        self.agents = {"agent1": (0, 0, "blue"), "agent2": (19, 19, "green")}
        self.map = Map(random=True, agent_bases=self.agents)
        self.grid = self.appView.createGrid(self.map)
        self.gameState = GameState(self.map)
        self.gameState.set_agents(agents=self.agents)

        # Simulation parameters
        self.running = False
        self.speed_simu = self.appView.get_speed_simu()

        # init agent
        self.decision_agent = Agent()

    def run(self):
        """Launch the application
        """
        """Launch the application
        """
        self.appView.show()
        self.appView.mainloop()

    def show_agents(self):
        """Show the agents on the grid
        """
        self.grid.update(self.gameState)

    def random_move(self):
        """Perform a random movement for all agents. (the movement may fail)
        """
        actions = {}
        moves = ["N", "S", "O", "E"]
        for a in self.agents:
            # d = random.choice(moves)
            print(self.gameState.get_infos(self.agents)[a])
            d = self.decision_agent.act_best(self.gameState.get_infos(self.agents)[a])
            print(d)
            actions[a] = ["Move", d]
        self.gameState.update_state(actions)
        # self.grid.update(self.gameState) # Show changes on the graphical interface


    def new_map(self):
        """Change the map (randomly)
        """
        self.map.reset(random=True)
        self.gameState.set_map(self.map)
        self.grid.update(self.gameState) # Show changes on the graphical interface

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