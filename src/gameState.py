import copy

from map import Map
from Agent import CombatAgent


def sign(x):
    if x >= 0:
        return 1
    else:
        return -1


class GameState:
    """
    Class representing the actual state of the game and containing all the action that can happen inside
    """

    def __init__(self, map: Map = None, agents=None) -> None:
        self.map = map
        self.abs_grid = []
        if self.map:
            self.abs_grid = self._create_abs_grid_from_map(self.map)
        self.bases = None
        self.agents = agents
        self.infos = {}

    def set_map(self, map: Map):
        self.map = map
        self.abs_grid = self._create_abs_grid_from_map(self.map)

    def set_agents(self, agents: dict):
        self.agents = agents
        for a in agents.keys():
            (x, y) = agents[a]["position"]
            self.abs_grid[y][x] = a

    def update_state(self, actions: dict):
        """
        Update the state off all agents with their corresponding action and return their reward
        :param actions: dictionary with agent and their actions
        :return: dictionary with agent and the reward corresponding to their action
        """
        # template actions: {"agent1":"N", "agent2":"A", "agent3":"E"}
        move_set = ["N", "S", "W", "E", "A"]
        rewards = {}
        for a in actions.keys():  # Movement action of the agent
            if actions[a] != "A" and actions[a]:
                d = actions[a]
                rewards[a] = [self._movement(a, d) if pos_act == d else 0 for pos_act in move_set]

        for a in actions.keys():  # Attack action of the agent
            if actions[a] == "A":
                d = actions[a]
                rewards[a] = [self._atk(self.agents[a]) if pos_act == d else 0 for pos_act in move_set]

        for a in actions.keys():  # no action -> dead agent
            if actions[a] != "A" and actions[a] not in move_set:
                rewards[a] = [0 for pos_act in move_set]

        return rewards

    def get_infos(self, agents: dict):
        """
        Check the information about the surrounding of the agents
        :param agents:
        :return: Dictionary with information of all the agents
        """
        self.infos.clear()
        for a in agents.keys():
            (x, y) = agents[a]["position"]
            self.infos[a] = self._observe_surrounding(position=(x, y), v_range=3)
        return self.infos

    def _atk(self, agent):
        """
        Apply the attack of an agent
        :param agent:
        :return: Reward of the attack
        """
        da = agent["AI"]
        da: CombatAgent
        r_atk = da.get_range()
        atk = da.get_atk()
        (x, y) = agent["position"]
        hit = False
        reward = 0
        for i in range(-r_atk, r_atk + 1):
            for j in range(-r_atk, r_atk + 1):
                xo = x + i
                yo = y + j
                if xo < 0 or xo >= self.map.width or yo < 0 or yo >= self.map.height:
                    continue
                if (abs(xo - x) == r_atk and abs(yo - y) <= r_atk) or (abs(xo - x) <= r_atk and abs(yo - y) == r_atk):
                    if self.abs_grid[yo][xo] != "W" and self.abs_grid[yo][xo] != "R" and self.abs_grid[yo][xo] != "_":
                        target = self.abs_grid[yo][xo]
                        self.agents[target]["hp"] -= atk
                        hit = True
                        if self.agents[target]["AI"].get_color() == da.get_color():
                            reward -= 15  # -15 points per hit ally
                        elif self.agents[target]["hp"] <= 0:
                            reward += 20  # +20 points per killed ennemy
                        else:
                            reward += 10  # +10 points per hit ennemy
        if not hit:
            reward -= 0.1  # -0.1 point if no hit
        return reward

    def _movement(self, agent, direction):
        """
        Apply the movement of the agent given its direction
        :param agent:
        :param direction:
        :return: Reward corresponding to the move
        """
        (x, y) = self.agents[agent]["position"]
        xp = x
        yp = y
        match direction:
            case "W":
                x -= 1
            case "E":
                x += 1
            case "N":
                y -= 1
            case "S":
                y += 1
        if x < 0 or x >= self.map.width or y < 0 or y >= self.map.height or self.abs_grid[y][
            x] != "_":  # Move only in the grid and to free cells
            return -1  # reward = -1 if no move
        self.abs_grid[yp][xp] = "_"
        self.abs_grid[y][x] = agent
        self.agents[agent]["position"] = (x, y)
        return 0  # reward = 0 if move

    def _observe_surrounding(self, position, v_range=3):
        """
        Check for information in a certain range around the agent
        :param position:
        :param v_range: limitation of the agent sight
        :return: information observed
        """
        cx, cy = position
        da_self = self.agents[self.abs_grid[cy][cx]]["AI"]
        agents_pos, resources_pos, walls_pos = [], [], []

        def get_relevant_positions(distance=3):
            """
            Search only in place the agent can perceive information
            """
            return [(x, y) for x in range(-distance, distance + 1)
                    for y in range(-distance, distance + 1)
                    if abs(x) + abs(y) <= distance and (x, y) != (0, 0)]

        def check_position(x, y):
            """
            Check what is in a specific position
            :param x:
            :param y:
            :return: number corresponding to the element observed
            """
            if x < 0 or y < 0 or y >= len(self.abs_grid) or x >= len(self.abs_grid[0]):
                return -1  # Outside grid
            cell = self.abs_grid[y][x]
            if cell == "_":
                return 0  # Nothing
            elif cell == "W":
                walls_pos.append((x, y))
                return 1  # Wall
            elif cell == "R":
                resources_pos.append((x, y))
                return 2  # Resource
            else:  # Found an agent
                da_other = self.agents[cell]["AI"]
                da: CombatAgent
                color_other = da_other.get_color()
                r_other = da_other.get_range()

                color_self = da_self.get_color()
                if color_self == color_other:
                    if r_other == 1:
                        return 3
                    if r_other == 2:
                        return 4
                else:
                    if r_other == 1:
                        return 5
                    if r_other == 2:
                        return 6

                agents_pos.append((x, y))
                return 3  # Agent

        relevant_positions = get_relevant_positions(v_range)
        surrounding_info = [check_position(cx + dx, cy + dy) for dx, dy in relevant_positions]

        return surrounding_info

    def _create_abs_grid_from_map(self, map: Map):
        """
        Generate the environment were the action will take place
        :param map:
        :return: None
        """
        abs_grid = [["_" for j in range(map.width)] for i in range(map.height)]
        for (x, y) in map.walls_positions:
            abs_grid[y][x] = "W"
        for (x, y) in map.resources_positions:
            abs_grid[y][x] = "R"
        self.bases = map.agents_bases
        for a in self.bases.keys():
            (x, y) = self.bases[a]["position"]
            abs_grid[y][x] = a
        return abs_grid
