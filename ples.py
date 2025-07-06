from ples_UI import UI
from ples_sim import Sim
import time

ui = UI()
choice, worldType,worldInfo = None, None,None
while choice is None and worldType is None:
    ui.detectEvents()
    choice, worldType, worldInfo = ui.drawMainMenu()
    time.sleep(0.01)

if choice=='create_world':
    sim = Sim(_wW=500, _wH=333, _timeRate=1.0, _worldType=worldType)
    ui = UI(sim, sim.env.cells, sim.env.plants, sim.wW, sim.wH, _sW=1500, _sH=999, _worldType=worldType)
elif choice=='load_world':
    print(worldType,worldInfo)
    sim = Sim(_wW=500, _wH=333, _timeRate=1.0, _worldType=worldType,_worldInfo=(worldInfo))
    ui = UI(sim, sim.env.cells, sim.env.plants, sim.wW, sim.wH, _sW=1500, _sH=999, _worldType=worldType)
else:
    print('Not Create World')
    sim = Sim(_wW=500, _wH=333, _timeRate=1.0, _worldType='continental')
    ui = UI(sim, sim.env.cells, sim.env.plants,sim.wW, sim.wH, _sW=1500, _sH=999, _worldType='continental')

try:
    while True:
        start_time = time.perf_counter()
        ui.detectEvents()
        sim.run()
        ui.update()
        elapsed_time = (time.perf_counter() - start_time) * 1000
except KeyboardInterrupt:
    print("Uscita con Ctrl+C")
