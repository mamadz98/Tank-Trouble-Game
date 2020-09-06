import pygame
import random
import math
import socket
import time
import os
import sys
from random import shuffle

#Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PURPLE = (255, 0, 255)
gray = (128,128,128)
width = 1280
height = 600
 
class Config(object):
    width = 1500
    height = 800
    fps = 100

 
class Bullet(pygame.sprite.Sprite):
    side = 4 
    vel = 180 # velocity
    mass = 50
    maxlifetime = 10.0 # seconds
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.boss = boss
        self.dx = 0
        self.dy = 0
        self.angle = 0
        self.lifetime = 0.0
        self.color = self.boss.color
        self.calculate_heading()
        self.dx += self.boss.dx
        self.dy += self.boss.dy
        self.pos = self.boss.pos[:] 
        self.x = self.pos[0]
        self.y = self.pos[1]
        self.calculate_origin()
        self.update()
 
    def calculate_heading(self):
       
        self.radius = Bullet.side # for collision detection
        self.angle += self.boss.turretAngle
        self.mass = Bullet.mass
        self.vel = Bullet.vel
        image = pygame.Surface((Bullet.side * 2, Bullet.side)) # rect 2 x 1
        image.fill((128,128,128)) # fill grey
        pygame.draw.rect(image, self.color, (0,0,int(Bullet.side * 1.5), Bullet.side)) # rectangle 1.5 length
        pygame.draw.circle(image, self.color, (int(self.side *1.5) ,self.side//2), self.side//2) #  circle
        image.set_colorkey((128,128,128)) # grey transparent
        self.image0 = image.convert_alpha()
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.rect = self.image.get_rect()
        self.dx = math.cos(degrees_to_radians(self.boss.turretAngle)) * self.vel
        self.dy = math.sin(degrees_to_radians(-self.boss.turretAngle)) * self.vel
 
    def calculate_origin(self):
        self.pos[0] +=  math.cos(degrees_to_radians(self.boss.turretAngle)) * (Tank.side-20)
        self.pos[1] +=  math.sin(degrees_to_radians(-self.boss.turretAngle)) * (Tank.side-20)
 
    def update(self, seconds=0.0):
        self.lifetime += seconds
        if self.lifetime > Bullet.maxlifetime:
            self.kill()
        # ------ calculate movement --------
        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        #------- move -------
        self.rect.centerx = round(self.pos[0],0)
        self.rect.centery = round(self.pos[1],0)

    def elastic_collision(self, sprite):
        dirx = self.x - sprite.x 
        diry = self.y - sprite.y 
        # the velocity of the centre of mass
        sumofmasses =  self.mass + 50
        sx = (self.dx * self.mass + 10) / sumofmasses
        sy = (self.dy * self.mass - 50) / sumofmasses
        bdxs = sprite.dx - sx
        bdys = sprite.dy - sy
        cbdxs = self.dx - sx
        cbdys = self.dy - sy
        distancesquare = dirx * dirx + diry * diry
        if distancesquare == 0:
            dirx = random.randint(0,11) - 5.5
            diry = random.randint(0,11) - 5.5
            distancesquare = dirx * dirx + diry * diry
        dp = (bdxs * dirx + bdys * diry) # scalar product
        dp /= distancesquare # divide by distance * distance.
        cdp = (cbdxs * dirx + cbdys * diry)
        cdp /= distancesquare
        if dp > 0:
            self.dx -= 3 * dirx * cdp 
            self.dy -= 3 * diry * cdp

	    

 
class Tank(pygame.sprite.Sprite):
    side = 30 # side of the quadratic tank sprite
    recoiltime = 0.75 # how many seconds  the cannon is busy after firing one time
    mgrecoiltime = 0.2 # how many seconds the bow mg (machine gun) is idle
    turretTurnSpeed = 25 # turret
    tankTurnSpeed = 20 # tank
    movespeed = 120
    maxrotate = 360 # maximum amount of degree the turret is allowed to rotate
    book = {} # a book of tanks to store all tanks
    number = 0 # each tank gets his own number
    firekey = (pygame.K_SPACE, pygame.K_RETURN)
    turretLeftkey = (pygame.K_q, pygame.K_KP4)
    turretRightkey = (pygame.K_e, pygame.K_KP6)
    forwardkey = (pygame.K_w, pygame.K_KP5)
    backwardkey = (pygame.K_s, pygame.K_KP2)
    tankLeftkey = (pygame.K_a, pygame.K_KP1)
    tankRightkey = (pygame.K_d, pygame.K_KP3)
    color = ((200,200,0), (0,0,200))
 
    def __init__(self, startpos = (150,150), angle=0):
        if Tank.number >1:
            Tank.number = 0
        self.number = Tank.number # now i have a unique tank number
        Tank.number += 1 # prepare number for next tank

        Tank.book[self.number] = self # store myself into the tank book
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.dead= False        
        self.pos = [startpos[0], startpos[1]] # x,y
        self.dx = 0
        self.dy = 0
        self.ammo = 30 # main gun
        self.mgammo = 500 # machinge gun
        self.color = Tank.color[self.number]
        self.turretAngle = angle #turret facing
        self.tankAngle = angle # tank facing
        self.firekey = Tank.firekey[self.number] # main gun
        self.turretLeftkey = Tank.turretLeftkey[self.number] # turret
        self.turretRightkey = Tank.turretRightkey[self.number] # turret
        self.forwardkey = Tank.forwardkey[self.number] # move tank
        self.backwardkey = Tank.backwardkey[self.number] # reverse tank
        self.tankLeftkey = Tank.tankLeftkey[self.number] # rotate tank
        self.tankRightkey = Tank.tankRightkey[self.number] # rotat tank
        image = pygame.Surface((Tank.side,Tank.side)) # created on the fly
        image.fill((128,128,128)) # fill grey
        if self.side > 10:
             pygame.draw.rect(image, self.color, (5,5,self.side-10, self.side-10)) #tank body, margin 5
             pygame.draw.rect(image, (90,90,90), (0,0,self.side//6, self.side)) # track left
             pygame.draw.rect(image, (90,90,90), (self.side-self.side//6, 0, self.side,self.side)) # right track
             pygame.draw.rect(image, (255,0,0), (self.side//6+5 , 10, 10, 5)) # red bow rect left
        pygame.draw.circle(image, (255,0,0), (self.side//2,self.side//2), self.side//3 , 2) # red circle for turret
        image = pygame.transform.rotate(image,-90) # rotate so to ldook east
        self.image0 = image.convert_alpha()
        self.image = image.convert_alpha()
        self.rect = self.image0.get_rect()
        #---------- turret ------------------
        self.firestatus = 0.0 # time left until cannon can fire again
        self.mgfirestatus = 0.0 # time until mg can fire again
        self.mg2firestatus = 0.0 # time until turret mg can fire again
        self.turndirection = 0    # for turret
        self.tankturndirection = 0
        self.movespeed = Tank.movespeed
        self.turretTurnSpeed = Tank.turretTurnSpeed
        self.tankTurnSpeed = Tank.tankTurnSpeed
        Turret(self) # create a Turret for this tank
 
    
 

    def update(self, seconds):
        # no need for seconds but the other sprites need it
        #-------- reloading, firestatus----------
        if self.firestatus > 0:
            self.firestatus -= seconds # cannon will soon be ready again
            if self.firestatus <0:
                self.firestatus = 0 #avoid negative numbers
        if self.mgfirestatus > 0:
            self.mgfirestatus -= seconds # bow mg will soon be ready again
            if self.mgfirestatus <0:
                self.mgfirestatus = 0 #avoid negative numbers
        if self.mg2firestatus > 0:
            self.mg2firestatus -= seconds # turret mg will soon be ready again
            if self.mg2firestatus <0:
                self.mg2firestatus = 0 #avoid negative numbers
 
        # ------------ keyboard --------------
        pressedkeys = pygame.key.get_pressed()
        # -------- turret manual rotate ----------
        self.turndirection = 0    #  left / right turret rotation
        if pressedkeys[self.turretLeftkey]:
            self.turndirection += 5
        if pressedkeys[self.turretRightkey]:
            self.turndirection -= 5
 
        #---------- tank rotation ---------
        self.tankturndirection = 0 # reset left/right rotation
        if pressedkeys[self.tankLeftkey]:
            self.tankturndirection += 5
        if pressedkeys[self.tankRightkey]:
            self.tankturndirection -= 5
 
        # ---------------- rotate tank ---------------
        self.tankAngle += self.tankturndirection * self.tankTurnSpeed * seconds # time-based turning of tank
        # angle etc from Tank (boss)
        oldcenter = self.rect.center
        oldrect = self.image.get_rect() # store current surface rect
        self.image  = pygame.transform.rotate(self.image0, self.tankAngle) 
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter 
        # if tank is rotating, turret is also rotating with tank !
        # -------- turret autorotate ----------
        self.turretAngle += self.tankturndirection * self.tankTurnSpeed * seconds  + self.turndirection * self.turretTurnSpeed * seconds # time-based turning
        # ---------- fire cannon -----------
        if (self.firestatus ==0) and (self.ammo > 0):
            if pressedkeys[self.firekey]:
                self.firestatus = Tank.recoiltime # seconds until tank can fire again
                Bullet(self)    
                self.ammo -= 1
        # ---------- movement ------------
        self.dx = 0
        self.dy = 0
        self.forward = 0 # movement calculator
			
	
        if pressedkeys[self.forwardkey]:
            self.forward += 1
        if pressedkeys[self.backwardkey]:
            self.forward -= 1
        # if both are pressed togehter, self.forward becomes 0
        if self.forward == 1:
	    
            self.dx =  math.cos(degrees_to_radians(self.tankAngle)) * self.movespeed
            self.dy =  -math.sin(degrees_to_radians(self.tankAngle)) * self.movespeed
	     
        if self.forward == -1:
            self.dx =  -math.cos(degrees_to_radians(self.tankAngle)) * self.movespeed
            self.dy =  math.sin(degrees_to_radians(self.tankAngle)) * self.movespeed
	

 
        # ------------- check border collision ---------------------
        self.pos[0] += self.dx * seconds
        self.pos[1] += self.dy * seconds
        if self.pos[1] + self.side//2 >= Config.height:
            self.pos[1] = Config.height - self.side//2
            self.dy = 0 # crash into border
        elif self.pos[1] -self.side/2 <= 0:
            self.pos[1] = 0 + self.side//2
            self.dy = 0
        # ---------- paint sprite at correct position ---------
        self.rect.centerx = round(self.pos[0], 0) #x
        self.rect.centery = round(self.pos[1], 0) #y
        if self.rect.left > 1260:
            self.rect.right = 0


 
class Turret(pygame.sprite.Sprite):
    def __init__(self, boss):
        pygame.sprite.Sprite.__init__(self, self.groups) # THE most important line !
        self.boss = boss
        self.side = self.boss.side        
        self.images = {} # how much recoil after shooting, reverse order of apperance
        self.images[0] = self.draw_cannon(0)  
        self.images[1] = self.draw_cannon(1)
        self.images[2] = self.draw_cannon(2)
        self.images[3] = self.draw_cannon(3)
        self.images[4] = self.draw_cannon(4)
        self.images[5] = self.draw_cannon(5)
        self.images[6] = self.draw_cannon(6)
        self.images[7] = self.draw_cannon(7)
        self.images[8] = self.draw_cannon(8)  # position of max recoil
        self.images[9] = self.draw_cannon(4)
        self.images[10] = self.draw_cannon(0) 
 
    def update(self, seconds):        
        if self.boss.firestatus > 0:
            self.image = self.images[int(self.boss.firestatus // (Tank.recoiltime / 10.0))]
        else:
            self.image = self.images[0]
        # --------- rotating -------------
        # angle etc from Tank (boss)
        oldrect = self.image.get_rect() # store current surface rect
        self.image  = pygame.transform.rotate(self.image, self.boss.turretAngle) 
        self.rect = self.image.get_rect()
        # ---------- move with boss ---------
        self.rect = self.image.get_rect()
        self.rect.center = self.boss.rect.center
 
    def draw_cannon(self, offset):
         # painting facing right, offset is the recoil
         image = pygame.Surface((self.boss.side * 2,self.boss.side * 2)) # created on the fly
         image.fill((128,128,128)) # fill grey
         pygame.draw.circle(image, (255,0,0), (self.side,self.side), 11, 0) # red circle
         pygame.draw.circle(image, (0,255,0), (self.side,self.side), 10, 0) # green circle
         pygame.draw.rect(image, (255,0,0), (self.side-10, self.side + 10, 15,2)) # turret mg rectangle
         pygame.draw.rect(image, (0,255,0), (self.side-10 -
 offset,self.side - 5, self.side - offset,8)) # green cannon
         pygame.draw.rect(image, (255,0,0), (self.side-10 - offset,self.side - 5, self.side - offset,9),1) # red rect 
         image.set_colorkey((128,128,128))
         return image

class WAll(pygame.sprite.Sprite):
 
    def __init__(self, x, y, width, height, color):
        super(WAll, self).__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        if (width > 20):
            self.vertical = False
        else:
            self.vertical = True
	    
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        self.x = x
        self.y =y
        self.dx =0
        self.dy =0
 
 
    def stop_collision(self, wall):
        b = pygame.sprite.collide_rect(self,wall)
        if b:
           if (self.vertical):
              if wall.pos[0] < self.x:
                   wall.pos[0] -= 5
              else:
                   wall.pos[0] += 5	
           else:
              if wall.pos[1] < self.y:
                   wall.pos[1] -= 5
              else:
                   wall.pos[1] += 5	
			
class Bonus(pygame.sprite.Sprite):
    maxlifetime = 7.0 # seconds
    def __init__(self, x, y, width=15, height=15):
        super(Bonus, self).__init__()
        self.image = pygame.Surface([width, height])
        pygame.draw.circle(self.image, (255,0,0), (x,y), 5 , 2)
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x
        self.x = x
        self.y = y
        self.dx =0
        self.dy =0
        self.lifetime = 0.0
        self.update()
        self.a = random.randint(0,2)
 
    def update(self, seconds=0.0):
	
        self.lifetime += seconds
        if self.lifetime > Bonus.maxlifetime:
            self.kill()
			

# ---------------- End of classes --------------------



#------------ defs ------------------
def radians_to_degrees(radians):
    return (radians / math.pi) * 180.0
 
def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)
 
def main():
    pygame.init()
    screen = pygame.display.set_mode([width, height])


    pygame.display.set_caption('tank trouble')
    background = pygame.Surface(([width, height]))
    background.fill((gray)) # fill grey light 
 
    background = background.convert()
    screen.blit(background, (0,0)) # delete all
    clock = pygame.time.Clock()    # create pygame clock object
    FPS = Config.fps               # desired max. framerate 
    playtime = 0
 

	 
	
	  
    wallgroup = pygame.sprite.Group()	 
    tankgroup = pygame.sprite.Group()
    bulletgroup = pygame.sprite.Group()
    bonusgroup = pygame.sprite.Group()
    allgroup = pygame.sprite.LayeredUpdates()

    Tank._layer = 4   # base layer
    Bullet._layer = 7 # to prove that Bullet is in top-layer
    Turret._layer = 6 # above Tank & Tracer
 
    #assign default groups to each sprite class
    Tank.groups = tankgroup, allgroup
    Turret.groups = allgroup
    Bullet.groups = bulletgroup, allgroup
    WAll.groups = allgroup,wallgroup
    Bonus.groups = allgroup,bonusgroup
    player1 = Tank((150,150), 90) # create  first tank, looking north
    player2 = Tank((450,250), -90) # create second tank, looking south
    bonus1 = Bonus(400,400)
    bonusgroup.add(bonus1)
    walls = []
    wall1 = [[0, 0, 1280, 20, BLACK],
		         [0, 580, 1280, 20, BLACK],
		         [0, 0, 20, 600, BLACK],
		         [1260, 0, 20, 600, BLACK],
[0, 140,110,20,BLACK],[240,140,110,20,BLACK],[460,140,110,20,BLACK],[120,300,110,20,BLACK],[350,300,110,20,BLACK],
[460,300,110,20,BLACK],[0,440,110,20,BLACK],[350,440,110,20,BLACK],[1160,440,110,20,BLACK],[350,300,20,140,BLACK],[240,0,20,140,BLACK],[930,0,20,140,BLACK],[810,300,20,300,BLACK],[810,300,150,20,BLACK],
[660,450,150,20,BLACK]]
    wall2= [[0, 0, 1280, 20, BLACK],
		         [0, 580, 1280, 20, BLACK],
		         [0, 100, 200, 20, BLACK],[200, 100, 20, 400,BLACK]
		         ,[1260, 0, 20, 200, BLACK],[1000,300,110,20,BLACK],
[960,300,110,20,BLACK],[0,440,110,20,BLACK],[550,0,20,100,BLACK],[730,300,200,20,BLACK],[1060,440,110,20,BLACK],[450,300,20,140,BLACK],[840,0,20,140,BLACK],[930,520,20,140,BLACK],[810,300,20,300,BLACK],[810,300,150,20,BLACK],
[660,450,150,20,BLACK]]
    walls.append(wall1)
    walls.append(wall2)
    a = random.randint(0,len(walls)-1)
    for item in walls[a]:
        wall = WAll(item[0], item[1], item[2], item[3], item[4])
        wallgroup.add(wall)
	


    mainloop = True    

       
    while mainloop:
	
        milliseconds = clock.tick(Config.fps)  # milliseconds passed since last frame
        seconds = milliseconds / 1000.0 # seconds passed since last frame (float)
        playtime += seconds
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False # exit game
    
        for wall in wallgroup:
            crashgroup = pygame.sprite.spritecollide(wall, bulletgroup,False, pygame.sprite.collide_rect)
            for bullet in crashgroup :    
                bullet.elastic_collision(wall)
        for tank in tankgroup :
                crashgroup = pygame.sprite.spritecollide(tank, bulletgroup,False, pygame.sprite.collide_rect)
                for bullet in crashgroup:
                    if (bullet.lifetime >0.2):
                        background.fill(BLACK,tank.rect)
                        screen.fill(BLACK,tank.rect)
                        pygame.display.flip()
                        tank.kill()
                        main()
        for tank in tankgroup:
            crashgroup = pygame.sprite.spritecollide(tank, bonusgroup,True, pygame.sprite.collide_rect)
            for bonus in crashgroup :    
                if bonus.a == 0:
                    tank.recoiltime = 0
                elif bonus.a == 1:
                    tank.movespeed = 300
                    pygame.display.flip()
                tank.update(seconds)
			    
				
        for wall in wallgroup:
            crashgroup = pygame.sprite.spritecollide(wall, tankgroup,False, pygame.sprite.collide_rect)
            for tank in crashgroup :    
                wall.stop_collision(tank)
    
    
	# --- Drawing ---
	
    
        screen.blit(background, (0,0)) # delete all
        screen.fill(gray)
        allgroup.clear(screen, background) # funny effect if you outcomment this line
        allgroup.update(seconds)
        allgroup.draw(screen)
        wallgroup.draw(screen)
        bonusgroup.draw(screen)
        pygame.display.flip() # flip the screen 30 times a second
	
    return 0	     
     
if __name__ == '__main__':
    main()
