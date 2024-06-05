
import random
import copy
import os

MINIMUM_DISTANCE_BASES_RESOURCES = 3
MINIMUM_DISTANCE_BASES_WALLS = 0


class Map:
    """Create and store a game map
    """
    def __init__(self, random=False, width=20, height=20, num_walls=40, num_resource_ores=0, agent_bases:dict=None) -> None:
        """_summary_

        Args:
            random (bool, optional): Specify if the map must be generated randomly or not. Defaults to False.
            width (int, optional): The number of row in the new map. Ignored if random is set to False. Defaults to 20.
            height (int, optional): The number of column in the new map. Ignored if random is set to False. Defaults to 20.
            num_walls (int, optional): The number of walls in the new map. Ignored if random is set to False. Defaults to 20.
            num_resource_ores (int, optional): The number of resource ores in the new map. Ignored if random is set to False. Defaults to 2.
            agent_bases (dict, optional): _description_. Defaults to None.
        """
        self.agents_bases = copy.deepcopy(agent_bases)
        self.bases_positions = []
        if agent_bases:
            for a in agent_bases.keys():
                pos = agent_bases[a]["position"]
                self.bases_positions.append(pos)
        self.width = width
        self.height = height
        self.random = random
        self.num_walls = num_walls
        self.num_resource_ores = num_resource_ores
        
        self.walls_positions = []
        self.resources_positions = []
        
        if random:
            self.create_random_map()
        else:
            self.create_map_0()
            
    
    def reset(self, random=False, width=None, height=None, num_walls=None, num_resource_ores=None, agent_bases:dict=None):
        if agent_bases:
            self.agents_bases = copy.deepcopy(agent_bases)
            self.bases_positions.clear()
            for a in agent_bases.keys():
                pos = agent_bases[a]["position"]
                self.bases_positions.append(pos)
        if width:
            self.width = width
        if height:
            self.height = height
        if num_walls:
            self.num_walls = num_walls
        if num_resource_ores:
            self.num_resource_ores = num_resource_ores
            
        if random:
            self.create_random_map()
        else:
            self.create_map_0()
        
            
            
    def create_map_0(self):
        if self.width < 20 or self.height < 20:
                raise ValueError
        self.walls_positions = [(7, 9), (8, 9), (9, 9), (11, 9), (13, 9),
                            (7, 10), (9, 10), (11, 10), (13, 10),
                            (7, 11), (9, 11), (11, 11), (12, 11), (13, 11)]
        self.resources_positions = [(8, 10), (12, 10)]
            
            
    def create_random_map(self):
        self._place_resources()
        self._place_walls()
        
    
    def save(self, file):
        for y in range(20):
            for x in range(20):
                if (x, y) in self.bases_positions:
                    file.write("B, ")
                elif (x, y) in self.walls_positions:
                    file.write("W, ")
                elif (x, y) in self.resources_positions:
                    file.write("R, ")
                else:
                    file.write("_, ")
            file.write("\n")
        file.close()
        
    def load_filename(self, filename):
        if(os.path.exists(filename)):
            file = open(filename, "r")
            self.load(file)
        else:
            for dirpath, dirnames, filenames in os.walk("."):
                if filename in filenames:
                    p = os.path.join(dirpath, filename)
                    file = open(p, "r")
                    self.load(file)
                    break
                
        
        
        
    def load(self, file):
        self.bases_positions = []
        self.walls_positions = []
        self.resources_positions = []
        y = 0
        x = 0
        for line in file.readlines():
            line:str
            line = line.strip()
            row = line.split(",")
            for c in row:
                if c == "W" or c == " W" or c == "W ":
                    self.walls_positions.append((x, y))
                elif c == "R" or c == " R" or c == "W ":
                    self.resources_positions.append((x, y))
                elif c == "B" or c == " B" or c == "W ":
                    self.bases_positions.append((x, y))
                x += 1
            y += 1
            x = 0
        file.close()
        self._assign_bases_to_agents()
        
    
    def _assign_bases_to_agents(self):
        if self.agents_bases:
            if len(self.bases_positions) == len(self.agents_bases.keys()):
                for i, a in enumerate(self.agents_bases.keys()):
                    self.agents_bases[a]["position"] = self.bases_positions[i]
            else:
                raise Wrong_bases_number_error

    def _place_resources(self):
        # 1. Clear previous positions
        self.resources_positions.clear()
        
        # 2. Seach possible positions
        possible_positions = []
        for x in range(self.width):
            for y in range(self.height):
                valid_pos = True
                if self.bases_positions:
                    for (xb, yb) in self.bases_positions:
                        if abs(x - xb) <= MINIMUM_DISTANCE_BASES_RESOURCES and abs(y - yb) <= MINIMUM_DISTANCE_BASES_RESOURCES:
                            valid_pos = False
                if valid_pos:
                    possible_positions.append((x, y))
                    
        # 3. randomly select positions
        if len(possible_positions) < self.num_resource_ores:
            raise Resources_placement_error
        for i in range(self.num_resource_ores):
            pos = random.choice(possible_positions)
            self.resources_positions.append(pos)
            possible_positions.remove(pos)
            
            
    def _place_walls(self):
        # 1. Clear previous positions
        self.walls_positions.clear()
        
        # 2. Seach possible positions
        possible_positions = []
        for x in range(self.width):
            for y in range(self.height):
                valid_pos = True
                if self.bases_positions:
                    for (xb, yb) in self.bases_positions:
                        if abs(x - xb) <= MINIMUM_DISTANCE_BASES_WALLS and abs(y - yb) <= MINIMUM_DISTANCE_BASES_WALLS:
                            valid_pos = False
                if (x, y) in self.resources_positions:
                    valid_pos = False
                if valid_pos:
                    possible_positions.append((x, y))
        
        # 3. randomly select positions
        if len(possible_positions) < self.num_walls:
            raise Walls_placement_error
        p_positions = copy.copy(possible_positions)
        for i in range(self.num_walls):
            pos = random.choice(possible_positions)
            self.walls_positions.append(pos)
            possible_positions.remove(pos)
        
        # 4. Correct possible errors
        if self.bases_positions:
            c = 0
            while True:
                way_exists = True
                c+= 1
                if c == 2000: # avoid infinite loop
                    break
                for (xb, yb) in self.bases_positions:
                    for r_pos in self.resources_positions:
                        way_exists = self._find_way((xb, yb), r_pos, [])
                        if not way_exists:
                            break
                    if not way_exists:
                        break
                if not way_exists:           
                    possible_positions = copy.copy(p_positions)
                    self.walls_positions.append(pos)
                    for i in range(self.num_walls):
                        pos = random.choice(possible_positions)
                        self.walls_positions.append(pos)
                        possible_positions.remove(pos)
                else:
                    break
        
    
    def _find_way(self, position, goal, visited: list):
        if position == goal:
            return True
        visited.append(position)
        x, y = position
        if x+1 < self.width and (x+1, y) not in visited and (x+1, y) not in self.walls_positions:
            if(self._find_way((x+1, y), goal, visited)):
                return True
            
        if y+1 < self.height and (x, y+1) not in visited and (x, y+1) not in self.walls_positions:
            if(self._find_way((x, y+1), goal, visited)):
                return True
            
        if x-1 >= 0 and (x-1, y) not in visited and (x-1, y) not in self.walls_positions:
            if(self._find_way((x-1, y), goal, visited)):
                return True
            
        if y-1 >= 0 and (x, y-1) not in visited and (x, y-1) not in self.walls_positions:
            if(self._find_way((x, y-1), goal, visited)):
                return True
            
        return False

    
class Resources_placement_error(Exception):
    """Error in placement of resources
    """
    pass


class Walls_placement_error(Exception):
    """Error in placement of resources
    """
    pass


class Wrong_bases_number_error(Exception):
    """Difference between the number of bases and the number of agents
    """
    pass