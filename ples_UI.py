import random
import sys
import numpy as np
import pygame,os,json
from scipy.spatial import KDTree

def unpair(z):
    w = int((((8 * z + 1) ** 0.5) - 1) / 2)
    t = (w * w + w) // 2
    b = z - t
    a = w - b
    return a, b

class UI:
    def __init__(self, sim=None, env_width=1, env_height=1,_s_w=1,_s_h=1,_world_type=None):
        self.sim=sim
        if sim is not None:
            self.cells = sim.env.cells
        self.rows = env_height
        self.cols = env_width
        self.env_window_width=_s_w
        self.env_window_height=_s_h
        self.cell_width = _s_w // self.cols
        self.cell_height = _s_h // self.rows
        self.worldType=_world_type
        self.selected_option = None
        self.worlds_folder= "worlds"
        self.world_types = ["Continental", "Archipelago"]
        self.saved_worlds = [f for f in os.listdir(self.worlds_folder) if f.endswith(".json") and os.path.isfile(os.path.join(self.worlds_folder, f))]
        self.world_type_index = 0
        pygame.init()

        self.font = pygame.font.Font("assets/font/ari-w9500-bold.ttf", 20)
        self.big_font = pygame.font.Font("assets/font/ari-w9500-bold.ttf", 44)
        self.screen_w,self.screen_h=self.get_screen_sizes()
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        self.sidebar_w ,self.sidebar_h = (self.screen_w-self.env_window_width)//2, (self.screen_h-self.env_window_height)//2

        self.chButton=0
        self.selected_plant = None
        self.savefile_img = pygame.image.load("assets/SaveFile.png").convert_alpha()
        self.savefile_img = pygame.transform.scale(self.savefile_img, (35, 35))
        self.savefile_rect = pygame.Rect(self.screen_w - 40, self.screen_h - 40, 35, 35)
        self.show_graph=True
        self.col_seed_extra = random.randint(0, 120000)
        pygame.display.set_caption("PlES")
        self.family_colors = {}
        self.species_base_colors = {}
        self.family_first_seen = {}
        self.family_order = []
        self.map_type = 0

    @staticmethod
    def get_screen_sizes():
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h
        return width, height

    def handle_events(self, rects, arrow_rects):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.button == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if arrow_rects[1].collidepoint(event.pos):
                    if self.chButton != 0:
                        if self.world_type_index + 1 != len(self.world_types if self.chButton == 1 else self.saved_worlds):
                            self.world_type_index += 1
                        else:
                            self.world_type_index = 0
                elif arrow_rects[0].collidepoint(event.pos):
                    if self.chButton != 0:
                        if self.world_type_index != 0:
                            self.world_type_index -= 1
                        else:
                            self.world_type_index = len(self.world_types if self.chButton == 1 else self.saved_worlds) - 1
                elif rects[0].collidepoint(event.pos):
                    if self.chButton:
                        return 'create_world', self.world_types[self.world_type_index], (None, None)
                    else:
                        self.chButton = 1
                        self.world_type_index = 0
                elif rects[1].collidepoint(event.pos):
                    if self.chButton:
                        filename = self.saved_worlds[self.world_type_index]
                        filepath = os.path.join(self.worlds_folder, filename)
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        return 'load_world', data['world_type'], [data['octaves'], data['seed']]
                    else:
                        self.chButton = 2
                        self.world_type_index = 0
                elif rects[2].collidepoint(event.pos):
                    if self.chButton:
                        return 'placeholder', None
                    else:
                        self.chButton = 3
                        self.world_type_index = 0
                else:
                    self.chButton = 0
        return None

    def draw_menu(self):
        result = None
        textcolor = (175, 175, 175)

        create_button_rect = pygame.Rect(self.screen_w / 2 - 375, 350, 750, 100)
        load_button_rect = pygame.Rect(self.screen_w / 2 - 375, (self.screen_h - 400 + 300) / 2 + 50, 750, 100)
        placeholder_button_rect = pygame.Rect(self.screen_w / 2 - 375, self.screen_h - 400 + 50, 750, 100)

        button_released_img = pygame.image.load('assets/ButtonReleased.png').convert_alpha()
        button_released_img = pygame.transform.scale(button_released_img, (create_button_rect.width,
                                                                                     create_button_rect.height))
        button_pressed_img = pygame.image.load('assets/ButtonPressed.png').convert_alpha()
        button_pressed_img = pygame.transform.scale(button_pressed_img, (create_button_rect.width,
                                                                                   create_button_rect.height))
        button_pressed_arrows_img = pygame.image.load('assets/ButtonPressedArrows.png').convert_alpha()
        button_pressed_arrows_img = pygame.transform.scale(button_pressed_arrows_img, (create_button_rect.width,
                                                                                   create_button_rect.height))

        while result is None or result[0]=='placeholder':
            left_arrow_rect = pygame.Rect(self.screen_w / 2 - 375 + 10,
                                                 350 + 35 if self.chButton == 1 else (self.screen_h - 400 + 300) / 2 + 85,
                                                 30, 30)
            right_arrow_rect = pygame.Rect(self.screen_w / 2 - 375 + 710,
                                                  350 + 35 if self.chButton == 1 else (self.screen_h - 400 + 300) / 2 + 85,
                                                  30, 30)
            result = self.handle_events((create_button_rect, load_button_rect, placeholder_button_rect), (left_arrow_rect, right_arrow_rect))

            self.screen.blit(button_released_img if self.chButton != 1 else button_pressed_arrows_img , create_button_rect)
            self.screen.blit(button_released_img if self.chButton != 2 else button_pressed_arrows_img, load_button_rect)
            self.screen.blit(button_released_img if self.chButton != 3 else button_pressed_img, placeholder_button_rect)

            text1 = self.big_font.render("Create new world" if self.chButton != 1 else self.world_types[self.world_type_index], True, textcolor if self.chButton != 1 else (200, 200, 200))
            text1_rect = text1.get_rect(center=create_button_rect.center)
            self.screen.blit(text1, text1_rect)

            text2 = self.big_font.render("Load world" if self.chButton != 2 else self.saved_worlds[self.world_type_index], True, textcolor if self.chButton != 2 else (200, 200, 200))
            text2_rect = text2.get_rect(center=load_button_rect.center)
            self.screen.blit(text2, text2_rect)

            text3 = self.big_font.render("Coming soon...", True, textcolor if self.chButton != 3 else (200, 200, 200))
            text3_rect = text3.get_rect(center=placeholder_button_rect.center)
            self.screen.blit(text3, text3_rect)


            if self.chButton == 1:
                center_x = self.screen_w // 2
                y = create_button_rect.bottom + 60
                current_type = self.world_types[self.world_type_index]
                text = self.big_font.render(current_type, True, (0, 0, 0))
                self.screen.blit(text, text.get_rect(center=(center_x, y)))

            pygame.display.flip()
        return result

    def draw_world(self):
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.cells[y][x]
                color = self.color_for_cell(cell)
                rect = pygame.Rect(
                    x * self.cell_width + self.sidebar_w,
                    y * self.cell_height + self.sidebar_h,
                    self.cell_width,
                    self.cell_height
                )
                pygame.draw.rect(self.screen, color, rect)
        self.draw_plants()
        self.draw_global_light(self.sim.light, self.sim.l_strength)

    def draw_family_map(self):
        if not self.sim.env.plants:
            return

        plants = self.sim.env.plants
        coords = np.array([(p.x, p.y) for p in plants])
        fam_ids = [p.fam_id for p in plants]

        species_families = {}
        for p in plants:
            s, _ = unpair(p.fam_id)
            if s not in species_families:
                species_families[s] = []
            if p.fam_id not in species_families[s]:
                species_families[s].append(p.fam_id)

        tree = KDTree(coords)

        ys, xs = np.mgrid[0:self.sim.env.height, 0:self.sim.env.width]
        grid_points = np.column_stack([xs.ravel(), ys.ravel()])
        _, indices = tree.query(grid_points)

        color_map = np.array([self.get_color(fam_ids[i], species_families) for i in range(len(plants))])
        pixel_colors = color_map[indices].reshape(self.sim.env.height, self.sim.env.width, 3)

        surface = pygame.surfarray.make_surface(pixel_colors.transpose(1, 0, 2))
        surface = pygame.transform.scale(surface, (self.env_window_width, self.env_window_height))
        surface.set_alpha(123)
        self.screen.blit(surface, (self.sidebar_w, self.sidebar_h))

    def draw_plants(self):
        if self.sim.env.plants:
            for plant in self.sim.env.plants:
                self.draw_plant(plant)

    def draw_plant(self, plant):
        x = plant.x * self.cell_width + self.sidebar_w
        y = plant.y * self.cell_height + self.sidebar_h
        scale = self.cell_width

        plant_height = max(2, int(scale * 0.6 * plant.height / 3))
        plant_width = max(1, int(scale * 0.2))

        if plant.stress > 0.7:
            color = (101, 67, 33)
        elif plant.stress > 0.4:
            t = (plant.stress - 0.4) / 0.3
            color = self.sim.interpolate_color((180, 160, 30), (101, 67, 33), t)  # yellow -> brown
        elif plant.wet < 0.3:
            t = plant.wet / 0.3
            color = self.sim.interpolate_color((180, 160, 30), (34, 120, 30), t)  # yellow -> green
        else:
            g = int(90 + plant.wet * 80)
            color = (20, g, 20)

        stem_x = x + plant_width // 2
        pygame.draw.rect(self.screen, color, (stem_x, y - plant_height, plant_width, plant_height))

        if plant.stress < 0.7:
            leaf_size = max(1, int(plant_width * 1.5))
            leaf_y = y - int(plant_height * 0.6)
            pygame.draw.ellipse(self.screen, color, (stem_x - leaf_size, leaf_y, leaf_size, leaf_size // 2))
            pygame.draw.ellipse(self.screen, color, (stem_x + plant_width, leaf_y, leaf_size, leaf_size // 2))

        if plant.wet > 0.7 and plant.stress < 0.2:
            pygame.draw.circle(self.screen, (100, 220, 100), (stem_x, y - plant_height), max(1, plant_width // 2))

    @staticmethod
    def color_for_cell(cell):
        ctype = cell["type"]


        if ctype == "dirt":
            temp = cell["temperature"]+cell["tempDrift"]  # -1.0 to 1.0
            if temp > 0.5: #0.5 to 1
                color = (137, 128, 45) if cell["grass"] else (51, 37, 6)
            elif temp > 0.3: #0.3 to 0.5
                color = (73, 92, 5) if cell["grass"] else (63, 37, 8)
            elif temp > 0.2: #0.2 to 0.3
                color = (46, 104, 13) if cell["grass"] else (100, 53, 13)
            elif temp > -0.15: #-0.3 to 0.2
                color = (19, 109, 21) if cell["grass"] else (139, 69, 19)
            elif temp > -0.3: #-0.4 to -0.3
                color = (46, 104, 45) if cell["grass"] else (134, 73, 25)
            elif temp > -0.4: #-0.4 to -0.3
                color = (77, 124, 77) if cell["grass"] else (129, 78, 30)
            elif temp > -0.5: #-0.5 to -0.4
                color = (148, 178, 148) if cell["grass"] else (119, 88, 40)
            else: #-1 to -0.5
                color = (209, 249, 219) if cell["grass"] else (122, 98, 63)

        elif ctype == "water":
            color = (154, 184, 194)
        elif ctype == "sand":
            color = (203, 189, 147)
        elif ctype == "mountain":
            color = (100, 100, 100)
        else:
            color = (0, 0, 0)

        return color

    def screen_to_world(self, pos):
        x, y = pos
        x_world = int((x-self.sidebar_w)//self.cell_width)
        y_world = int((y-self.sidebar_h)//self.cell_height)
        return x_world, y_world

    def get_color(self, fid, species_families):
        if fid not in self.family_colors:
            s, fam = unpair(fid)
            if s not in self.species_base_colors:
                np.random.seed(hash(s) % 2 ** 32 + self.col_seed_extra)
                base = np.random.randint(80, 255, size=3)
                self.species_base_colors[s] = base
            else:
                base = self.species_base_colors[s]
            # Darken slightly for each new family within species
            fam_index = species_families[s].index(fid)
            factor = max(0.4, 1.0 - fam_index * 0.15)
            color = tuple(int(c * factor) for c in base)
            self.family_colors[fid] = color
        return self.family_colors[fid]

    def draw_line_graph(self, data, graph, margins):
        GRAY25 = (70, 70, 70)

        graph.fill((0, 0, 0))

        W = graph.get_width() - margins[0] - margins[1]
        H = graph.get_height() - margins[2] - margins[3]
        LEFT = margins[0]
        RIGHT = graph.get_width() - margins[1]
        BOTTOM = graph.get_height() - margins[3]

        if not data:
            return
        data = [step for step in data if sum(step.values()) > 0]
        if len(data) < 2:
            return

        for i, step in enumerate(data):
            for f in step.keys():
                if f not in self.family_first_seen:
                    self.family_first_seen[f] = i
                if f not in self.family_order:
                    self.family_order.append(f)

        species_families = {}
        for f in self.family_order:
            s, fam = unpair(f)
            if s not in species_families:
                species_families[s] = []
            if f not in species_families[s]:
                species_families[s].append(f)

        species_order = sorted(species_families.keys(),
                               key=lambda s: min(self.family_first_seen.get(f, 0)
                                                 for f in species_families[s]))

        for s in species_order:
            species_families[s].sort(key=lambda f: self.family_first_seen.get(f, 0))

        families = []
        for s in species_order:
            families.extend(species_families[s])

        LEN = len(data)

        normalized = []
        for step in data:
            total = sum(step.values())
            if total == 0:
                normalized.append({f: 0 for f in families})
            else:
                normalized.append({f: step.get(f, 0) / total for f in families})

        # For each family, find the tick it first appeared and its species's stack position at that tick
        family_y_offsets = {}  # fam_id : fraction offset where it starts drawing from

        for f in families:
            s, _ = unpair(f)
            first = self.family_first_seen.get(f, 0)
            species_fams = species_families[s]
            fam_index = species_fams.index(f)
            if fam_index == 0:
                family_y_offsets[f] = None
            else:
                if first < len(normalized):
                    offset = sum(normalized[first].get(ff, 0) for ff in families[:families.index(f)])
                    family_y_offsets[f] = offset
                else:
                    family_y_offsets[f] = None

        for i in range(LEN - 1):
            x1 = LEFT + (i / LEN) * W
            x2 = LEFT + ((i + 1) / LEN) * W

            y_stack_prev = 0
            y_stack_next = 0

            for f in families:
                v1 = normalized[i][f]
                v2 = normalized[i + 1][f]

                y1_bottom = y_stack_prev
                y1_top = y_stack_prev + v1

                y2_bottom = y_stack_next
                y2_top = y_stack_next + v2

                y1b = BOTTOM - y1_bottom * H
                y1t = BOTTOM - y1_top * H
                y2b = BOTTOM - y2_bottom * H
                y2t = BOTTOM - y2_top * H

                color = self.get_color(f, species_families)

                pygame.draw.polygon(graph, color, [
                    (x1, y1b),
                    (x1, y1t),
                    (x2, y2t),
                    (x2, y2b),
                ])

                y_stack_prev += v1
                y_stack_next += v2

        for frac in [0.25, 0.5, 0.75, 1.0]:
            y = BOTTOM - frac * H
            pygame.draw.line(graph, GRAY25, (LEFT, y), (RIGHT, y), 1)

    @staticmethod
    def dist_to_text(value, is_percent, u):
        if is_percent:
            return f"{value}%"
        else:
            return f"{value / u:.2f}"

    def draw_side_menu(self):
        self.sim.l_strength = self.sim.l_strength / 2
        rect = pygame.Rect(0, 0, self.screen_w, self.sidebar_h)
        pygame.draw.rect(self.screen, self.sim.light, rect)

        day = self.sim.time // 480
        hour = self.sim.time % 480 * 3 // 60
        minute = self.sim.time * 3 % 60

        text_surface = self.font.render(f"{hour}:{minute:02d}  Day {day}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, 10)
        self.screen.blit(text_surface, text_rect)

        if self.sim.active_events:
            text = " - ".join(self.sim.active_events.keys())
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect()
            text_rect.bottomleft = (10, self.screen_h-10)
            self.screen.blit(text_surface, text_rect)

        self.screen.blit(self.savefile_img, (self.screen_w - 40, self.screen_h - 40))

        if self.selected_plant is not None:
            txt_surf = self.font.render(f"Species: {self.selected_plant.species}, Family: {self.selected_plant.family}", True, (255, 255, 255))
            txt_rect = txt_surf.get_rect()
            txt_rect.topright = (self.screen_w - 10, 10)
            self.screen.blit(txt_surf, txt_rect)

        if self.show_graph:
            self.draw_population_graph()

    def draw_population_graph(self):
        graph_width = 500
        graph_height = 300
        graph_x = self.screen_w - graph_width - 10
        graph_y = self.screen_h - graph_height - 10

        graph_surface = pygame.Surface((graph_width, graph_height))
        margins = [10, 10, 10, 10]

        population_data = self.sim.population_history

        self.draw_line_graph(population_data, graph_surface, margins)
        self.screen.blit(graph_surface, (graph_x, graph_y))

    @staticmethod
    def average_colors(colors):
        r = sum(c[0] for c in colors) // len(colors)
        g = sum(c[1] for c in colors) // len(colors)
        b = sum(c[2] for c in colors) // len(colors)
        return (r, g, b)

    @staticmethod
    def is_valid_color(color):
        return (
                isinstance(color, (tuple, list)) and
                len(color) == 3 and
                all(isinstance(c, int) and 0 <= c <= 255 for c in color)
        )

    def draw_global_light(self, light_color, strength=0.5):
        alpha = int(255 * strength)
        overlay = pygame.Surface((self.env_window_width, self.env_window_height), pygame.SRCALPHA)
        overlay.fill((*light_color, alpha))
        self.screen.blit(overlay, (self.sidebar_w, self.sidebar_h))

    def update(self):
        if self.sim is not None:
            self.screen.fill(self.sim.interpolate_color(self.sim.light, (255,255,255),0.2))
            self.draw_world()
            if self.map_type==1:
                self.draw_family_map()
            self.draw_side_menu()
            pygame.display.flip()

    def detect_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_s:
                    self.map_type=(self.map_type+1)%2
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event)

    def handle_click(self, event):
        if event.button == 1:
            if self.savefile_rect.collidepoint(event.pos):
                self.sim.save_world()
            clicked_at = self.screen_to_world(event.pos)
            if 0<clicked_at[0]<self.cols and 0<clicked_at[1]<self.rows:
                for plant in self.sim.env.plants:
                    if abs(plant.x - clicked_at[0]) <= 2 and abs(plant.y - clicked_at[1]) <= 2:
                        if self.selected_plant is not plant:
                            self.selected_plant = plant
                        else:
                            self.selected_plant = None
                        return
                self.sim.env.create_plant(x=clicked_at[0],y=clicked_at[1], add_to_world=True)