from ples_env import Env
from ples_plants import Plant
import json
file_mondo="world.json"
class Sim:
    def __init__(self,_wW,_wH,_timeRate,_worldType,_worldInfo=(None,None)):
        self.wW=_wW
        self.wH=_wH
        self.env = Env(self.wW, self.wH, _worldType,_worldInfo[0],_worldInfo[1])
        self.timerate=_timeRate
        self.frame=0
        self.mHour=72
        self.worldType=_worldType

    def run(self):
        self.updateTime()
        self.env.plants = [Plant for Plant in self.env.plants if Plant.update()]

    def salva_mondo(self):
        item = {
            "seed": self.env.seed,
            "octaves": self.env.octaves,
        }

        with open(file_mondo, "w") as f:
            json.dump(item, f, indent=2)

        print(f"Mondo salvato con successo in {file_mondo}")


    def updateTime(self):
        self.frame+=1
        if self.frame % 1 == 0:
            self.mHour+=1
            self.dHour=self.mHour%96

    def updateLuminosity(self, luminosity):
        self.env.updateLuminosity(luminosity)

    def getTime(self):
        return self.mHour

