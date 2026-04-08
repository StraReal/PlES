import random
from ples_env import Env
import json,os
from collections import deque

world_folder="worlds"
class Sim:
    def __init__(self,_world_w,_world_h,_world_type,_world_info=(None,None)):
        self.world_w=_world_w
        self.world_h=_world_h
        self.env = Env(self.world_w, self.world_h, _world_type,_world_info[1],_world_info[0])
        self.frame=0
        self.time = 72
        self.day = 0
        self.worldType=_world_type
        self.light, self.l_strength = self.get_sky_color(self.time)
        self.l_strength = self.l_strength / 2
        self.luminosity = self.rgb_into_luminosity(self.light)
        self.plant_id_counts = {}
        self.population_history = deque(maxlen=100)
        self.active_events = {}

    @staticmethod
    def interpolate_color(color1, color2, t):
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
        self.tick_events()
        self.env.random_tick(positions, self.active_events)
        if not self.time % 10:
            self.plant_id_counts = {}
            for plant in self.env.plants:
                if plant.fam_id in self.plant_id_counts:
                    self.plant_id_counts[plant.fam_id] += 1
                else:
                    self.plant_id_counts[plant.fam_id] = 1
            self.population_history.append(self.plant_id_counts.copy())
        self.time += 1
        self.day = self.time % 480

    def tick_events(self):
        # trigger events randomly
        if not any(e in self.active_events for e in "rain") and random.random() < 0.001:
            duration = random.randint(200, 800)
            self.active_events["rain"] = duration
            print(f"Rain started, lasting {duration} ticks")

        if not any(e in self.active_events for e in ("glaciation", "heatwave", "rain")) and random.random() < 0.0005:
                duration = random.randint(300, 1000)
                self.active_events["heatwave"] = duration
                print(f"Heatwave started, lasting {duration} ticks")

        if not any(e in self.active_events for e in ("glaciation", "heatwave", "rain")) and random.random() < 0.0001:
                duration = random.randint(3500, 8000)
                self.active_events["heatwave"] = duration
                print(f"Heatwave started, lasting {duration} ticks")

        #tick down active events
        for event in list(self.active_events):
            self.active_events[event] -= 1
            if self.active_events[event] <= 0:
                print(f"{event} ended")
                del self.active_events[event]

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
