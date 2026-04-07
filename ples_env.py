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
        if self.world_type=='Archipelago':
            self.limits = [0, 0.1, 0.35]
        elif self.world_type == 'Continental':
            self.limits = [-0.2, -0.1, 0.35]
        else:
            self.limits = [-0.2, -0.1, 0.35]
        self.cells, self.plants = self.generate_environment()
        self.luminosity = 1.0

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
                    "height": height,
                    "waterUnder": water_under,
                    "grass": grass
                }
                row.append(cell)
            cells.append(row)

        plants=[]
        for i in range(10):
            plants.append(self.create_plant(world=cells))
        return cells, plants

    def create_plant(self, x=None, y=None, world=None, add_to_world=False):
        if x is None:
            x = random.randint(0, self.width - 1)
        if y is None:
            y = random.randint(0, self.height - 1)
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
        p = Plant(x, y, behaviours, world, starter=True)
        if add_to_world:
            self.plants.append(p)
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

    def update_luminosity(self, luminosity):
        self.luminosity = luminosity

    def random_tick(self, positions):
        for x, y in positions:
            cell = self.cells[y][x]

            base_rate = RECHARGE_RATES.get(cell["type"], 0.001)
            temp_factor = max(0.0, 1.0 - ((cell["temperature"] - OPTIMAL_TEMP) ** 2) * 2)
            cell["waterUnder"] = min(1.0, cell["waterUnder"] + base_rate * temp_factor * 10)

            if cell["grass"] and (random.uniform(0, cell["waterUnder"]) > 0.3 or random.random() > 0.99) and (random.uniform(0, self.luminosity) > 0.2):
                exx = random.randint(-1, 1)
                exy = 0
                if not exx:
                    exy = random.choice([-1, 1])
                nx, ny = x + exx, y + exy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.cells[ny][nx]["grass"] = True
                if random.random() < 0.0001:
                    self.create_plant(x=x, y=y, add_to_world=True)