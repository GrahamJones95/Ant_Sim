from math import pi, sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
import numpy as np
from enum import Enum
PRATIO = 5 

FoodColor = (111, 168, 50)
ObstacleColor = (201, 159, 74)

def is_food(color):
    if(color[1] == 0):
         return False
    return abs(FoodColor[0]/FoodColor[1] - color[0]/color[1])  < 0.0001

class AntMode(Enum):
     FIND_FOOD = 0
     RETURN_NEST = 1

class Vec2():
	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
	def vint(self):
		return (int(self.x), int(self.y))
     
class AntSplat(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.image = pg.Surface([40,40])
        self.image.set_colorkey(0)
        self.color = [215,0,0]

        pg.draw.circle(self.image, self.color, [20, 20], 8)

        self.splatters = [[randint(-12,12), randint(-12,12)] for _ in range(10)]        
        self.rect = self.image.get_rect(center=pos)
        

    def update(self): 
        if(self.color[0] >= 30):
             self.color[0] -= 0.4

        pg.draw.circle(self.image, self.color, [20, 20], 9)
        for splatter in self.splatters:
            pg.draw.circle(self.image, self.color, [20+splatter[0], 20+splatter[1]], 5)

class Ant(pg.sprite.Sprite):
    
    def __init__(self, drawSurf, nest, teamNum):
        super().__init__()
        self.drawSurf = drawSurf
        self.curW, self.curH = self.drawSurf.get_size()
        self.nest = nest
        self.image = pg.Surface((12, 21)).convert()
        self.image.set_colorkey(0)
        self.teamNum = teamNum
        self.health = 100

        antColor = (100,42,42) if teamNum == 1 else (50,80,80)
        # Draw Ant
        pg.draw.aaline(self.image, antColor, [0, 5], [11, 15])
        pg.draw.aaline(self.image, antColor, [0, 15], [11, 5]) # legs
        pg.draw.aaline(self.image, antColor, [0, 10], [12, 10])
        pg.draw.aaline(self.image, antColor, [2, 0], [4, 3]) # antena l
        pg.draw.aaline(self.image, antColor, [9, 0], [7, 3]) # antena r
        pg.draw.ellipse(self.image, antColor, [3, 2, 6, 6]) # head
        pg.draw.ellipse(self.image, antColor, [4, 6, 4, 9]) # body
        pg.draw.ellipse(self.image, antColor, [3, 13, 6, 8]) # rear
        
        self.food_blit = pg.Surface([3,3])
        pg.draw.circle(self.food_blit, FoodColor, [0,0], 10)
        # save drawing for later
        self.orig_img = pg.transform.rotate(self.image.copy(), -90)
        self.rect = self.image.get_rect(center=self.nest.pos)
        self.ang = randint(0, 360)
        self.desireDir = pg.Vector2(cos(radians(self.ang)),sin(radians(self.ang)))
        self.pos = pg.Vector2(self.rect.center)
        self.vel = pg.Vector2(0,0)
        self.last_sdp = (nest.pos[0]/10/2,nest.pos[1]/10/2)
        self.mode = 0
        self.mode = AntMode.FIND_FOOD
        self.has_food = False
    
    def update(self, dt):  # behavior
        mid_result = left_result = right_result = [0,0,0]
        mid_GA_result = left_GA_result = right_GA_result = [0,0,0]
        randAng = randint(0,360)
        accel = pg.Vector2(0,0)
        wandrStr = .12  # how random they walk around
        maxSpeed = 12  # 10-12 seems ok
        steerStr = 3  # 3 or 4, dono
        # Converts ant's current screen coordinates, to smaller resolution of pherogrid.
        #scaledown_pos = (int((self.pos.x/self.curW)*self.pgSize[0]), int((self.pos.y/self.curH)*self.pgSize[1]))
        # Get locations to check as sensor points, in pairs for better detection.
        mid_sensL = Vec2.vint(self.pos + pg.Vector2(21, -3).rotate(self.ang))
        mid_sensR = Vec2.vint(self.pos + pg.Vector2(21, 3).rotate(self.ang))
        left_sens1 = Vec2.vint(self.pos + pg.Vector2(18, -14).rotate(self.ang))
        left_sens2 = Vec2.vint(self.pos + pg.Vector2(16, -21).rotate(self.ang))
        right_sens1 = Vec2.vint(self.pos + pg.Vector2(18, 14).rotate(self.ang))
        right_sens2 = Vec2.vint(self.pos + pg.Vector2(16, 21).rotate(self.ang))
        # May still need to adjust these sensor positions, to improve following.

        
        
        if self.drawSurf.get_rect().collidepoint(mid_sensL) and self.drawSurf.get_rect().collidepoint(mid_sensR):
            mid_GA_result = max(self.drawSurf.get_at(mid_sensL)[:3], self.drawSurf.get_at(mid_sensR)[:3])
        if self.drawSurf.get_rect().collidepoint(left_sens1) and self.drawSurf.get_rect().collidepoint(left_sens2):
            left_GA_result = max(self.drawSurf.get_at(left_sens1)[:3],self.drawSurf.get_at(left_sens2)[:3])
        if self.drawSurf.get_rect().collidepoint(right_sens1) and self.drawSurf.get_rect().collidepoint(right_sens2):
            right_GA_result = max(self.drawSurf.get_at(right_sens1)[:3],self.drawSurf.get_at(right_sens2)[:3])
        
        wallColor = (50,50,50)  # avoid walls of this color

        # if self.mode == AntMode.FIND_FOOD and mid_GA_result == FoodColor: # if food
        # # if self.mode == AntMode.FIND_FOOD and is_food(mid_GA_result): # if food
        if self.mode == AntMode.FIND_FOOD and self.has_food:
                self.desireDir = pg.Vector2(-1,0).rotate(self.ang).normalize() 
                maxSpeed = 5
                wandrStr = .01
                steerStr = 5
                self.mode = AntMode.RETURN_NEST

        elif(self.mode == AntMode.RETURN_NEST):
            if(self.pos.distance_to(self.nest.pos) < 20):
                 self.mode = AntMode.FIND_FOOD
                 self.has_food = False
                 self.nest.food += 1
            else:
                 self.desireDir += pg.Vector2(self.nest.pos - self.pos).normalize() * .08

        
        if left_GA_result == wallColor or left_GA_result == ObstacleColor:
            self.desireDir += pg.Vector2(0,2).rotate(self.ang) #.normalize()
            wandrStr = .1
            steerStr = 7
        elif right_GA_result == wallColor or right_GA_result == ObstacleColor:
            self.desireDir += pg.Vector2(0,-2).rotate(self.ang) #.normalize()
            wandrStr = .1
            steerStr = 7
        elif mid_GA_result == wallColor or mid_GA_result == ObstacleColor:
            self.desireDir = pg.Vector2(-2,0).rotate(self.ang) #.normalize()
            maxSpeed = 4
            wandrStr = .1
            steerStr = 7

        # Avoid edges
        if not self.drawSurf.get_rect().collidepoint(left_sens1) and self.drawSurf.get_rect().collidepoint(right_sens1):
            self.desireDir += pg.Vector2(0,1).rotate(self.ang) #.normalize()
            wandrStr = .01
            steerStr = 5
        elif not self.drawSurf.get_rect().collidepoint(right_sens1) and self.drawSurf.get_rect().collidepoint(left_sens1):
            self.desireDir += pg.Vector2(0,-1).rotate(self.ang) #.normalize()
            wandrStr = .01
            steerStr = 5
        elif not self.drawSurf.get_rect().collidepoint(Vec2.vint(self.pos + pg.Vector2(21, 0).rotate(self.ang))):
            self.desireDir += pg.Vector2(-1,0).rotate(self.ang) #.normalize()
            maxSpeed = 5
            wandrStr = .01
            steerStr = 5

        randDir = pg.Vector2(cos(radians(randAng)),sin(radians(randAng)))
        self.desireDir = pg.Vector2(self.desireDir + randDir * wandrStr).normalize()
        dzVel = self.desireDir * maxSpeed
        dzStrFrc = (dzVel - self.vel) * steerStr
        accel = dzStrFrc if pg.Vector2(dzStrFrc).magnitude() <= steerStr else pg.Vector2(dzStrFrc.normalize() * steerStr)
        velo = self.vel + accel * dt
        self.vel = velo if pg.Vector2(velo).magnitude() <= maxSpeed else pg.Vector2(velo.normalize() * maxSpeed)
        self.pos += self.vel * dt
        self.ang = degrees(atan2(self.vel[1],self.vel[0]))

        
        if(self.mode == AntMode.RETURN_NEST):
            self.food_blit.fill(FoodColor)
        else:
            self.food_blit.fill((0,0,0))

        self.orig_img.blit(self.food_blit, [18,4])

        # adjusts angle of img to match heading
        self.image = pg.transform.rotate(self.orig_img, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        # actually update position
        self.rect.center = self.pos