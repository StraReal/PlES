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

def pair(a, b):
    return (a + b) * (a + b + 1) // 2 + b

def genetic_distance(b1, b2):
    dist = 0.0
    for k, v in b1.items():
        if isinstance(v, float):
            dist += abs(v - b2[k])
        elif isinstance(v, dict):
            dist += genetic_distance(v, b2[k])
    return dist

_next_family = 0
_family_founders = {}  # family_id : founder behaviours

def new_family_id(behaviours, species):
    global _next_family
    _next_family += 1
    fam_id = pair(species, _next_family)
    _family_founders[fam_id] = behaviours
    return _next_family

SPECIATION_THRESHOLD = 1.5

class Plant:
    def __init__(self, x, y, behaviours, world, starter=False, species=0, family=0):
        self.x = x
        self.y = y
        self.species = species
        self.family = family
        self.fam_id = pair(species, family)
        self.world = world
        self.cell = self.world[y][x]
        self.type = self.cell["type"]
        self.temp = self.cell["temperature"]
        self.underground_water = self.cell["waterUnder"]
        self.c_height = self.cell["height"]
        self.wet = 1.0 if starter else 0.5
        self.height = random.random() * 3 if starter else 0.1
        self.root_depth = random.random() if starter else 0.0
        self.behaviours = behaviours
        self.stress = 0.0
        self.age = 0

    def update(self, luminosity, tick_rate=1):
        self.age += tick_rate

        water_gain = self.get_water_from_roots() * tick_rate
        evaporation = (0.005 + (luminosity * 0.01) + max(0, (self.temp+self.cell["tempDrift"]) * 0.005)) * tick_rate
        self.wet = max(0.0, min(1.0, self.wet + water_gain - evaporation))

        self.deepen_roots()

        self.stress = max(0.0, min(1.0, self.stress + ((0.4 - self.wet) / 20) * tick_rate))

        prefs = self.behaviours["Preferences"]
        temp_delta = abs(self.temp+self.cell["tempDrift"] - prefs["OptimalTemp"])
        if temp_delta > prefs["TempTolerance"]:
            temp_stress = (temp_delta - prefs["TempTolerance"]) * 0.15 * tick_rate
            self.stress = max(0.0, min(1.0, self.stress + temp_stress))

        water_delta = abs(self.underground_water - prefs["OptimalWater"])
        if water_delta > prefs["WaterTolerance"]:
            water_stress = (water_delta - prefs["WaterTolerance"]) * 0.15 * tick_rate
            self.stress = max(0.0, min(1.0, self.stress + water_stress))

        if self.type in ("water", "mountain"):
            self.stress += 0.02 * tick_rate

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
        for _ in range(random.randint(1, 4)):
            new_behaviours = mutate(self.behaviours)
            dx = random.randint(-50, 50)
            dy = random.randint(-50, 50)
            new_x = min(max(0, self.x + dx), world_w - 1)
            new_y = min(max(0, self.y + dy), world_h - 1)
            if self.world[new_y][new_x]["type"] == "water":
                continue

            dist = genetic_distance(new_behaviours, _family_founders[self.fam_id])
            if dist > SPECIATION_THRESHOLD:
                new_family = new_family_id(new_behaviours, self.species)
                print(f"family {new_family} arose in {self.species}")
            else:
                new_family = self.family

            seeds.append(Plant(new_x, new_y, new_behaviours, self.world,
                               species=self.species, family=new_family))
        return seeds

    def add_to_founders(self):
        _family_founders[self.fam_id] = self.behaviours