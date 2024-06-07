import tkinter as tk
import tkinter.messagebox as msg
import os
from tkinter import filedialog as fd

import random
import threading as thr
import time

# For the training
from tqdm import tqdm

from AppView import AppView
from progression_bar_view import ProgressBarView
from simuChoiceView import SimuChoiceView
from map import Map
from gameState import GameState
from Agent import (Agent, CombatAgent)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # To disable the spam Warning from TensorFlow


class AppController(AppView.Listener, SimuChoiceView.Listener):
    def __init__(self) -> None:
        # Create the view
        self.appView = AppView()
        self.appView.setListener(self)

        # Create the agents, the map, the grid and the gameState
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
        """
        Launch the application
        """
        self.appView.show()
        self.appView.mainloop()

    def train_model(self):
        """
        Show the progress bar window and launch the thread that make the training
        """
        pb = ProgressBarView(self.appView)
        pb.show()
        
        if self.train_thread is None or not self.train_thread.is_alive():
            self.train_thread = thr.Thread(target=self._train_model, name="train_thread", args=[pb], daemon=True)
            self.train_thread.start()
        
    def _train_model(self, progress_bar: ProgressBarView):
        """
        Train the ML model
        :param progress_bar: the view of the progress bar
        """
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Disable the spam Warning from TensorFlow
        episodes = 200
        progress_bar.set_value(episodes)
        list_old_states = {a:[] for a in self.agents.keys()}
        list_rewards = {a:[] for a in self.agents.keys()}
        list_new_states = {a:[] for a in self.agents.keys()}
        list_end = {a:[] for a in self.agents.keys()}
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
            
            if i % 20 == 0: # Change the map every 20 episodes
                # Load the map
                train_map = Map(random=True, agent_bases=self.agents)
                if i == 180: # Last 20 episodes with the predefined map0
                    train_map.load_filename("map0.csv")
                self.grid.set_map(train_map)
                # Place the agents in their bases on the map
                self._reset_pos_agents()
                train_gameState = GameState(train_map, self.agents)
            
            while not done:
                if step_nbr == 512:
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
                            agent_color = self.agents[a]["AI"].get_color()
                            team_number_alive[agent_color] -= 1
                            if team_number_alive[agent_color] == 0:
                                done = True
                        decision_agent = self.agents[a]["AI"]
                        new_states[a] = new_states[a] + [hp]

                        # Train the agents per batch every 64 steps (batch size = 64)
                        if (step_nbr % 64 == 0 and step_nbr !=0) or end or done:
                            decision_agent.training_montage(tuple(list_old_states[a]), tuple(list_rewards[a]), tuple(list_new_states[a]), tuple(list_end[a]))
                            list_old_states[a].clear()
                            list_rewards[a].clear()
                            list_new_states[a].clear()
                            list_end[a].clear()
                        else:
                            list_old_states[a].append(old_states[a])
                            list_rewards[a].append(rewards[a])
                            list_new_states[a].append(new_states[a])
                            list_end[a].append(end)

                        # Remember this action and its consequence for later
                        decision_agent.fill_memory(old_states[a], rewards[a], new_states[a], end)
                step_nbr += 1
            
            for decision_agent_name, decision_agent in self.decisionAgents.items():
                decision_agent.train_long_memory()
            
            # Save intermediate models
            for decision_agent_name, decision_agent in self.decisionAgents.items():
                decision_agent: Agent
                decision_agent.save(f"../weights_rl/temp/{decision_agent_name}.weights.h5")
            
            self._reset_pos_agents()
            train_gameState.set_map(train_map)
            progress_bar.update_progress(i + 1) # update progress in progessbar
        
        # Save the final models
        t = time.ctime()
        path = "../weights_rl/"
        for l in t:
            if l == ":":
                l = "-"
            path += l
        os.mkdir(f"{path}")
        for decision_agent_name, decision_agent in self.decisionAgents.items():
            decision_agent: Agent
            decision_agent.save(f"{path}/{decision_agent_name}.weights.h5")
        
    def random_move(self):
        """
        Perform a random action for all agents. (the action may fail)
        """
        actions = {}
        for a in self.agents:
            if self.agents[a]["hp"] <= 0:
                d = 0
            else:
                d = random.choice(["N", "S", "W", "E", "A"])
            actions[a] = d
        self.gameState.update_state(actions)
        self.grid.update(self.gameState)  # Show changes on the graphical interface
        
    def trained_move(self):
        """
        Perform the best action for all agents accordind to the trained ML model. (the action may fail)
        """
        actions = {}
        for a in self.agents:
            decision_agent = self.agents[a]["AI"]
            hp = self.agents[a]["hp"]
            if hp <= 0:
                d = 0
            else:
                decision_agent: Agent
                d = decision_agent.act_best(self.gameState.get_infos(self.agents)[a] + [hp])
            actions[a] = d
        self.gameState.update_state(actions)
        self.grid.update(self.gameState)  # Show changes on the graphical interface

    def new_map(self):
        """
        Change the map (randomly)
        """
        self.map.reset(random=True)
        # Place the agents in their bases on the map
        self._reset_pos_agents()
        self.gameState.set_map(self.map)
        # Show changes on the graphical interface
        self.grid.set_map(self.map)
        self.grid.update(self.gameState)

    def run_simu(self):
        """
        Launch the simulation
        """
        choice = SimuChoiceView(self.appView)
        choice.set_listener(self)
        choice.show()
            
    def run_random_simu(self):
        """
        Launch a random simulation
        """
        if self.simu_thread is None or not self.simu_thread.is_alive():
            self.running = True
            self.simu_thread = thr.Thread(target=self._run_random_simu, name="simu_thread", args=[self.speed_simu], daemon=True)
            self.simu_thread.start()
            
    def run_trained_simu(self):
        """
        Launch a simulation using the trained ML model
        """
        try:
            dir = fd.askdirectory(initialdir="../weights_rl")
            for decision_agent_name, decision_agent in self.decisionAgents.items():
                decision_agent: Agent
                decision_agent.load(f"{dir}/{decision_agent_name}.weights.h5")
        except:
            msg.showwarning("Error in model loading",
                            "No suitable models were found. Please train the model before running the simulation. By default, the simulation will be run with the untrained model")
        if self.simu_thread is None or not self.simu_thread.is_alive():
            self.running = True
            self.simu_thread = thr.Thread(target=self._run_trained_simu, name="simu_thread", args=[self.speed_simu], daemon=True)
            self.simu_thread.start()

    def _run_random_simu(self, speed):
        """
        Run a random simulation
        """
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
        """
        Run a simulation using the trained ML model
        """              
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
        """
        Stop the simulation
        """
        self.running = False

    def save_map(self):
        """
        Save the current map
        """
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
        """
        Load an existing map
        """
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
        """
        Reset the position and the hp of all agents
        """
        for a in self.agents.keys():
            self.agents[a]["position"] = self.map.agents_bases[a]["position"]
            self.agents[a]["hp"] = self.agents[a]["hpMax"]
            
    def reset(self):
        """
        Reset the state of the agents, the gamestate and the grid (the visualisation)
        """
        self._reset_pos_agents()
        self.gameState.set_map(self.map)
        self.grid.update(self.gameState)
