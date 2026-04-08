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
    sim = Sim(_world_w=500, _world_h=333, _world_type=world_type)
    ui = UI(sim, env_width=sim.world_w, env_height=sim.world_h, _s_w=1500, _s_h=999, _world_type=world_type)
elif choice=='load_world':
    sim = Sim(_world_w=500, _world_h=333, _world_type=world_type,_world_info=world_info)
    ui = UI(sim,  env_width=sim.world_w, env_height=sim.world_h, _s_w=1500, _s_h=999, _world_type=world_type)
else:
    print('Not Create World')
    sim = Sim(_world_w=500, _world_h=333, _world_type='continental')
    ui = UI(sim, env_width=sim.world_w, env_height=sim.world_h, _s_w=1500, _s_h=999, _world_type='continental')

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
