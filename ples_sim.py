import random

from ples_env import Env
from ples_plants import Plant
import json,os
world_folder="worlds"
class Sim:
    def __init__(self,_wW,_wH,_timeRate,_worldType,_worldInfo=(None,None)):
        self.wW=_wW
        self.wH=_wH
        print(_worldType,_worldInfo[0],_worldInfo[1])
        self.env = Env(self.wW, self.wH, _worldType,_worldInfo[1],_worldInfo[0])
        self.timerate=_timeRate
        self.frame=0
        self.time = 72
        self.day = 0
        self.worldType=_worldType
        self.light, self.l_strength = self.get_sky_color(self.time)
        self.l_strength = self.l_strength / 2
        self.luminosity = self.rgb_into_luminosity(self.light)

    @staticmethod
    def interpolate_color(color1, color2, t):
        if t>1:
            print(t)
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * t)
            for i in range(3)
        )

    def get_sky_color(self, time):
        t = time % 480

        day = (200, 220, 255)
        night = (10, 10, 30)
        sunset = (255, 140, 60)

        if t < 100:
            return night,1
        elif t < 140:
            factor = (t - 100) / 40
            return self.interpolate_color(night, sunset, factor),1-factor
        elif t < 160:
            factor = (t - 140) / 20
            return self.interpolate_color(sunset, day, factor),(1-factor)*0.1
        elif t < 360:
            return day, 0
        elif t < 380:
            factor = (t - 360) / 20
            return self.interpolate_color(day, sunset, factor),factor/2
        elif t < 420:
            factor = (t - 380) / 40
            return self.interpolate_color(sunset, night, factor),(factor/2)+0.45
        else:
            return night,1

    @staticmethod
    def rgb_into_luminosity(color):
        r,g,b=color
        return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

    def run(self):
        self.light, self.l_strength = self.get_sky_color(self.time)
        self.l_strength = self.l_strength / 2
        self.luminosity = self.rgb_into_luminosity(self.light)
        self.env.update_luminosity(self.luminosity)
        l = int(self.env.width * self.env.height * 0.05)
        positions = [(random.randint(0, self.env.width - 1), random.randint(0, self.env.height - 1)) for _ in range(l)]
        self.env.random_tick(positions)
        self.time += 1
        self.day = self.time % 480
        alive = []
        new_plants = []
        for plant in self.env.plants:
            if plant.update(self.luminosity):
                alive.append(plant)
                if random.random() < 0.001:
                    new_plants.extend(plant.produce_seeds())
        for seed in new_plants:
            if 0 <= seed.x < self.wW and 0 <= seed.y < self.wH:
                alive.append(seed)
        self.env.plants = alive

    def save_world(self):
        folder = "worlds"
        os.makedirs(folder, exist_ok=True)
        i = 1
        while os.path.exists(os.path.join(folder, f"world{i}.json")):
            i += 1

        filepath = os.path.join(folder, f"world{i}.json")

        item = {
            "seed": self.env.seed,
            "octaves": self.env.octaves,
            "world_type": self.env.world_type
        }

        with open(filepath, "w") as f:
            json.dump(item, f, indent=2)

        print(f"Succesfully saved world to {filepath}")
