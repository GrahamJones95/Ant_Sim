from math import pi, sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
import numpy as np
from ant import Ant
from dropdown import DropDown

FLLSCRN = False         # True for Fullscreen, or False for Window
INITIAL_ANT_COUNT = 50               # Number of Ants to spawn
WIDTH = 1200            # default 1200
HEIGHT = 600            # default 800
FPS = 60                # 48-90
VSYNC = True            # limit frame rate to refresh rate
SHOWFPS = True          # show framerate debug
NUM_OBSTACLES = 30
OBSTACLE_COLOR = (201, 159, 74)

COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)

FoodColor = (50, 255, 50)
FoodRadius = 15

class Food(pg.sprite.Sprite):

    def __init(self, drawSurf, pos):
        super().__init__()
        self.drawSurf = drawSurf
        self.pos = pos
        self.image = pg.Surface((FoodRadius,FoodRadius)).convert()
        self.rect = self.image.get_rect(center=self.pos)
        pg.draw.circle(self.image, FoodColor, (7.5,7.5), 7.5)

class Obstacles():
    def __init__(self):
        obstacle_surface = pg.Surface((WIDTH, HEIGHT))
        obstacles_added = 0

        self.rects = []

        while(obstacles_added < NUM_OBSTACLES):
            top_left = (randint(0, WIDTH), randint(0,HEIGHT))
            self.add_at_pos(top_left)
            obstacles_added += 1

    def add_at_pos(self, pos):
        width = randint(10, 60)
        height = randint(10, 60)
        
        width = width if pos[0] + width < WIDTH else WIDTH - pos[0]
        height = height if pos[1] + height < HEIGHT else HEIGHT - pos[1]

        self.rects.append(pg.Rect(pos, (width, height)))
class Simuation:
    def __init__(self):
        pg.init()  # prepare window
        pg.display.set_caption("Ant War")

        try: pg.display.set_icon(pg.img.load("nants.png"))
        except: print("FYI: nants.png icon not found, skipping..")

        self.screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED, vsync=VSYNC)

        self.clock = pg.time.Clock()

        self.object_dropdown_menu = DropDown(
        [COLOR_INACTIVE, COLOR_ACTIVE],
        [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
        0, 0, 200, 50, 
        pg.font.SysFont(None, 30), 
        "Select Mode", ["Add Food", "Add Obstacle"])

        self.setup_ant_groups()
        self.setup_obstacles()
        self.setup_food()

    def setup_ant_groups(self):
        self.ant_group_1 = pg.sprite.Group()
        self.ant_group_2 = pg.sprite.Group()

        cur_w, cur_h = self.screen.get_size()

        self.nest1 = (cur_w/4, cur_h/2)
        self.nest2 = (3*cur_w/4, cur_h/2)

        for n in range(INITIAL_ANT_COUNT):
            self.ant_group_1.add(Ant(self.screen, self.nest1, 1))
            self.ant_group_2.add(Ant(self.screen, self.nest2, 2))
    
    def setup_obstacles(self):
        self.obstacles = Obstacles()
        for obstacle in self.obstacles.rects:
            pg.draw.rect(self.screen, OBSTACLE_COLOR, obstacle)

    def setup_food(self):
        self.food_group = pg.sprite.Group()

    def handle_user_input(self, event_list):
        for e in event_list:
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return True
            elif e.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                match self.object_dropdown_menu.current_option:
                    case "Add Obstacle":
                        self.obstacles.add_at_pos(mousepos)
                    case "Add Food":
                        self.food_group.add(Food(self.screen, mousepos))

    def simulate(self):
        while True:
            event_list = pg.event.get()
            if self.handle_user_input(event_list):
                return

            dt = self.clock.tick(FPS) / 300

            self.ant_group_1.update(dt)
            self.ant_group_2.update(dt)

            for ant_collide, collide_list in pg.sprite.groupcollide(self.ant_group_1, self.ant_group_2, False, False).items():
                for ant in [ant_collide, *collide_list]:
                    ant.health -= len(collide_list)
                    if ant.health < 0:
                        ant.kill()
                        # ant_group_1.add(Ant(screen, nest1, 1))
                        # ant_group_2.add(Ant(screen, nest2, 2))
                

            self.screen.fill(0) # fill MUST be after sensors update, so previous draw is visible to them

            selected_option = self.object_dropdown_menu.update(event_list)
            if selected_option >= 0:
                self.object_dropdown_menu.main = self.object_dropdown_menu.options[selected_option]

            for obstacle in self.obstacles.rects:
                pg.draw.rect(self.screen, OBSTACLE_COLOR, obstacle)

            self.ant_group_1.draw(self.screen)
            self.ant_group_2.draw(self.screen)
            self.food_group.draw(self.screen)
            self.object_dropdown_menu.draw(self.screen)
            pg.display.update()

def main():    
    sim = Simuation()
    sim.simulate()
    
if __name__ == '__main__':
    main()  
    pg.quit()