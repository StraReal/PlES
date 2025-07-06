import copy
import random
class Plant:
    def __init__(self, x, y, type, height, cellHeight, undergroundWater, temp, id, rootDepth, water, behaviours):
        self.x = x
        self.y = y
        self.gType = type
        self.temp = temp
        self.id = id
        self.height = height
        self.cHeight = cellHeight
        self.UGW = undergroundWater
        self.rootDepth = rootDepth
        self.wet = water
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
            new_behaviours = self.mutate_behaviour(copy.deepcopy(self.behaviours))
            dx = random.randint(-50, 50)
            dy = random.randint(-50, 50)
            new_x = max(0,self.x + dx)
            new_y = max(0,self.y + dy)

            seed = Plant(new_x, new_y, behaviours=new_behaviours, is_seed=True)
            seeds.append(seed)

        return seeds

    def mutate_behaviour(self, behaviour):
        for key in behaviour:
            if isinstance(behaviour[key], (int, float)):
                behaviour[key] *= random.uniform(0.95, 1.05)
        return behaviour