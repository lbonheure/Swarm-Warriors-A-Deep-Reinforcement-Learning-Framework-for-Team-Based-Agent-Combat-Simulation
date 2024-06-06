import copy

from map import Map
from Agent import CombatAgent


def sign(x):
    if x >= 0:
        return 1
    else:
        return -1


class GameState:
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
        #self.get_infos(self.agents)

    def update_state(self, actions: dict):
        # template actions: {"agent1":"N", "agent2":"A", "agent3":"E"}
        move_set = ["N", "S", "W", "E"]
        rewards = {}
        for a in actions.keys():  # Movement action of the agent
            if actions[a] != "A" and actions[a] in move_set:
                d = actions[a]
                rewards[a] = self._movement(a, d)

        for a in actions.keys():  # Attack action of the agent
            if actions[a] == "A":
                rewards[a] = self._atk(self.agents[a])

        for a in actions.keys():  # no action -> dead agent
            if actions[a] != "A" and actions[a] not in move_set:
                rewards[a] = 0

        self.get_infos(self.agents)
        return rewards

    #def is_in_his_base(self, agent):
    #    return self.agents[agent] == self.bases[agent]

    def get_infos(self, agents: dict):
        self.infos.clear()
        for a in agents.keys():
            (x, y) = agents[a]["position"]
            self.infos[a] = self._observe_surrounding(position=(x, y), v_range=3)
        return self.infos

    def _atk(self, agent):
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
                        if self.agents[target]["AI"].color == da.color:
                            reward -= 10  # -10 points per hit ally
                        else:
                            reward += 10 # +10 points per hit ennemy
                        # TODO reward + en cas de kill et reward - pour l'agent qui meurt
        if not hit:
            reward -= 1  # -1 point if no hit
        return reward

    def _movement(self, agent, direction):
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
        if x < 0 or x >= self.map.width or y < 0 or y >= self.map.height or self.abs_grid[y][x] != "_": # Move only in the grid and to free cells
            return 0 # reward = 0 if no move
        # TODO verifier synchro abs_grid et position agent
        self.abs_grid[yp][xp] = "_"
        self.abs_grid[y][x] = agent
        self.agents[agent]["position"] = (x, y)
        #print("move", agent, "from", (xp, yp), "to", (x, y), "abs_grid value=", self.abs_grid[y][x])
        return 1 # reward = 1 if move

    def _observe_surrounding(self, position, v_range=3):
        cx, cy = position
        da_self = self.agents[self.abs_grid[cy][cx]]["AI"]
        agents_pos, resources_pos, walls_pos = [], [], []

        def get_relevant_positions(distance=3):
            return [(x, y) for x in range(-distance, distance + 1)
                    for y in range(-distance, distance + 1)
                    if abs(x) + abs(y) <= distance and (x, y) != (0, 0)]

        def check_position(x, y):
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
            else:
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
        print("create_abs_grid_from_map")
        abs_grid = [["_" for j in range(map.width)] for i in range(map.height)]
        for (x, y) in map.walls_positions:
            abs_grid[y][x] = "W"
        for (x, y) in map.resources_positions:
            abs_grid[y][x] = "R"
        self.bases = map.agents_bases
        for a in self.bases.keys():
            # print(self.bases[a])
            (x, y) = self.bases[a]["position"]
            abs_grid[y][x] = a
        return abs_grid
