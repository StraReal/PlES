import pygame,time,os,json
clock=pygame.time.Clock()
FONTPATH_DIR = "assets/font"
def get_font_list():
    return [os.path.join(FONTPATH_DIR, f)
            for f in os.listdir(FONTPATH_DIR)
            if f.lower().endswith((".ttf", ".otf"))]
font_list = get_font_list()
if font_list:
    FONTPATH = font_list[0]
else:
    raise FileNotFoundError("Nessun font trovato nella cartella assets/font")

def squashTowardsZero(x, factor=4):
    return x**factor
def mapValue(value, min_val, max_val, oMin_val=0.0, oMax_val=1.0):
    if oMax_val == oMin_val:
        raise ValueError("Intervallo originale non valido: massimo e minimo uguali")
    t = (value - oMin_val) / (oMax_val - oMin_val)
    mapped_val = t * (max_val - min_val) + min_val
    return mapped_val
class UI:
    def __init__(self,sim=None,cells=None, plants=None,wW=1, wH=1,_sW=1,_sH=1,_worldType=None):
        self.prev_mouse_click = False
        self.selWorldType=False
        self.inWorld=False
        self.mapToShow=0
        self.sim=sim
        self.cells = cells
        self.rows = wH
        self.cols = wW
        self.swW=_sW
        self.swH=_sH
        self.cell_width = _sW // self.cols
        self.cell_height = _sH // self.rows
        self.worldType=_worldType
        self.LOD=2
        pygame.font.init()
        self.font = pygame.font.Font(FONTPATH, 21)
        self.selected_option = None
        self.worlds_folder= "worlds"
        self.world_types = ["Continental", "Archipelago"]
        self.saved_worlds = [f for f in os.listdir(self.worlds_folder) if f.endswith(".json") and os.path.isfile(os.path.join(self.worlds_folder, f))]
        self.world_type_index = 0
        self.menufont = pygame.font.Font(FONTPATH, 40)
        pygame.init()
        self.screenW,self.screenH=self.getScreenDimensions()
        self.screen = pygame.display.set_mode((self.screenW, self.screenH))
        self.sBarW,self.sBarH=(self.screenW-self.swW)//2,(self.screenH-self.swH)//2
        self.chButton=0
        self.selected_plant = None
        self.SaveFile = pygame.image.load("assets/SaveFile.png").convert_alpha()
        self.RSaveFile = pygame.transform.scale(self.SaveFile, (35, 35))
        self.rect_savefile = pygame.Rect(self.screenW - 40, self.screenH - 40, 35, 35)
        pygame.display.set_caption("PlES")
        if self.sim is not None:
            self.plants=self.sim.env.plants
            self.time = self.sim.getTime()
            self.light, self.lStrength = self.getSkyColor(self.time)
            self.lStrength = self.lStrength / 2
            self.luminosity = self.RGBIntoLuminosity(self.light)
        else:
            self.time = 0
            self.light = (0, 0, 0)
            self.lStrength = 0
            self.luminosity = 0


    def getScreenDimensions(self):
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h
        return width, height

    def drawMainMenu(self):
        BUTTONCOLOR = (19, 109, 21) if not self.chButton else (9, 54, 10)
        TEXTCOLOR=(255,255,255) if not self.chButton else (200,200,200)
        rectCreate = pygame.Rect(self.screenW / 2 - 375, 350, 750, 100)
        rectPlaceholder = pygame.Rect(self.screenW / 2 - 375, self.screenH - 400 + 50, 750, 100)
        rectLoad = pygame.Rect(self.screenW / 2 - 375, (self.screenH - 400 + 300) / 2 + 50, 750, 100)
        pygame.draw.rect(self.screen, BUTTONCOLOR if self.chButton != 1 else (19, 109, 21), rectCreate,
                         border_radius=10)
        pygame.draw.rect(self.screen, BUTTONCOLOR if self.chButton != 2 else (19, 109, 21), rectLoad, border_radius=10)
        pygame.draw.rect(self.screen, BUTTONCOLOR if self.chButton != 3 else (19, 109, 21), rectPlaceholder,
                         border_radius=10)
        font = self.menufont
        text1 = font.render("Crea nuovo mondo" if self.chButton != 1 else self.world_types[self.world_type_index], True, TEXTCOLOR if self.chButton != 1 else (255,255,255))
        text1_rect = text1.get_rect(center=rectCreate.center)
        self.screen.blit(text1, text1_rect)
        text2 = font.render("Carica mondo"if self.chButton != 2 else self.saved_worlds[self.world_type_index], True, TEXTCOLOR if self.chButton != 2 else (255,255,255))
        text2_rect = text2.get_rect(center=rectLoad.center)
        self.screen.blit(text2, text2_rect)
        text3 = font.render("Coming soon...", True, TEXTCOLOR if self.chButton != 3 else (255,255,255))
        text3_rect = text3.get_rect(center=rectPlaceholder.center)
        self.screen.blit(text3, text3_rect)
        lArRect = pygame.Rect(self.screenW / 2 - 375 + 10, 350 + 35 if self.chButton==1 else (self.screenH - 400 + 300) / 2 + 85, 30, 30)
        rArRect = pygame.Rect(self.screenW / 2 - 375 + 710, 350 + 35 if self.chButton==1 else (self.screenH - 400 + 300) / 2 + 85, 30, 30)
        if self.chButton!=0:
            pygame.draw.rect(self.screen, (200,200,200), lArRect, border_radius=3)
            pygame.draw.rect(self.screen, (200, 200, 200), rArRect, border_radius=3)
        mousePos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        just_clicked = mouse_click and not self.prev_mouse_click
        self.prev_mouse_click = mouse_click
        if just_clicked:
            if rArRect.collidepoint(mousePos):
                if self.chButton!=0:
                    if self.world_type_index+1!=len(self.world_types if self.chButton==1 else self.saved_worlds):
                        self.world_type_index+=1
                    else:
                        self.world_type_index=0
            elif lArRect.collidepoint(mousePos):
                if self.chButton!=0:
                    if self.world_type_index!=0:
                        self.world_type_index-=1
                    else:
                        self.world_type_index=len(self.world_types if self.chButton==1 else self.saved_worlds)-1
            elif rectCreate.collidepoint(mousePos):
                if self.chButton:
                    return 'create_world', self.world_types[self.world_type_index], (None,None)
                else:
                    self.chButton = 1
            elif rectLoad.collidepoint(mousePos):
                if self.chButton:
                    filename = self.saved_worlds[self.world_type_index]
                    filepath = os.path.join(self.worlds_folder, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    return 'load_world', data['world_type'],[data['octaves'],data['seed']]
                else:
                    self.chButton = 2
            elif rectPlaceholder.collidepoint(mousePos):
                if self.chButton:
                    return 'placeholder', None
                else:
                    self.chButton = 3
            else:
                self.chButton = 0
        if self.chButton == 1:
            types_font = pygame.font.SysFont(None, 44)
            center_x = self.screenW // 2
            y = rectCreate.bottom + 60
            current_type = self.world_types[self.world_type_index]
            text = types_font.render(current_type, True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=(center_x, y)))
        pygame.display.flip()
        return None, None, (None,None)

    def detectMouseMotion(self):
        mousePos = pygame.mouse.get_pos()
        mouseX, mouseY=mousePos
        newCLH = [None, None, None]

    def drawWorld(self):
        self.difW = (self.screenW - self.swW) / 2
        self.difH = (self.screenH - self.swH) / 2
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.cells[y][x]
                color = self.colorForCell(cell)
                rect = pygame.Rect(
                    x * self.cell_width + self.difW,
                    y * self.cell_height + self.difH,
                    self.cell_width,
                    self.cell_height
                )
                pygame.draw.rect(self.screen, color, rect)
        self.drawPlants()
        self.drawGlobalLight(self.light, self.lStrength)

    def drawPlants(self):
        if self.plants:
            for Plant in self.plants:
                self.drawGPlant(Plant.x*self.cell_width+self.sBarW, Plant.y*self.cell_height+self.sBarH,self.cell_width)

    def drawGPlant(self, x, y, scale=1, hfactor=1):
        cell_size = 6*scale
        plant_height = int(cell_size * 0.6 * hfactor)
        plant_width = int(cell_size * 0.2)
        color = (255,0,255)
        pygame.draw.rect(self.screen, color, (x,y, plant_width, plant_height))

    def drawCactus(self, x, y, scale=1, hfactor=1):
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

    def colorForCell(self, cell):
        acqua = (154, 184, 194)
        terra = (139, 69, 19)
        erba = (19, 109, 21)
        sabbia = (203, 189, 147)
        montagna=(100,100,100)
        tipo = cell["type"]
        if tipo == "terra":
            color = terra
        elif tipo== 'terraErba':
            color=erba
        elif tipo == "acqua":
            color=acqua
        elif tipo == "sabbia":
            color = sabbia
        elif tipo == "montagna":
            color = montagna
        else:
            color = (0, 0, 0)
        return color

    def drawTemperature(self):
        self.difW=(self.screenW-self.swW)/2
        self.difH = (self.screenH - self.swH)/2
        veryCold=(0, 0, 128)
        cold=(0, 128, 255)
        neutral=(17,124,19)
        hot=(255, 165, 0)
        veryHot=(255, 0, 0)
        for y in range(self.rows):
            for x in range(self.cols):
                cell = self.cells[y][x]
                temp=cell.temperature
                if temp < -0.5:
                    color=self.interpolateColor(veryCold,cold,mapValue(temp,0,1,-1,-0.5))
                elif temp < 0:
                    color=self.interpolateColor(cold,neutral,mapValue(temp,0,1,-0.5,0))
                elif temp < 0.5:
                    color=self.interpolateColor(neutral,hot,mapValue(temp,0,1,0,0.5))
                else:
                    color=self.interpolateColor(hot,veryHot,mapValue(temp,0,1,0.5,1))
                rect = pygame.Rect(x * self.cell_width + self.difW, y * self.cell_height + self.difH,
                                   self.cell_width, self.cell_height)
                pygame.draw.rect(self.screen, color, rect)

    def drawSideMenu(self):
        self.time = self.sim.getTime()
        self.light,self.lStrength=self.getSkyColor(self.time)
        self.luminosity=self.RGBIntoLuminosity(self.light)
        self.lStrength=self.lStrength/2
        rect = pygame.Rect(0, 0,
                           self.screenW, self.difH)
        pygame.draw.rect(self.screen,self.light, rect)
        self.dTime=self.time//96
        self.hTime=self.time%96*15//60
        self.mTime=self.time*15%60
        text_surface = self.font.render(f"{self.hTime}:{self.mTime:02d}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10,10)
        self.screen.blit(text_surface, text_rect)
        text_surface = self.font.render(f"Day {self.dTime}", True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (70, 10)
        self.screen.blit(text_surface, text_rect)
        self.screen.blit(self.RSaveFile, (self.screenW - 40, self.screenH - 40))
        if self.selected_plant is not None:
            #print(self.selected_plant.rootDepth, self.selected_plant.wet)
            self.doNothing()

    def interpolateColor(self, color1, color2, t):
        if t>1:
            print(t)
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * t)
            for i in range(3)
        )

    def averageColors(self, colors):
        r = sum(c[0] for c in colors) // len(colors)
        g = sum(c[1] for c in colors) // len(colors)
        b = sum(c[2] for c in colors) // len(colors)
        return (r, g, b)

    def getSkyColor(self,mHour):
        t = mHour % 96

        day = (200, 220, 255)
        night = (10, 10, 30)
        sunset = (255, 140, 60)

        if t < 20:
            return night,1
        elif t < 28:
            factor = (t - 20) / (28 - 20)
            return self.interpolateColor(night, sunset, factor),1-factor
        elif t < 32:
            factor = (t - 28) / (32 - 28)
            return self.interpolateColor(sunset, day, factor),(1-factor)*0.1
        elif t < 72:
            return day, 0
        elif t < 76:
            factor = (t - 72) / (76 - 72)
            return self.interpolateColor(day, sunset, factor),factor/2
        elif t < 84:
            factor = (t - 76) / (84 - 76)
            return self.interpolateColor(sunset, night, factor),(factor/2)+0.45
        else:
            return night,1

    def is_valid_color(self,color):
        return (
                isinstance(color, (tuple, list)) and
                len(color) == 3 and
                all(isinstance(c, int) and 0 <= c <= 255 for c in color)
        )

    def RGBIntoLuminosity(self,color):
        r,g,b=color
        return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255

    def applyLight(self, base_color, light_color, strength=0.5):
        return tuple(
            int(base_color[i] * (1 - strength) + light_color[i] * strength)
            for i in range(3)
        )

    def drawGlobalLight(self, light_color, strength=0.5):
        alpha = int(255 * strength)
        overlay = pygame.Surface((self.swW, self.swH), pygame.SRCALPHA)
        overlay.fill((*light_color, alpha))
        self.screen.blit(overlay, (self.sBarW, self.sBarH))

    def update(self):
        self.plants = self.sim.env.plants
        self.handleClick()
        self.sim.updateLuminosity(self.luminosity)
        self.screen.fill(self.interpolateColor(self.light, (255,255,255),0.2))
        if self.mapToShow==0:
            start_time = time.perf_counter()
            self.drawWorld()
            elapsed_time = (time.perf_counter() - start_time) * 1000
            #print(f"Frame time: {elapsed_time:.2f} ms")
        else:
            self.drawTemperature()
        self.drawSideMenu()
        pygame.display.flip()
        clock.tick(60)

    def detectEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()

    def handleClick(self):
        mouse_click = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        if mouse_click and not self.prev_mouse_click:
            if self.rect_savefile.collidepoint(mouse_pos):
                self.sim.save_world()
            for plant in self.plants or []:
                px = plant.x * self.cell_width + self.sBarW
                py = plant.y * self.cell_height + self.sBarH
                rect = pygame.Rect(px, py,
                                   int(6 * self.cell_width * 0.2),  # width
                                   int(6 * self.cell_width * 0.6))  # height
                if rect.collidepoint(mouse_pos):
                    self.selected_plant = plant
                    print(self.selected_plant)
                    break
        self.prev_mouse_click = mouse_click

    def doNothing(self):
        nan = 69