import tkinter as tk
import tkinter.messagebox as msg
import os
from tkinter import filedialog as fd

import copy
import random
import threading as thr
import time

from AppView import AppView
from progression_bar_view import ProgressBarView
from map import Map
from gameState import GameState
from Agent import (Agent, CombatAgent)

# For the training
from tqdm import tqdm
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # To disable the spam Warning from TensorFlow


class AppController(AppView.Listener):
    def __init__(self) -> None:
        # Create the view
        self.appView = AppView()
        self.appView.setListener(self)

        # Create the map, the grid and the gameState
        # agent: (x, y, hp, decisionAgent)
        self.decisionAgent_blue_melee = CombatAgent(color="blue", atk_range=1, atk=10)
        self.decisionAgent_blue_range = CombatAgent(color="blue", atk_range=2, atk=10)
        self.decisionAgent_red_melee = CombatAgent(color="red", atk_range=1, atk=10)
        self.decisionAgent_red_range = CombatAgent(color="red", atk_range=2, atk=10)
        self.decisionAgents = {"decisionAgent_blue_melee": self.decisionAgent_blue_melee,
                               "decisionAgent_blue_range": self.decisionAgent_blue_range,
                               "decisionAgent_red_melee": self.decisionAgent_red_melee,
                               "decisionAgent_red_range": self.decisionAgent_red_range
                               }
        self.agents = {"agent_b1": {"position": (0, 0), "hp": 70, "hpMax": 70, "AI": self.decisionAgent_blue_range},
                       "agent_b2": {"position": (7, 0), "hp": 100, "hpMax": 100, "AI": self.decisionAgent_blue_melee},
                       "agent_b3": {"position": (12, 0), "hp": 100, "hpMax": 100, "AI": self.decisionAgent_blue_melee},
                       "agent_b4": {"position": (19, 0), "hp": 70, "hpMax": 70, "AI": self.decisionAgent_blue_range},
                       "agent_r1": {"position": (0, 19), "hp": 70, "hpMax": 70, "AI": self.decisionAgent_red_range},
                       "agent_r2": {"position": (7, 19), "hp": 100, "hpMax": 100, "AI": self.decisionAgent_red_melee},
                       "agent_r3": {"position": (12, 19), "hp": 100, "hpMax": 100, "AI": self.decisionAgent_red_melee},
                       "agent_r4": {"position": (19, 19), "hp": 70, "hpMax": 70, "AI": self.decisionAgent_red_range}}
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
        progress = tk.IntVar(self.appView, 0)
        pb = ProgressBarView(self.appView, progress)
        pb.show()
        
        # TODO Init model for training

        # TODO train model -> 1 shot ? many times ?
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Disable the spam Warning from TensorFlow

        # Load the map
        train_map = Map(agent_bases=self.agents)
        train_map.load_filename("map0.csv")
        # Place the agents in their bases on the map
        self._reset_pos_agents()
        train_gameState = GameState(train_map, self.agents)
        # train_gameState.set_agents(agents=self.agents)
        episodes = 1000
        for i in tqdm(range(episodes)):
            done = False
            step_nbr = 0
            while not done:
                if step_nbr == 1000:
                    done = True

                # Observe the actual states
                old_states = train_gameState.get_infos(self.agents)

                actions = {}
                for a in self.agents:
                    decision_agent = self.agents[a]["AI"]
                    hp = self.agents[a]["hp"]
                    if hp > 0:
                        decision_agent: Agent
                        old_states[a] = old_states[a] + [hp]
                        d = decision_agent.act_train(old_states[a])
                        actions[a] = d

                rewards = train_gameState.update_state(actions)

                new_states = train_gameState.get_infos(self.agents)

                for a in self.agents:
                    end = False
                    hp = self.agents[a]["hp"]
                    if hp <= 0 or done:
                        end = True
                    decision_agent = self.agents[a]["AI"]
                    new_states[a] = new_states[a]+[hp]
                    # Train the agent over this single step
                    print(old_states[a], rewards[a], new_states[a], end)
                    decision_agent.training_montage(old_states[a], rewards[a], new_states[a], end)

                    # Remember this action and its consequence for later
                    decision_agent.fill_memory(old_states[a], rewards[a], new_states[a], end)

                step_nbr += 1

            for a in self.agents:
                decision_agent = self.agents[a]["AI"]
                decision_agent: Agent
                decision_agent.train_long_memory()

            if step_nbr % 500 == 0:
                for decision_agent_name, decision_agent in self.decisionAgents.items():
                    decision_agent: Agent
                    decision_agent.model.save(f"../weights_rl/{decision_agent_name}.h5")

            self._reset_pos_agents()
            
            progress.set(i+1) # update progress in progessbar

        # TODO Prepare model for simu
        # TODO Reset gameState

    def random_move(self):
        """Perform a random movement for all agents. (the movement may fail)
        """
        actions = {}
        for a in self.agents:
            decision_agent = self.agents[a]["AI"]
            hp = self.agents[a]["hp"]
            decision_agent: Agent
            d = decision_agent.act_best(self.gameState.get_infos(self.agents)[a] + [hp])
            actions[a] = d
        self.gameState.update_state(actions)
        self.grid.update(self.gameState)  # Show changes on the graphical interface

    def new_map(self):
        """Change the map (randomly)
        """
        self.map.reset(random=True)
        # Place the agents in their bases on the map
        self._reset_pos_agents()
        self.gameState.set_map(self.map)
        # Show changes on the graphical interface
        self.grid.set_map(self.map)
        self.grid.update(self.gameState)

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

    def save_map(self):
        if (os.path.exists("./maps")):
            dir = "./maps"
        elif (os.path.exists("../maps")):
            dir = "../maps"
        else:
            dir = "."
        file = fd.asksaveasfile(filetypes=[("csv file", "*.csv"), ], defaultextension=".csv", initialdir=dir)
        if file:
            self.map.save(file)

    def load_map(self):
        if (os.path.exists("./maps")):
            dir = "./maps"
        elif (os.path.exists("../maps")):
            dir = "../maps"
        else:
            dir = "."
        file = fd.askopenfile(filetypes=[("csv file", "*.csv"), ], defaultextension=".csv", initialdir=dir)
        if file:
            self.map.load(file)

        # Place the agents in their bases on the map
        self._reset_pos_agents()

        self.gameState.set_map(self.map)
        # Show changes on the graphical interface
        self.grid.set_map(self.map)
        self.grid.update(self.gameState)

    def _reset_pos_agents(self):
        for a in self.agents.keys():
            self.agents[a]["position"] = self.map.agents_bases[a]["position"]
            self.agents[a]["hp"] = self.agents[a]["hpMax"]
