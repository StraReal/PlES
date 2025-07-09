import copy
import random


def mutate(behaviour):
    d_m = behaviour.copy()
    for k, v in d_m.items():
        if isinstance(v, float):
            d_m[k] = v + random.random()
        elif isinstance(v, dict):
            d_m[k] = mutate(v)
    return d_m
class Plant:
    def __init__(self, x, y, behaviours, world, starter=False):
        self.x = x
        self.y = y
        self.id = id
        self.wet = 1 if starter else 0.5
        self.world=world
        cell = self.world[y][x]
        self.type = cell["type"]
        self.temp = cell["temperature"]
        self.UGW = cell["waterUnder"]
        self.cHeight = cell["height"]
        self.height = random.random() * 3 if starter else 0.1
        self.rootDepth = random.random() if starter else 0
        self.behaviours = behaviours
        self.stress = 0.0

    def update(self):
        self.wet+=(self.UGW*self.rootDepth)/10
        self.onDry()
        self.stress+=(0.5-self.wet)/10
        self.stress = max(0, min(self.stress, 1))
        if self.stress > self.behaviours["Thresholds"]["Stress"]:
            print(f'Plant {self.id} died')
            return False
        return True

    def onDry(self):
        if self.wet<self.behaviours["Thresholds"]["Water"]:
            self.deepenRoots(self.behaviours["onDry"]["deepening"])
        else:
            self.deepenRoots(self.behaviours["onWet"]["deepening"])

    def deepenRoots(self, deepening):
        self.rootDepth += deepening

    def produceSeeds(self):
        seeds = []
        num_seeds = random.randint(3, 7)

        for _ in range(num_seeds):
            new_behaviours = mutate(self.behaviours)
            dx = random.randint(-50, 50)
            dy = random.randint(-50, 50)
            new_x = max(0,self.x + dx)
            new_y = max(0,self.y + dy)
            seed = Plant(new_x, new_y,new_behaviours,self.world)
            seeds.append(seed)

        return seeds
