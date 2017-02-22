import pygame,random,math
from pygame.locals import *
import constants
        
class Hero(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.spriteSheet = pygame.image.load("sprites/characters/hero.png").convert()
        self.image = pygame.Surface((44,58)).convert()
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 110 - self.rect.height #positon at bottom of the background
        self.changex = 1
        self.speed = 1#what base changex is
        self.diffx = 0#measures the change in x
        self.width = 12#make image the first from the sprite sheet walk
        self.image.blit(self.spriteSheet,(0,0),(self.width,712,44,58))
        self.multi = constants.multi #easy reference for bonus mode

        #variables for fighting
        self.fighting = False
        self.attack = False
        self.target = None #tells us which enemy we're fighting
        self.dir = 1 #direction to move in a fight
        self.sinPos = 0
        self.basey = self.rect.y#use current height as base for sine curve
        self.pause = pygame.time.get_ticks()
        self.stats = {
            "ATK" : 7,
            "DEF" : 8,
            "MAX_HP"  : 25,
            "SPD" : 5
            }
        #attack sound
        self.swing = pygame.mixer.Sound('music/effects/swing.ogg')
        #copy the hp to know its value
        self.currentHP = self.stats["MAX_HP"]
        self.dead = False #he's not dead yet
        #equipment
        self.armour = {
            "ATK": None,
            "DEF": None,
            "SPD": None
            }
        #for cities
        self.talking = False
        self.gold = 30

    def update(self):
        if self.dead:#check if neeed to play dying animation
            self.diffx += 1
            if self.diffx >= 20:
                self.die()
                self.diffx = 0
        elif not self.fighting:#not fighting so walk
            self.diffx += abs(self.changex)
            if self.rect.right < 530:
                self.rect.x += self.changex
            if self.diffx >= 10:
                self.walk()
                self.diffx = 0
        elif self.fighting:
            if self.sinPos == 0 and self.attack == True: #if back at start reset attack
                    self.dir = 1
                    self.attack = False
                    self.pause = pygame.time.get_ticks()
            self.fight()

    def walk(self):
        #move along in the animation
        self.width += 64
        #if at the end then go back to the start
        if self.width > 576:
            self.width = 12
        #reset image
        self.image.fill(constants.BLACK)
        self.image.blit(self.spriteSheet,(0,0),(self.width,712,44,58))
        if self.changex < 0:
            self.image = pygame.transform.flip(self.image,True,False)

    def die(self): #dying animation
        self.width += 64
        if self.width > 332:#don't go past last frame
            self.width = 332
        self.image.fill(constants.BLACK)
        self.image.blit(self.spriteSheet,(0,0),(self.width,1290,44,58))
        
    def fight(self):
        Foe = self.target.stats #syntax sugar
        #if time passed is greater than 1.5s - the speed and not attacking
        if (pygame.time.get_ticks() - self.pause) > (1500 - 100*self.stats["SPD"]) and (not self.attack and not self.multi):
            self.attack = True
        if self.attack:
            self.rect.x += 1*self.dir
            #sinPos imitates the rectx but is centred for the sine curve
            self.sinPos += 1*self.dir
            self.rect.y = self.basey -10*math.sin(12*self.sinPos*math.pi/180)#make half a sine wave that goes 15 pixels
            if self.rect.colliderect(self.target.rect):
                self.dir = -1#start moving back
                dmg = self.stats["ATK"] - math.floor(Foe["DEF"]*2/3)
                if dmg < 0:
                    dmg = 0
                Foe["HP"] -= dmg
                if Foe["HP"] > 0:
                    self.swing.play()

    def startTalk(self):
        self.talking = True
        self.changex = 0
        self.image.fill(constants.BLACK)
        self.image.blit(self.spriteSheet,(0,0),(12,712,44,58))
        if self.speed < 0:#face correct way
            self.image = pygame.transform.flip(self.image,True,False)
        self.width = 12        
        
#possible images for enemies
Images = ["sprites/characters/monster1.PNG",
          "sprites/characters/monster2.PNG",
          "sprites/characters/monster3.PNG",
          "sprites/characters/monster4.PNG",
          "sprites/characters/monster5.PNG"]

death = ['music/enemies/demon.ogg',
         'music/enemies/wolf.ogg',
         'music/enemies/thief.ogg',
         'music/enemies/giant.ogg',
         'music/enemies/ogre.ogg']

class Enemy(pygame.sprite.Sprite):
    def __init__(self,cleared,hero):
        super().__init__()
        choice = random.randint(0,4)
        self.image = pygame.image.load(Images[choice]).convert_alpha()
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        self.hero = hero #locates the hero for dealing damage
        self.rect.y = 110 - self.rect.height
        #noise made when dead
        self.noise = pygame.mixer.Sound(death[choice])

        self.fighting = False
        #attack sound
        self.swing = pygame.mixer.Sound('music/effects/swing.ogg')
        
        self.attack = False
        self.dir = -1
        self.sinPos = 0
        self.basey = self.rect.y
        self.pause = pygame.time.get_ticks()
        self.stats = {
            "ATK" : 5,
            "DEF" : 3,
            "HP"  : 7,
            "SPD" : 4,
            "Treasure" : 2#no of blocks given after defeat
            }
        
        #give enemies some stat variance
        points = 7 + 3*math.floor(cleared/2)
        bonus = random.randint(0,2)
        self.stats["Treasure"] += bonus
        points += bonus*2#with more treasure the stats increase
        for trait in self.stats:
            if trait != "HP" and trait != "Treasure":
                #can also decrease the stat
                bonus = random.randint(-1,2 + math.floor(cleared/2))
                self.stats[trait] += bonus
                points -= bonus
        #give remaining points to HP
        self.stats["HP"] += points
        
    def update(self):
        if self.fighting:
            if self.sinPos == 0 and self.attack == True:#if back at start reset attack
                self.dir = -1
                self.attack = False
                self.pause = pygame.time.get_ticks()
            self.fight()
        
    def fight(self):
        Chara = self.hero.stats#syntax sugar
        #same as hero's function
        if (pygame.time.get_ticks() - self.pause) > (1500 - 100*self.stats["SPD"]) and not self.attack:
            self.attack = True
        if self.attack:
            self.rect.x += 1*self.dir
            self.sinPos += 1*self.dir
            self.rect.y = self.basey + 10*math.sin(12*self.sinPos*math.pi/180)
            if self.rect.colliderect(self.hero.rect):
                self.dir = 1
                dmg = self.stats["ATK"] - math.floor(Chara["DEF"]*2/3)
                if dmg < 0:
                    dmg = 0
                self.hero.currentHP -= dmg
                self.swing.play()
            
            
    
