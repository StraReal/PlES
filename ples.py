import pygame

from ples_UI import UI
from ples_sim import Sim
import time

starting_ui = UI()
clock = pygame.time.Clock()
choice, world_type, world_info = None, None,None
while choice is None and world_type is None:
    starting_ui.detect_events()
    choice, world_type, world_info = starting_ui.draw_menu()
    clock.tick(60)

if choice=='create_world':
    sim = Sim(_wW=500, _wH=333, _timeRate=1.0, _worldType=world_type)
    ui = UI(sim, sim.env.cells, sim.env.plants, sim.wW, sim.wH, _sW=1500, _sH=999, _worldType=world_type)
elif choice=='load_world':
    sim = Sim(_wW=500, _wH=333, _timeRate=1.0, _worldType=world_type,_worldInfo=world_info)
    ui = UI(sim, sim.env.cells, sim.env.plants, sim.wW, sim.wH, _sW=1500, _sH=999, _worldType=world_type)
else:
    print('Not Create World')
    sim = Sim(_wW=500, _wH=333, _timeRate=1.0, _worldType='continental')
    ui = UI(sim, sim.env.cells, sim.env.plants,sim.wW, sim.wH, _sW=1500, _sH=999, _worldType='continental')

try:
    while True:
        start_time = time.perf_counter()
        ui.detect_events()
        sim.run()
        ui.update()
        elapsed_time = (time.perf_counter() - start_time) * 1000
        clock.tick(60)
except KeyboardInterrupt:
    print("Quit with Ctrl+C")
