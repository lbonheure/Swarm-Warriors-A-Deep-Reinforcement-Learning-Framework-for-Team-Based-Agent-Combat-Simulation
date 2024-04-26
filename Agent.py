import random

DIRECTIONS = ["N", "S", "W", "E"]

class Agent:
    def __init__(self, id=None, init_pos=None) -> None:
        self.pos_x = 0
        self.pos_y = 0
        if init_pos is not None:
            self.pos_x, self.pos_y = init_pos

        self.deplacement_capacity = random.randint(1,2)
    
    def move(self):
        for i in range(self.deplacement_capacity):
            d = self._choose_direction()
            match d:
                case "N":
                    self.pos_y += 1
                case "S":
                    self.pos_y -= 1
                case "W":
                    self.pos_x -= 1
                case "E":
                    self.pos_x += 1            
        return self.pos_x, self.pos_y

    def _choose_direction(self):
        # TODO need a policy
        return random.choice(DIRECTIONS)
    


class CombatAgent(Agent):
    def __init__(self, id=None, init_pos=None) -> None:
        super().__init__(id, init_pos)
        self.alive = True
        self.hp_max = 1000
        self.hp = 1000
        self.atk = 100

        self.heal_capacity = random.random()
        self.damage_capacity = 1 - self.heal_capacity

    def heal(self):
        return self.heal_capacity * self.atk
    
    def attack(self):
        return self.damage_capacity * self.atk

    def receive_damage(self, value):
        self.hp -= value
        if self.hp <= 0:
            self.alive = False

    def receive_heal(self, value):
        self.hp += value
        if self.hp >= self.hp_max:
            self.hp = self.hp_max

    def color(self):
        if self.hp > self.hp_max // 2:
            return "green"
        elif self.hp > self.hp_max // 4:
            return "yellow"
        elif self.hp > 0:
            return "red"
        else:
            return "black"


class ResourceAgent(Agent):
    def __init__(self, id=None, init_pos=None) -> None:
        super().__init__(id, init_pos)

        self.storage_size = 100
        self.store = 0

        self.mining_rate = random.random()
        self.deplacement_speed = 1 - self.mining_rate

    def mine(self, resource_left):
        r_mined = max(int(self.mining_rate * self.storage_size / 2), resource_left)
        if self.store + r_mined > self.storage_size:
            r_mined = self.storage_size - self.store
        self.store += r_mined
        return resource_left - r_mined
    
    def exchange_to(self, max_size):
        quantity = max(self.store, max_size)
        self.store -= quantity
        return quantity
    
    def exchange_from(self, quantity):
        self.store += quantity
        if self.store > self.storage_size:
            self.store = self.storage_size
            raise StorageOverload("max size of storage reached!")

    def resource_lim(self):
        return self.storage_size - self.store
    
    def move(self):
        if random.random() < self.deplacement_speed:
            super().move()


class StorageOverload(Exception):
    pass