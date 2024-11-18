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

            width = randint(10, 60)
            height = randint(10, 60)
            
            width = width if top_left[0] + width < WIDTH else WIDTH - top_left[0]
            height = height if top_left[1] + height < HEIGHT else HEIGHT - top_left[1]

            self.rects.append(pg.Rect(top_left, (width, height)))
            obstacles_added += 1


def main():
    pg.init()  # prepare window
    pg.display.set_caption("Ant War")

    try: pg.display.set_icon(pg.img.load("nants.png"))
    except: print("FYI: nants.png icon not found, skipping..")

    # setup fullscreen or window mode
    screen = pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED, vsync=VSYNC)

    cur_w, cur_h = screen.get_size()
    screenSize = (cur_w, cur_h)
    nest1 = (cur_w/4, cur_h/2)
    nest2 = (3*cur_w/4, cur_h/2)

    ant_group_1 = pg.sprite.Group()
    ant_group_2 = pg.sprite.Group()
    food_group = pg.sprite.Group()

    obstacles = Obstacles()

    new_obstacles = []

    for obstacle in obstacles.rects:
        pg.draw.rect(screen, OBSTACLE_COLOR, obstacle)

    for n in range(INITIAL_ANT_COUNT):
        ant_group_1.add(Ant(screen, nest1, 1))
        ant_group_2.add(Ant(screen, nest2, 2))

    font = pg.font.Font(None, 30)
    clock = pg.time.Clock()

    object_dropdown_menu = DropDown(
    [COLOR_INACTIVE, COLOR_ACTIVE],
    [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
    0, 0, 200, 50, 
    pg.font.SysFont(None, 30), 
    "Select Mode", ["Add Food", "Add Obstacle"])

    while True:
        event_list = pg.event.get()
        for e in event_list:
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
            elif e.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                match object_dropdown_menu.current_option:
                    case "Add Obstacle":
                        new_obstacles.append(mousepos)
                    case "Add Food":
                        food_group.add([Food(screen, mousepos)])

        dt = clock.tick(FPS) / 100

        ant_group_1.update(dt)
        ant_group_2.update(dt)

        for ant_collide, collide_list in pg.sprite.groupcollide(ant_group_1, ant_group_2, False, False).items():
            for ant in [ant_collide, *collide_list]:
                ant.health -= len(collide_list)
                if ant.health < 0:
                    ant.kill()
                    # ant_group_1.add(Ant(screen, nest1, 1))
                    # ant_group_2.add(Ant(screen, nest2, 2))
            

        screen.fill(0) # fill MUST be after sensors update, so previous draw is visible to them

        selected_option = object_dropdown_menu.update(event_list)
        if selected_option >= 0:
            object_dropdown_menu.main = object_dropdown_menu.options[selected_option]

        for obstacle in obstacles.rects:
            pg.draw.rect(screen, OBSTACLE_COLOR, obstacle)
        for obstacle in new_obstacles:
            pg.draw.circle(screen, OBSTACLE_COLOR, obstacle, 10)

        ant_group_1.draw(screen)
        ant_group_2.draw(screen)
        food_group.draw(screen)
        object_dropdown_menu.draw(screen)
        pg.display.update()


if __name__ == '__main__':
    main()  
    pg.quit()