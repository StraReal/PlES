from perlin_noise import PerlinNoise
from ples_plants import Plant
import random

RECHARGE_RATES = {
    "water":    0.005,
    "dirt":     0.004,
    "sand":     0.001,
    "mountain": 0.0005,
}
OPTIMAL_TEMP = 0.2

class Env:
    def __init__(self, _wW, _wH, _worldType, _seed,_octaves):
        self.width = _wW
        self.height = _wH
        self.gWetness = 0
        self.octaves:int=_octaves if _octaves else 8
        self.seed: int = _seed if _seed else random.randint(1, 10 ** 5)
        self.world_type=_worldType
        self.plant_id = 0
        if self.world_type=='Archipelago':
            self.limits = [0, 0.1, 0.35]
        elif self.world_type == 'Continental':
            self.limits = [-0.2, -0.1, 0.35]
        else:
            self.limits = [-0.2, -0.1, 0.35]
        self.cells = self.generate_environment()
        self.plants = []
        self.dirty = False

    def generate_environment(self):
        noise = PerlinNoise(self.octaves, self.seed)
        habitat_noise = PerlinNoise(2, self.seed+1)

        noise_map = [
            [noise([x / self.width, y / self.height]) for x in range(self.width * 3)]
            for y in range(self.height)
        ]
        habitat_map = [
            [habitat_noise([x / self.width, y / self.height]) for x in range(self.width)]
            for y in range(self.height)
        ]

        cells = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                height = noise_map[y][x]
                temperature = noise_map[y][x + self.width] + habitat_map[y][x] * 2
                temperature = max(-1.0, min(1.0, temperature))
                water_under = (noise_map[y][x + self.width * 2] + 1) / 2
                cell_type, grass = self.get_cell_type(height, temperature)
                cell = {
                    "type": cell_type,
                    "temperature": temperature,
                    "tempDrift": 0.0,
                    "height": height,
                    "waterUnder": water_under,
                    "grass": grass
                }
                row.append(cell)
            cells.append(row)

        return cells

    def create_plant(self, x=None, y=None, world=None, add_to_world=False):
        if x is None:
            x = random.randint(0, self.width - 1)
        if y is None:
            y = random.randint(0, self.height - 1)
        if self.cells[y][x]["type"] == "water":
            return None
        if world is None:
            world = self.cells
        behaviours = {
            "Thresholds": {
                "Water": random.uniform(0.2, 0.6),
                "Stress": random.uniform(0.5, 0.9)
            },
            "onWet": {"deepening": random.uniform(-0.05, 0.0)},
            "onDry": {"deepening": random.uniform(0.0, 0.05)},

            "Preferences": {
                "OptimalTemp": random.uniform(-1.0, 1.0),
                "TempTolerance": random.uniform(0.1, 0.4),
                "OptimalWater": random.uniform(0.0, 1.0),
                "WaterTolerance": random.uniform(0.1, 0.4),
            }
        }
        p = Plant(x, y, behaviours, world, starter=True, species=self.plant_id)
        self.plant_id += 1
        if add_to_world:
            self.plants.append(p)
            p.add_to_founders()
        return p

    def get_cell_type(self, value, temp):
        if value < self.limits[0]:
            return "water", False
        elif value < self.limits[1]:
            return "sand", False
        elif value < self.limits[2]:
            return "dirt", 0.3>temp>-0.15
        else:
            return "mountain", False

    def random_tick(self, positions, active_events, luminosity):
        if active_events is None:
            active_events = {}

        rain = "rain" in active_events
        heatwave = "heatwave" in active_events
        glaciation = "glaciation" in active_events

        for x, y in positions:
            cell = self.cells[y][x]

            base_rate = RECHARGE_RATES.get(cell["type"], 0.001)
            temp_factor = max(0.0, 1.0 - ((cell["temperature"]+cell["tempDrift"] - OPTIMAL_TEMP) ** 2) * 2)
            recharge = base_rate * temp_factor * 10

            if rain:
                recharge *= 4.0
                cell["tempDrift"] = cell["tempDrift"] - 0.0015
                self.dirty = True
            if heatwave:
                recharge *= 0.3
                cell["tempDrift"] = cell["tempDrift"] + 0.004
                self.dirty = True
            if glaciation:
                recharge *= 0.7
                cell["tempDrift"] = cell["tempDrift"] - 0.006
                self.dirty = True
            if abs(cell["tempDrift"])>0.02:
                cell["tempDrift"] = cell["tempDrift"] * 0.99
                self.dirty = True

            cell["waterUnder"] = min(1.0, cell["waterUnder"] + recharge)

            if cell["grass"] and (random.uniform(0, cell["waterUnder"]) > 0.3 or random.random() > 0.99) and (random.uniform(0, luminosity) > 0.2):
                exx = random.randint(-1, 1)
                exy = 0
                if not exx:
                    exy = random.choice([-1, 1])
                nx, ny = x + exx, y + exy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not self.cells[ny][nx]["grass"]:
                        self.cells[ny][nx]["grass"] = True
                        self.dirty = True
                if random.random() < 0.0001:
                    self.create_plant(x=x, y=y, add_to_world=True)

        new_plants = []

        tick_plants = random.sample(self.plants, len(self.plants) // 5)
        tick_set = set(id(p) for p in tick_plants)
        alive = [p for p in self.plants if id(p) not in tick_set]
        for plant in tick_plants:
            if plant.update(luminosity, tick_rate=4.5):
                alive.append(plant)
                if random.random() < 0.001:
                    new_plants.extend(plant.produce_seeds())

        for seed in new_plants:
            if 0 <= seed.x < self.width and 0 <= seed.y < self.height:
                alive.append(seed)

        self.plants = alive