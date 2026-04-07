import copy
import random

def mutate(behaviour):
    d_m = behaviour.copy()
    for k, v in d_m.items():
        if isinstance(v, float):
            d_m[k] = v + random.gauss(0, 0.05)
            d_m[k] = max(0.0, min(1.0, d_m[k]))
        elif isinstance(v, dict):
            d_m[k] = mutate(v)
    return d_m

class Plant:
    def __init__(self, x, y, behaviours, world, starter=False, id_num=0):
        self.x = x
        self.y = y
        self.id = id_num
        self.world = world
        cell = self.world[y][x]
        self.type = cell["type"]
        self.temp = cell["temperature"]
        self.underground_water = cell["waterUnder"]
        self.c_height = cell["height"]
        self.wet = 1.0 if starter else 0.5
        self.height = random.random() * 3 if starter else 0.1
        self.root_depth = random.random() if starter else 0.0
        self.behaviours = behaviours
        self.stress = 0.0
        self.age = 0

    def update(self, luminosity):
        self.age += 1

        water_gain = self.get_water_from_roots()
        evaporation = 0.005 + (luminosity * 0.01) + max(0, self.temp * 0.005)
        self.wet = max(0.0, min(1.0, self.wet + water_gain - evaporation))

        self.deepen_roots()

        self.stress = max(0.0, min(1.0, self.stress + (0.4 - self.wet) / 20))

        prefs = self.behaviours["Preferences"]
        temp_delta = abs(self.temp - prefs["OptimalTemp"])
        if temp_delta > prefs["TempTolerance"]:
            temp_stress = (temp_delta - prefs["TempTolerance"]) * 0.15
            self.stress = max(0.0, min(1.0, self.stress + temp_stress))

        water_delta = abs(self.underground_water - prefs["OptimalWater"])
        if water_delta > prefs["WaterTolerance"]:
            water_stress = (water_delta - prefs["WaterTolerance"]) * 0.15
            self.stress = max(0.0, min(1.0, self.stress + water_stress))

        if self.type in ("water", "mountain"):
            self.stress += 0.02

        if self.stress > self.behaviours["Thresholds"]["Stress"]:
            return False
        return True

    def deepen_roots(self):
        if self.wet < self.behaviours["Thresholds"]["Water"]:
            deepening = self.behaviours["onDry"]["deepening"]
        else:
            deepening = self.behaviours["onWet"]["deepening"]
        self.root_depth = max(0.0, min(1.0, self.root_depth + deepening))

    def get_water_from_roots(self):
        radius = self.root_depth * 7  # 0.0 -> 0 tiles, 1.0 -> 4 tiles
        total_water = 0.0

        for dy in range(-4, 5):
            for dx in range(-4, 5):
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist > radius:
                    continue

                nx, ny = self.x + dx, self.y + dy
                if not (0 <= nx < len(self.world[0]) and 0 <= ny < len(self.world)):
                    continue

                cell = self.world[ny][nx]
                available = cell["waterUnder"]
                if available <= 0:
                    continue

                falloff = max(0.0, 1.0 - (dist / (radius + 0.001))) ** 2
                drawn = min(available * falloff * 0.1, available)
                cell["waterUnder"] = max(0.0, available - drawn)
                total_water += drawn

        return total_water

    def should_seed(self):
        return self.age > 100 and self.stress < 0.3 and random.random() < 0.002

    def produce_seeds(self):
        seeds = []
        world_h = len(self.world)
        world_w = len(self.world[0])
        for _ in range(random.randint(3, 7)):
            new_behaviours = mutate(self.behaviours)
            dx = random.randint(-50, 50)
            dy = random.randint(-50, 50)
            new_x = min(max(0, self.x + dx), world_w - 1)
            new_y = min(max(0, self.y + dy), world_h - 1)
            seeds.append(Plant(new_x, new_y, new_behaviours, self.world, id_num=0))
        return seeds