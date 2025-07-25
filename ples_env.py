from perlin_noise import PerlinNoise
from ples_plants import Plant
import random

def mapValue(value, min_val, max_val, oMin_val=0.0, oMax_val=1.0):
    if oMax_val == oMin_val:
        raise ValueError("Intervallo originale non valido: massimo e minimo uguali")
    t = (value - oMin_val) / (oMax_val - oMin_val)
    mapped_val = t * (max_val - min_val) + min_val
    return mapped_val
def squashTowardsZero(x, factor=4):
    return x**factor

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
        self.cells, self.plants = self.generateEnvironment()
        self.luminosity = 1.0

    def generateEnvironment(self):
        noise = PerlinNoise(self.octaves, self.seed)
        noise_map = [
            [noise([x / self.width, y / self.height]) for x in range(self.width*3)]
            for y in range(self.height)
        ]
        cells=[]
        for y in range(self.height):
            row = []
            for x in range(self.width):
                height = noise_map[y][x]
                temperature = noise_map[y][x+self.width]
                UGW=(noise_map[y][x+self.width*2]+1)/2
                cell_type= self.getCellType(height, temperature)
                cell = {
                    "type": cell_type,
                    "temperature": temperature,
                    "height": height,
                    "waterUnder":UGW
                }
                row.append(cell)
            cells.append(row)

        plants=[]
        for i in range(10):
            x=random.randint(0,self.width-1)
            y=random.randint(0,self.height-1)
            behaviours={
                "Thresholds":{
                    "Water":random.random(),
                    "Stress": random.random()
                },
                "onWet": {
                    "deepening": (random.random()-1)/10
                },
                "onDry": {
                    "deepening": (random.random()-1)/10
                }
            }
            plants.append(Plant(x,y,behaviours, cells, starter=True))
        return cells, plants

    def getCellType(self, value, temp):
        if value < self.limits[0]:
            return "water"
        elif value < self.limits[1]:
            return "sand"
        elif value < self.limits[2]:
            if temp<-0.2:
                return "dirt"
            else:
                return "grassyDirt"
        else:
            return "mountain"

    def updateLuminosity(self, luminosity):
        self.luminosity = luminosity



