import tkinter as tk
import random
import threading as thr
import time

from AppView import AppView
from map import Map
from gameState import GameState
from Agent import (Agent, CombatAgent)


class AppController(AppView.Listener):
    def __init__(self) -> None:
        # Create the view
        self.appView = AppView()
        self.appView.setListener(self)

        # Create the map, the grid and the gameState
        # agent: (x, y, hp, decisionAgent)
        self.decisionAgent_blue_melee = Agent(color="blue", range=1)
        self.agents = {"agent1": [0, 0, 100, self.decisionAgent_blue_melee], "agent2": (19, 19, "green", True)}
        """
        self.agents = {"agent1": CombatAgent((0,0), "blue", output_net=5, range=1),
                       "agent2": CombatAgent((0,0), "blue", output_net=5, range=2),
                       "agent3": CombatAgent((0,0), "red", output_net=5, range=1),
                       "agent4": CombatAgent((0,0), "red", output_net=5, range=2)}
        """
        self.map = Map(random=True, agent_bases=self.agents)
        self.grid = self.appView.createGrid(self.map)
        self.gameState = GameState(self.map)
        self.gameState.set_agents(agents=self.agents)

        # Simulation parameters
        self.running = False
        self.speed_simu = self.appView.get_speed_simu()

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
        
    def train_model(self):
        # TODO interface graphique permetant de visualiser la progression du training
        # TODO Init model for training
        
        # TODO train model -> 1 shot ? many times ?
        train_map = Map()
        train_map.load("maps/map0.csv")
        train_gameState = GameState(train_map, self.agents)
        # train_gameState.set_agents(agents=self.agents)
        
        for i in range(100): # number of move for training
            actions = {}
            for a in self.agents:
                d = self.decision_agent.act_best(self.gameState.get_infos(self.agents)[a])
                print(d)
                actions[a] = d
            self.gameState.update_state(actions)
            
        # TODO Prepare model for simu
        # TODO Reset gameState

    def random_move(self):
        """Perform a random movement for all agents. (the movement may fail)
        """
        actions = {}
        for a in self.agents:
            _, _, _, decision_agent = self.agents[a]
            d = decision_agent.act_best(self.gameState.get_infos(self.agents)[a])
            print(d)
            actions[a] = d
        self.gameState.update_state(actions)
        self.grid.update(self.gameState) # Show changes on the graphical interface


    def new_map(self):
        """Change the map (randomly)
        """
        self.map.reset(random=True)
        self.gameState.set_map(self.map)
        self.grid.set_map(self.map) # Show changes on the graphical interface

    def run_simu(self):
        """Launch the simulation
        """
        if thr.active_count() < 2:
            self.running = True
            simu_thread = thr.Thread(target=self._run_simu, args=[self.speed_simu])
            simu_thread.start()
        
    def _run_simu(self, speed):
        while self.running:
            self.random_move()
            time.sleep(1 / speed.get())
        

    def stop_simu(self):
        """Stop the simulation
        """
        self.running = False