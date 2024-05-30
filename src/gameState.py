import copy


def sign(x):
    if x >= 0:
        return 1
    else:
        return -1


class GameState:
    def __init__(self, grid_width, grid_height, grid) -> None:
        self.grid = grid
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.abs_grid = [["_" for j in range(grid_width)] for i in range(grid_height)]
        self.bases = None
        self.agents = None
        self.infos = {}

    def clear(self):
        self.abs_grid = [["_" for j in range(self.grid_width)] for i in range(self.grid_height)]

    def set_walls(self, walls_pos):
        for (x, y) in walls_pos:
            self.abs_grid[y][x] = "W"

    def set_ores(self, ores_pos):
        for (x, y) in ores_pos:
            self.abs_grid[y][x] = "R"

    def set_agents(self, agents: dict):
        self.agents = agents
        for a in agents.keys():
            x, y, _ = agents[a]
            self.abs_grid[y][x] = a
        self.get_infos(self.agents)

    def set_bases(self, bases):
        self.bases = copy.deepcopy(bases)

    def update_state(self, actions: dict):
        # template actions: {"agent1":["Move", "E"], "agent2":["Mine"], "agent3":["Move", "N"]}
        for a in actions.keys():
            if actions[a][0] == "Move":
                d = actions[a][1]
                self._movement(a, d)
        self.grid.show_agents(self.agents)
        self.get_infos(self.agents)

    def allies_around(self, agent):
        return self.infos[agent]["ally_pos"]

    def mine_around(self, agent):
        return self.infos[agent]["resource_pos"]

    def is_collision(self, position):
        x, y = position
        if self.abs_grid[y][x] == "W":
            return True
        return False

    def is_in_his_base(self, agent):
        return self.agents[agent] == self.bases[agent]

    def get_infos(self, agents: dict):
        self.infos.clear()
        for a in agents.keys():
            x, y, _ = agents[a]
            agents_pos = []
            resources_pos = []
            walls_pos = []
            self._observe_surrounding(position=(x, y), v_range=3, agents_pos=agents_pos, resources_pos=resources_pos,
                                      walls_pos=walls_pos)

            self.infos[a] = {"ally_pos": agents_pos, "resource_pos": resources_pos, "walls_pos": walls_pos}
        return self.infos

    def _movement(self, agent, direction):
        x, y, c = self.agents[agent]
        match direction:
            case "O":
                x -= 1
            case "E":
                x += 1
            case "N":
                y -= 1
            case "S":
                y += 1
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height or self.abs_grid[y][x] == "W" or \
                self.abs_grid[y][x] == "R":
            return False
        self.agents[agent] = (x, y, c)
        return True

    def _observe_surrounding(self, position, v_range: int, agents_pos: list, resources_pos: list, walls_pos: list):
        cx, cy = position
        other_agents = []
        for i in range(v_range):
            try:
                match self.abs_grid[cy][cx + i + 1]:
                    case "_":
                        pass  # nothing
                    case "R":
                        resources_pos.append((cx + i + 1, cy))
                    case "W":
                        walls_pos.append((cx + i + 1, cy))
                        break
                    case _:
                        agents_pos.append((cx + i + 1, cy))
            except:
                break

        for i in range(v_range):
            try:
                match self.abs_grid[cy][cx - i - 1]:
                    case "_":
                        pass  # nothing
                    case "R":
                        resources_pos.append((cx - i - 1, cy))
                    case "W":
                        walls_pos.append((cx - i - 1, cy))
                        break
                    case _:
                        agents_pos.append((cx - i - 1, cy))
            except:
                break

        for i in range(v_range):
            try:
                match self.abs_grid[cy + i + 1][cx]:
                    case "_":
                        pass  # nothing
                    case "R":
                        resources_pos.append((cx, cy + i + 1))
                    case "W":
                        walls_pos.append((cx, cy + i + 1))
                        break
                    case _:
                        agents_pos.append((cx, cy + i + 1))
            except:
                break

        for i in range(v_range):
            try:
                match self.abs_grid[cy - i - 1][cx]:
                    case "_":
                        pass  # nothing
                    case "R":
                        resources_pos.append((cx, cy - i - 1))
                    case "W":
                        walls_pos.append((cx, cy - i - 1))
                        break
                    case _:
                        agents_pos.append((cx, cy - i - 1))
            except:
                break

        """
        for i in range(-v_range, v_range+1):
            for j in range(-v_range, v_range+1):
                if cy + i >= len(self.abs_grid) or cy + i < 0 or cx + j >= len(self.abs_grid[0]) or cx + j < 0:
                    continue
                match self.abs_grid[cy+i][cx+j]:
                    case "_":
                        pass # nothing
                    case "R":
                        resources_pos.append((cx+j, cy+i))
                    case "W":
                        walls_pos.append((cx+j, cy+i))
                    case _:
                        agents_pos.append((cx+j, cy+i))
                        other_agents.append(self.abs_grid[cy+i][cx+j])

        # Verify that walls don't block the view
        self._verify_obstacle(position, resources_pos, walls_pos)
        self._verify_obstacle(position, agents_pos, walls_pos)
        """

    """ 
    def _verify_obstacle(self, position, objects: list, walls_pos: list):
        cx, cy = position
        for (rx, ry) in objects:
            if rx == cx: # same vertical line
                if ry > cy + 1:
                    for i in range(1, ry-cy):
                        if (cx, cy+i) in walls_pos:
                            objects.remove((rx, ry))
                elif ry < cy - 1:
                    for i in range(1, cy-ry):
                        if (cx, cy-i) in walls_pos:
                            objects.remove((rx, ry))
            elif ry == cy: # same horizontal line
                if rx > cx + 1:
                    for i in range(1, rx-cx):
                        if (cx+i, cy) in walls_pos:
                            objects.remove((rx, ry))
                elif rx < cx - 1:
                    for i in range(1, cx-rx):
                        if (cx-1, cy) in walls_pos:
                            objects.remove((rx, ry))
            #else:
            #    inside_trajectory = self._find_trajectory(agent_pos, (rx, ry))


    def _find_trajectory(agent_pos, object_pos):
        cx, cy = agent_pos
        rx, ry = object_pos
        trajectory = []
        dx = rx-cx
        dy = ry-cx
        if dx == dy or dx == -dy: # diagonal
            for i in range(abs(dx)):
                trajectory.append((cx+i*sign(dx), cy+(i+1)*sign(dy)))
                trajectory.append((cx+(i+1)*sign(dx), cy+i*sign(dy)))
                trajectory.append((cx+(i+1)*sign(dx), cy+(i+1)*sign(dy)))
    """