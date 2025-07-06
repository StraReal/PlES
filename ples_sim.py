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
        self.mHour=72
        self.worldType=_worldType

    def run(self):
        self.updateTime()
        self.env.plants = [Plant for Plant in self.env.plants if Plant.update()]

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

    def updateTime(self):
        self.frame+=1
        if self.frame % 1 == 0:
            self.mHour+=1
            self.dHour=self.mHour%96

    def updateLuminosity(self, luminosity):
        self.env.updateLuminosity(luminosity)

    def getTime(self):
        return self.mHour

