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
from simuChoiceView import SimuChoiceView
from map import Map
from gameState import GameState
from Agent import (Agent, CombatAgent)

# For the training
from tqdm import tqdm
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # To disable the spam Warning from TensorFlow


class AppController(AppView.Listener, SimuChoiceView.Listener):
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
                               "decisionAgent_red_range": self.decisionAgent_red_range}
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

        self.train_thread = None

        # Simulation parameters
        self.simu_thread = None
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
        pb = ProgressBarView(self.appView)
        pb.show()

        if self.train_thread is None or not self.train_thread.is_alive():
            self.train_thread = thr.Thread(target=self._train_model, name="train_thread", args=[pb], daemon=True)
            self.train_thread.start()


    def _train_model(self, progress_bar):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Disable the spam Warning from TensorFlow

        # Load the map
        train_map = Map(agent_bases=self.agents)
        train_map.load_filename("map0.csv")
        self.grid.set_map(train_map)
        # Place the agents in their bases on the map
        self._reset_pos_agents()
        train_gameState = GameState(train_map, self.agents)
        # train_gameState.set_agents(agents=self.agents)
        episodes = 100
        for i in tqdm(range(episodes)):
            done = False
            step_nbr = 0

            team_number_alive = {}
            # Iterate over all agents
            for agent_info in self.agents.values():
                team_color = agent_info["AI"].get_color()
                if team_color not in team_number_alive:
                    team_number_alive[team_color] = 1
                else:
                    team_number_alive[team_color] += 1

            agent_status = {agent_id: True for agent_id, agent_info in self.agents.items()}
            while not done:
                if step_nbr == 500:
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
                    else:
                        actions[a] = 0

                rewards = train_gameState.update_state(actions)
                self.grid.update(train_gameState)

                new_states = train_gameState.get_infos(self.agents)

                for a in self.agents:
                    if agent_status[a]:
                        end = False
                        hp = self.agents[a]["hp"]
                        if hp <= 0 or done:
                            end = True
                            agent_status[a] = False
                            #self.agents[a]["AI"]: CombatAgent
                            agent_color = self.agents[a]["AI"].get_color()
                            team_number_alive[agent_color] -= 1

                        decision_agent = self.agents[a]["AI"]
                        new_states[a] = new_states[a] + [hp]
                        # Train the agent over this single step
                        decision_agent.training_montage(old_states[a], rewards[a], new_states[a], end)

                        # Remember this action and its consequence for later
                        decision_agent.fill_memory(old_states[a], rewards[a], new_states[a], end)
                    else:
                        new_states[a] = 0
                print(step_nbr)
                step_nbr += 1

                for team, count in team_number_alive.items():  # if 1 team is completely dead
                    if count == 0:
                        done = True

            #start = time.time_ns()
            for decision_agent_name, decision_agent in self.decisionAgents.items():
                decision_agent.train_long_memory()
            #e_time = (time.time_ns() - start) / 1000000
            #print("time for train long memory:", e_time, "ms")

            for decision_agent_name, decision_agent in self.decisionAgents.items():
                decision_agent: Agent
                decision_agent.model.save(f"../weights_rl/{episodes % 100}/{decision_agent_name}.h5")

            self._reset_pos_agents()
            train_gameState.set_map(train_map)
            progress_bar.update_progress(i + 1)  # update progress in progressbar


    def random_move(self):
        """Perform a random movement for all agents. (the movement may fail)
        """
        actions = {}
        for a in self.agents:
            d = random.choice(["N", "S", "W", "E", "A"])
            actions[a] = d
        self.gameState.update_state(actions)
        self.grid.update(self.gameState)  # Show changes on the graphical interface

    def trained_move(self):
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
        choice = SimuChoiceView(self.appView)
        choice.set_listener(self)
        choice.show()

    def run_random_simu(self):
        if self.simu_thread is None or not self.simu_thread.is_alive():
            self.running = True
            self.simu_thread = thr.Thread(target=self._run_random_simu, name="simu_thread", args=[self.speed_simu], daemon=True)
            self.simu_thread.start()

    def run_trained_simu(self):
        for decision_agent_name, decision_agent in self.decisionAgents.items():
            decision_agent: Agent
            decision_agent.load(f"../weights_rl/{decision_agent_name}.h5")
        if self.simu_thread is None or not self.simu_thread.is_alive():
            self.running = True
            self.simu_thread = thr.Thread(target=self._run_trained_simu, name="simu_thread", args=[self.speed_simu], daemon=True)
            self.simu_thread.start()

    def _run_random_simu(self, speed):
        while self.running:
            team_color = {}
            for a in self.agents.keys():
                if self.agents[a]["hp"] > 0:
                    color = self.agents[a]["AI"].color
                    team_color[color] = True
            if len(team_color.keys()) < 2:
                # Only 1 team is left
                self.running = False
                break

            self.random_move()
            time.sleep(1 / speed.get())

    def _run_trained_simu(self, speed):
        while self.running:
            team_color = {}
            for a in self.agents.keys():
                if self.agents[a]["hp"] > 0:
                    color = self.agents[a]["AI"].color
                    team_color[color] = True
            if len(team_color.keys()) < 2:
                # Only 1 team is left
                self.running = False
                break

            self.trained_move()
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

    def reset(self):
        self._reset_pos_agents()
        self.gameState.set_map(self.map)
        self.grid.update(self.gameState)
