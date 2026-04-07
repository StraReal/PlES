import random
import sys
import pygame,time,os,json

FONTPATH_DIR = "assets/font"
def get_font_list():
    return [os.path.join(FONTPATH_DIR, f)
            for f in os.listdir(FONTPATH_DIR)
            if f.lower().endswith((".ttf", ".otf"))]
font_list = get_font_list()
if font_list:
    FONTPATH = font_list[0]
else:
    raise FileNotFoundError(f"No font found in {FONTPATH_DIR}")

def map_value(value, min_val, max_val, original_min_val=0.0, original_max_val=1.0):
    if original_max_val == original_min_val:
        raise ValueError("Invalid interval: range can't be zero.")
    t = (value - original_min_val) / (original_max_val - original_min_val)
    mapped_val = t * (max_val - min_val) + min_val
    return mapped_val

def squash_towards_zero(x, factor=4):
    return x**factor
class UI:
    def __init__(self,sim=None,cells=None, plants=None,wW=1, wH=1,_sW=1,_sH=1,_worldType=None):
        self.sim=sim
        self.cells = cells
        self.rows = wH
        self.cols = wW
        self.swW=_sW
        self.swH=_sH
        self.cell_width = _sW // self.cols
        self.cell_height = _sH // self.rows
        self.worldType=_worldType
        pygame.font.init()
        self.font = pygame.font.Font(FONTPATH, 21)
        self.selected_option = None
        self.worlds_folder= "worlds"
        self.world_types = ["Continental", "Archipelago"]
        self.saved_worlds = [f for f in os.listdir(self.worlds_folder) if f.endswith(".json") and os.path.isfile(os.path.join(self.worlds_folder, f))]
        self.world_type_index = 0
        self.menu_font = pygame.font.Font(FONTPATH, 40)
        pygame.init()
        self.screen_w,self.screen_h=self.get_screen_sizes()
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        self.sidebar_w ,self.sidebar_h = (self.screen_w-self.swW)//2, (self.screen_h-self.swH)//2
        self.chButton=0
        self.selected_plant = None
        self.savefile_img = pygame.image.load("assets/SaveFile.png").convert_alpha()
        self.savefile_img = pygame.transform.scale(self.savefile_img, (35, 35))
        self.savefile_rect = pygame.Rect(self.screen_w - 40, self.screen_h - 40, 35, 35)
        pygame.display.set_caption("PlES")
        if self.sim is not None:
            self.plants=self.sim.env.plants
        else:
            self.plants=plants

    @staticmethod
    def get_screen_sizes():
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h
        return width, height

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            elif event.type == pygame.MOUSEBUTTONDOWN:
                left_arrow_rect = pygame.Rect(self.screen_w / 2 - 375 + 10, 350 + 35 if self.chButton == 1 else (self.screen_h - 400 + 300) / 2 + 85, 30, 30)
                right_arrow_rect = pygame.Rect(self.screen_w / 2 - 375 + 710, 350 + 35 if self.chButton == 1 else (self.screen_h - 400 + 300) / 2 + 85, 30, 30)
                rect_create = pygame.Rect(self.screen_w / 2 - 375, 350, 750, 100)
                rect_load = pygame.Rect(self.screen_w / 2 - 375, (self.screen_h - 400 + 300) / 2 + 50, 750, 100)
                rect_placeholder = pygame.Rect(self.screen_w / 2 - 375, self.screen_h - 400 + 50, 750, 100)

                if right_arrow_rect.collidepoint(event.pos):
                    if self.chButton != 0:
                        if self.world_type_index + 1 != len(self.world_types if self.chButton == 1 else self.saved_worlds):
                            self.world_type_index += 1
                        else:
                            self.world_type_index = 0
                elif left_arrow_rect.collidepoint(event.pos):
                    if self.chButton != 0:
                        if self.world_type_index != 0:
                            self.world_type_index -= 1
                        else:
                            self.world_type_index = len(self.world_types if self.chButton == 1 else self.saved_worlds) - 1
                elif rect_create.collidepoint(event.pos):
                    if self.chButton:
                        return 'create_world', self.world_types[self.world_type_index], (None, None)
                    else:
                        self.chButton = 1
                        self.world_type_index = 0
                elif rect_load.collidepoint(event.pos):
                    if self.chButton:
                        filename = self.saved_worlds[self.world_type_index]
                        filepath = os.path.join(self.worlds_folder, filename)
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        return 'load_world', data['world_type'], [data['octaves'], data['seed']]
                    else:
                        self.chButton = 2
                        self.world_type_index = 0
                elif rect_placeholder.collidepoint(event.pos):
                    if self.chButton:
                        return 'placeholder', None
                    else:
                        self.chButton = 3
                        self.world_type_index = 0
                else:
                    self.chButton = 0
        return None

    def draw_menu(self):
        buttoncolor = (19, 109, 21) if not self.chButton else (9, 54, 10)
        textcolor = (255, 255, 255) if not self.chButton else (200, 200, 200)
        rect_create = pygame.Rect(self.screen_w / 2 - 375, 350, 750, 100)
        rect_placeholder = pygame.Rect(self.screen_w / 2 - 375, self.screen_h - 400 + 50, 750, 100)
        rect_load = pygame.Rect(self.screen_w / 2 - 375, (self.screen_h - 400 + 300) / 2 + 50, 750, 100)

        pygame.draw.rect(self.screen, buttoncolor if self.chButton != 1 else (19, 109, 21), rect_create, border_radius=10)
        pygame.draw.rect(self.screen, buttoncolor if self.chButton != 2 else (19, 109, 21), rect_load, border_radius=10)
        pygame.draw.rect(self.screen, buttoncolor if self.chButton != 3 else (19, 109, 21), rect_placeholder, border_radius=10)

        font = self.menu_font
        text1 = font.render("Create new world" if self.chButton != 1 else self.world_types[self.world_type_index], True, textcolor if self.chButton != 1 else (255, 255, 255))
        text1_rect = text1.get_rect(center=rect_create.center)
        self.screen.blit(text1, text1_rect)

        text2 = font.render("Load world" if self.chButton != 2 else self.saved_worlds[self.world_type_index], True, textcolor if self.chButton != 2 else (255, 255, 255))
        text2_rect = text2.get_rect(center=rect_load.center)
        self.screen.blit(text2, text2_rect)

        text3 = font.render("Coming soon...", True, textcolor if self.chButton != 3 else (255, 255, 255))
        text3_rect = text3.get_rect(center=rect_placeholder.center)
        self.screen.blit(text3, text3_rect)

        lArRect = pygame.Rect(self.screen_w / 2 - 375 + 10, 350 + 35 if self.chButton == 1 else (self.screen_h - 400 + 300) / 2 + 85, 30, 30)
        rArRect = pygame.Rect(self.screen_w / 2 - 375 + 710, 350 + 35 if self.chButton == 1 else (self.screen_h - 400 + 300) / 2 + 85, 30, 30)

        if self.chButton != 0:
            pygame.draw.rect(self.screen, (200, 200, 200), lArRect, border_radius=3)
            pygame.draw.rect(self.screen, (200, 200, 200), rArRect, border_radius=3)

        if self.chButton == 1:
            types_font = pygame.font.SysFont(None, 44)
            center_x = self.screen_w // 2
            y = rect_create.bottom + 60
            current_type = self.world_types[self.world_type_index]
            text = types_font.render(current_type, True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=(center_x, y)))

        pygame.display.flip()

    def draw_main_menu(self):
        result = None
        while result is None:
            result = self.handle_events()
            self.draw_menu()
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

    def draw_plants(self):
        if self.plants:
            for plant in self.plants:
                self.draw_plant(plant)

    def draw_plant(self, plant):
        x = plant.x * self.cell_width + self.sidebar_w
        y = plant.y * self.cell_height + self.sidebar_h
        scale = self.cell_width

        plant_height = max(2, int(scale * 0.6 * plant.height / 3))
        plant_width = max(1, int(scale * 0.2))

        # Color: green when healthy, yellow when dry, brown when stressed
        if plant.stress > 0.7:
            color = (101, 67, 33)
        elif plant.stress > 0.4:
            t = (plant.stress - 0.4) / 0.3
            color = self.sim.interpolate_color((180, 160, 30), (101, 67, 33), t)  # yellow -> brown
        elif plant.wet < 0.3:
            t = plant.wet / 0.3
            color = self.sim.interpolate_color((180, 160, 30), (34, 120, 30), t)  # yellow -> green
        else:
            # Healthy: darker/richer green when well watered
            g = int(90 + plant.wet * 80)
            color = (20, g, 20)

        # Draw stem
        stem_x = x + plant_width // 2
        pygame.draw.rect(self.screen, color, (stem_x, y - plant_height, plant_width, plant_height))

        # Draw leaves, skip if dying
        if plant.stress < 0.7:
            leaf_size = max(1, int(plant_width * 1.5))
            leaf_y = y - int(plant_height * 0.6)
            pygame.draw.ellipse(self.screen, color, (stem_x - leaf_size, leaf_y, leaf_size, leaf_size // 2))
            pygame.draw.ellipse(self.screen, color, (stem_x + plant_width, leaf_y, leaf_size, leaf_size // 2))

        # Draw a small highlight dot on top if very healthy
        if plant.wet > 0.7 and plant.stress < 0.2:
            pygame.draw.circle(self.screen, (100, 220, 100), (stem_x, y - plant_height), max(1, plant_width // 2))

    def draw_cactus(self, x, y, scale=1, hfactor=1):
        green = (34, 139, 34)
        brown = (139, 69, 19)
        base_width = 3
        width = base_width * scale
        height = 12 * scale * hfactor
        arm_width = width * 0.7
        arm_height = height * 0.5
        pygame.draw.rect(self.screen, green, (x, y - height, width, height), border_radius=int(width // 2))

        pygame.draw.rect(self.screen, green, (x - arm_width, y - height * 0.6, arm_width, arm_height),
                         border_radius=int(arm_width // 2))
        pygame.draw.rect(self.screen, green, (x - arm_width, y - height * 0.6, arm_width, arm_width),
                         border_radius=int(arm_width // 2))
        pygame.draw.rect(self.screen, green, (x + width, y - height * 0.6, arm_width, arm_height),
                         border_radius=int(arm_width // 2))
        pygame.draw.rect(self.screen, green, (x + width, y - height * 0.6, arm_width, arm_width),
                         border_radius=int(arm_width // 2))
        pygame.draw.ellipse(self.screen, brown, (x - width, y, width * 3, width))

    @staticmethod
    def color_for_cell(cell):
        ctype = cell["type"]


        if ctype == "dirt":
            temp = cell["temperature"]  # -1.0 to 1.0
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

    def draw_temperature(self):
        very_cold=(0, 0, 128)
        cold=(0, 128, 255)
        neutral=(17,124,19)
        hot=(255, 165, 0)
        very_hot=(255, 0, 0)
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.cells[y][x]
                temp=cell.temperature
                if temp < -0.5:
                    color=self.sim.interpolate_color(very_cold,cold,map_value(temp,0,1,-1,-0.5))
                elif temp < 0:
                    color=self.sim.interpolate_color(cold,neutral,map_value(temp,0,1,-0.5,0))
                elif temp < 0.5:
                    color=self.sim.interpolate_color(neutral,hot,map_value(temp,0,1,0,0.5))
                else:
                    color=self.sim.interpolate_color(hot,very_hot,map_value(temp,0,1,0.5,1))
                rect = pygame.Rect(x * self.cell_width + self.sidebar_w, y * self.cell_height + self.sidebar_h,
                                   self.cell_width, self.cell_height)
                pygame.draw.rect(self.screen, color, rect)

    def screen_to_world(self, pos):
        x, y = pos
        x_world = int((x-self.sidebar_w)//self.cell_width)
        y_world = int((y-self.sidebar_h)//self.cell_height)
        return x_world, y_world

    def draw_side_menu(self):
        self.sim.l_strength=self.sim.l_strength/2
        rect = pygame.Rect(0, 0,
                           self.screen_w, self.sidebar_h)
        pygame.draw.rect(self.screen,self.sim.light, rect)
        day=self.sim.time//480
        hour=self.sim.time%480*3//60
        minute=self.sim.time*3%60
        text_surface = self.font.render(f"{hour}:{minute:02d}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10,10)
        self.screen.blit(text_surface, text_rect)
        text_surface = self.font.render(f"Day {day}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (70, 10)
        self.screen.blit(text_surface, text_rect)
        self.screen.blit(self.savefile_img, (self.screen_w - 40, self.screen_h - 40))
        if self.selected_plant is not None:
            #print(self.selected_plant.rootDepth, self.selected_plant.wet)
            pass

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
        overlay = pygame.Surface((self.swW, self.swH), pygame.SRCALPHA)
        overlay.fill((*light_color, alpha))
        self.screen.blit(overlay, (self.sidebar_w, self.sidebar_h))

    def update(self):
        self.plants = self.sim.env.plants
        self.screen.fill(self.sim.interpolate_color(self.sim.light, (255,255,255),0.2))
        self.draw_world()
        self.draw_side_menu()
        pygame.display.flip()

    def detect_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event)

    def handle_click(self, event):
        if event.button == 1:
            if self.savefile_rect.collidepoint(event.pos):
                self.sim.save_world()
            clicked_at = self.screen_to_world(event.pos)
            if 0<clicked_at[0]<self.cols and 0<clicked_at[1]<self.rows:
                for plant in self.plants:
                    if plant.x == clicked_at[0] and plant.y == clicked_at[1]:
                        if self.selected_plant is not plant:
                            self.selected_plant = plant
                            print(f"Selected plant {plant.x},{plant.y}")
                        else:
                            self.selected_plant = None
                            print("Unselected plant")
                        return
                self.sim.env.create_plant(x=clicked_at[0],y=clicked_at[1], add_to_world=True)