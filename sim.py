from math import pi, sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
import numpy as np
from ant import Ant, AntSplat, FoodColor, ObstacleColor, AntMode

from dropdown import DropDown

FLLSCRN = False         # True for Fullscreen, or False for Window
INITIAL_ANT_COUNT = 50               # Number of Ants to spawn
WIDTH = 1200            # default 1200
HEIGHT = 600            # default 800
FPS = 60                # 48-90
VSYNC = True            # limit frame rate to refresh rate
SHOWFPS = True          # show framerate debug
NUM_OBSTACLES = 30

COLOR_INACTIVE = (100, 80, 255)
COLOR_ACTIVE = (100, 200, 255)
COLOR_LIST_INACTIVE = (255, 100, 100)
COLOR_LIST_ACTIVE = (255, 150, 150)

FoodRadius = 15

NEW_ANT_FOOD = 8
INITIAL_FOOD_AMOUNT = 8

class Nest:
    def __init__(self, pos):
        self.pos = pos
        self.food = 0

    def make_new(self):
        if self.food >= NEW_ANT_FOOD:
            print("Food count: {}".format(self.food))
            self.food -= NEW_ANT_FOOD
            return True
        return False

class Food(pg.sprite.Sprite):

    def __init__(self, drawSurf, pos):
        super().__init__()
        self.drawSurf = drawSurf
        self.pos = pos
        self.image = pg.Surface((FoodRadius,FoodRadius)).convert_alpha()
        self.rect = self.image.get_rect(center=self.pos)
        self.color = list(FoodColor)
        pg.draw.circle(self.image, FoodColor, (7.5,7.5), 7.5)
        self.food_remaining = INITIAL_FOOD_AMOUNT

    def update(self):
        # if(self.color[2] <= 0 ):
        #     self.kill()
        #     return
        if(self.food_remaining <= 0):
            self.kill()
            return
        self.color = [(self.food_remaining*FoodColor[i])/INITIAL_FOOD_AMOUNT for i in range(3)]
        pg.draw.circle(self.image, self.color, (7.5,7.5), 7.5)

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
        self.ant_splat_group = pg.sprite.Group()

        cur_w, cur_h = self.screen.get_size()

        self.nest1 = Nest((cur_w/4, cur_h/2))
        self.nest2 = Nest((3*cur_w/4, cur_h/2))

        self.nest1_image_pos = (cur_w/4 - 25, cur_h/2)
        self.nest2_image_pos = (3*cur_w/4 - 25, cur_h/2)

        anthill_image = pg.image.load("ant_hill.png").convert_alpha()
        anthill_image = pg.transform.scale(anthill_image, [50,50])
        self.ANT_HILL_1 = anthill_image
        
        for n in range(INITIAL_ANT_COUNT):
            self.ant_group_1.add(Ant(self.screen, self.nest1, 1))
            self.ant_group_2.add(Ant(self.screen, self.nest2, 2))
    
    def setup_obstacles(self):
        self.obstacles = Obstacles()
        for obstacle in self.obstacles.rects:
            pg.draw.rect(self.screen, ObstacleColor, obstacle)

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

    def handle_ant_collisions(self):
        for ant, collide_list in pg.sprite.groupcollide(self.ant_group_1, self.ant_group_2, False, False).items():
            ant.health -= len(collide_list) * 4
            if ant.health < 0:
                self.ant_splat_group.add(AntSplat(ant.pos))
                ant.kill()


        for ant, collide_list in pg.sprite.groupcollide(self.ant_group_2, self.ant_group_1, False, False).items():
            ant.health -= len(collide_list) * 4
            if ant.health < 0:
                self.ant_splat_group.add(AntSplat(ant.pos))
                ant.kill()

        if self.nest1.make_new():
            self.ant_group_1.add(Ant(self.screen, self.nest1, 1))
        if self.nest2.make_new():
            self.ant_group_2.add(Ant(self.screen, self.nest2, 2))

    def handle_food_collision(self):
        for ant, collide_list in pg.sprite.groupcollide(self.ant_group_1, self.food_group, False, False).items():
            if(ant.mode == AntMode.FIND_FOOD):
                ant.has_food = True
                collide_list[0].food_remaining -= 1

        for ant, collide_list in pg.sprite.groupcollide(self.ant_group_2, self.food_group, False, False).items():
            if(ant.mode == AntMode.FIND_FOOD):
                ant.has_food = True
                collide_list[0].food_remaining -= 1

    def simulate(self):
        while True:
            event_list = pg.event.get()
            if self.handle_user_input(event_list):
                return

            dt = self.clock.tick(FPS) / 100

            self.ant_group_1.update(dt)
            self.ant_group_2.update(dt)
            self.ant_splat_group.update()
            self.food_group.update()


            self.handle_ant_collisions()
            self.handle_food_collision()

            self.screen.fill(0) # fill MUST be after sensors update, so previous draw is visible to them

            selected_option = self.object_dropdown_menu.update(event_list)
            if selected_option >= 0:
                self.object_dropdown_menu.main = self.object_dropdown_menu.options[selected_option]

            for obstacle in self.obstacles.rects:
                pg.draw.rect(self.screen, ObstacleColor, obstacle)
            
            self.ant_splat_group.draw(self.screen)
            self.screen.blit(self.ANT_HILL_1, self.nest1_image_pos)
            self.screen.blit(self.ANT_HILL_1, self.nest2_image_pos)
            self.ant_group_1.draw(self.screen)
            self.ant_group_2.draw(self.screen)
            

            self.food_group.draw(self.screen)
            self.object_dropdown_menu.draw(self.screen)
            msg = pg.font.SysFont(None, 30).render("Nest 1 Count: {} Nest 2 Count: {}".format(len(self.ant_group_1.sprites()), len(self.ant_group_2.sprites())),1, (255, 255, 255))
            # msg.fill((255,255,255))
            msg_background = pg.Surface([i+20 for i in msg.get_bounding_rect().size])
            msg_background.fill((200,200,200))
            msg_background.set_alpha(180)
            self.screen.blit(msg_background, msg_background.get_rect(center=[800,570]))
            self.screen.blit(msg, msg.get_rect(center=[800,570]))
            
            

            pg.display.update()

def main():    
    sim = Simuation()
    sim.simulate()
    
if __name__ == '__main__':
    main()  
    pg.quit()