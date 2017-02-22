import pygame,random,math
from pygame.locals import *
import constants, characters,blocks

#only use text because pygame not initialised yet
levelDesigns = ["sprites/back_jungle.png",
                "sprites/back_sand.png",
                "sprites/back_volcano.png"]
levelMusic = ["music/dungeon1.mp3",
              "music/dungeon2.wav",
              "music/dungeon3.mp3"]

#makes easier to handle simple images with pygame
class box(pygame.sprite.Sprite):
    def __init__(self,image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()

class Level(pygame.sprite.Sprite):
    def __init__(self,cleared,hero,hold):
        super().__init__()
        #make surface for background image
        self.image = pygame.Surface((11*constants.blockSize+200,110))
        self.rect = self.image.get_rect()
        self.rect.topleft = constants.mainDunPos
        baseTile = pygame.image.load(levelDesigns[cleared%3]).convert_alpha()
        pygame.mixer.music.load(levelMusic[cleared%3])
        pygame.mixer.music.play(-1)
        self.hold = hold
        self.objects = pygame.sprite.LayeredUpdates()
        self.enemies = []#keeps enemies in an easily accesible list
        self.target = None #sees who hero is fighting

        #health bar
        self.healthBar = pygame.Rect(0,0,100,15)
        self.penalty = 0#how much hero's stats go down

        #stuff for shifting the world
        self.worldShift = 0
        self.maxShift = 900 + 40*cleared

        if self.maxShift > 2000:
            self.maxShift = 2000#don't get bigger than 2000
        monsterNo = 5 + math.floor(cleared/3)#extra enemy every 3 levels
        if monsterNo > 13:
            monsterNo = 13

        #stores the background
        width = 0
        while width < self.maxShift+550: #add the base width of the screen to the width
            background = box(baseTile)
            background.rect.topleft = (width,0)
            self.objects.add(background)
            self.objects.change_layer(background,-2)
            width += background.rect.width
        self.hero = hero
        self.objects.add(self.hero)
        
        #place a door at the end of the level
        door = box(pygame.image.load("sprites/door.png").convert())
        door.image.set_colorkey(constants.BLACK)
        door.rect.right = self.maxShift + self.rect.width - 10
        door.rect.y = 110 - door.rect.height - 5
        self.objects.add(door)
        self.objects.change_layer(door,-1)
        
        #enemy creation
        for i in range(monsterNo):
            x = 0
            while x == 0:
                x = random.randint(100, self.maxShift + 250)
                for enemy in self.enemies:
                    if abs(x - enemy.rect.centerx) < 60: #if within 60 pixels of another enemy's centre
                        x = 0 #find new x
                        
            foe = characters.Enemy(cleared,hero)
            #position enemy
            foe.rect.centerx = x
            #foe.rect.bottom = self.rect.bottom - 20
            self.enemies.append(foe)
            self.objects.add(foe)
            

    def update(self):
        self.objects.update()
        self.objects.draw(self.image)
        #once quarter across screen shift screen
        if self.hero.rect.x > round(self.rect.width/4) and self.worldShift < self.maxShift:
            self.shift(round(self.rect.width/4) - self.hero.rect.x) #make the shift negative
        #fighting
        for foe in self.enemies:
            if (foe.rect.x - self.hero.rect.right) < 15 and not self.hero.fighting:
                foe.fighting = True
                self.target = foe
                self.hero.target = foe
                self.hero.fighting = True
                #make hero image first of the walk image
                self.hero.image.fill(constants.BLACK)
                self.hero.image.blit(self.hero.spriteSheet,(0,0),(12,712,44,58))
                self.hero.width = 12
                
        if self.target != None:
            if self.target.stats["HP"] <= 0 and not self.hero.dead:
                #reset hero for next fight
                self.hero.fighting = False
                self.hero.dir = 1
                self.hero.sinPos = 0
                self.hero.rect.y = self.hero.basey
                #give the hero the treasure for the victory
                for i in range(self.target.stats["Treasure"]):
                    blockType = random.choice(constants.blockList)
                    newBlock = blocks.Block(self.hold,blockType)
                    self.hold.add(newBlock)
                #remove the enemy from the groups
                self.enemies.remove(self.target)
                self.target.kill()
                self.target.noise.play()
                self.target = None
                if constants.multi:
                    self.hero.changex = 0

        #give hero a penalty for holding too much
        if len(self.hold.blockList) > 3*(self.penalty+1):
            self.penalty += 1
            for i in self.hero.stats:
                if i != 'MAX_HP':
                    self.hero.stats[i] -= 1
        elif len(self.hold.blockList) < 3*self.penalty:
            self.penalty -= 1
            for i in self.hero.stats:
                if i != 'MAX_HP':
                    self.hero.stats[i] += 1
        
        #make health bar percentage of max health
        self.healthBar.width = round(100 *(self.hero.currentHP/self.hero.stats['MAX_HP']))
        pygame.draw.rect(self.image,constants.RED,self.healthBar)


    def shift(self,shiftx):
        for item in self.objects:
            item.rect.x += shiftx
        #make world shift a positive value
        self.worldShift -= shiftx
            
            
