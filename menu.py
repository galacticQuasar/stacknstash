import random,pygame
import constants,credit,towns
from pygame.locals import *

#background animation
class fall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        #choose random block for image
        choice = random.choice(constants.blockList)
        self.image = choice[-2].convert_alpha()
        self.rect = self.image.get_rect()
        self.changey = 0

    def update(self):
        #accelerate until at 15 pixels/frame
        self.changey += 0.5
        if self.changey >= 15:
            self.changey = 15
        self.rect.y += self.changey
        if self.rect.y > constants.SCREEN_HEIGHT:
            self.kill()#remove block if it can't be seen anymore

class button(pygame.sprite.Sprite):
    def __init__(self,colour,text,posRect):
        super().__init__()
        self.colour = colour
        #text should be already made into surface
        self.text = text
        self.textRect = self.text.get_rect()
        self.rect = posRect
        self.image = pygame.Surface((self.rect.width,self.rect.height)).convert_alpha()
        self.textRect.center = (self.rect.width/2,self.rect.height/2)#put text at centre

    def update(self):
        #if mouse is over the block
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            newC = []
            for i in self.colour:
                if i < 205:
                    newC.append(i + 50)
                else:
                    newC.append(255)#can't get brighter
            newC = tuple(newC)
            self.image.fill(newC)
        else:
            self.image.fill(self.colour)
        self.image.blit(self.text,self.textRect)

def Menu(DISPLAYSURF,clock,font):#runs a menu before the game
    done = False
    pygame.mixer.music.load("music/menu.mp3")
    pygame.mixer.music.play(-1)
    objects = pygame.sprite.LayeredUpdates()
    
    pos1 = pygame.Rect(200,500,300,80)
    text1 = font.render('Start Game',False,constants.BLACK).convert_alpha()
    button1 = button(constants.GREEN,text1,pos1)
    objects.add(button1)
    objects.change_layer(button1,1)#bring buttons to the front
    pos2 = pygame.Rect(200,615,300,60)
    text2 = font.render('Bonus Mode',False,constants.BLACK).convert_alpha()
    button2 = button(constants.GREEN,text2,pos2)
    objects.add(button2)#do same things for 2nd button
    objects.change_layer(button2,1)

    text3 = font.render('credits',False,constants.BLACK).convert_alpha()
    height = constants.SCREEN_HEIGHT - text3.get_height() - 20
    pos3 = pygame.Rect(5,height,text3.get_width() + 10,50)
    button3 = button(constants.YELLOW,text3,pos3)
    objects.add(button3)
    objects.change_layer(button3,1)

    version = font.render(constants.v,False,constants.BLACK).convert_alpha()
    versionPos = (constants.SCREEN_WIDTH - version.get_width() - 5,constants.SCREEN_HEIGHT - 50)
    pause = pygame.time.get_ticks()#know when to spawn a new block

    title = pygame.image.load('sprites/title.png').convert_alpha()
    title = pygame.transform.scale2x(title)
    titleRect = title.get_rect()
    titleRect.y = 100
    titleRect.centerx = constants.SCREEN_WIDTH/2#half across screen
    
    while not done:
        if pause <= pygame.time.get_ticks():
            pause = pygame.time.get_ticks() + 1000#wait 1 second
            newBlock  = fall()
            newBlock.rect.x = random.randint(0,constants.SCREEN_WIDTH - 120)
            objects.add(newBlock)
            
        for event in pygame.event.get():
            
            if event.type == QUIT:
                return False,True # return done and quit
            
            elif event.type == MOUSEBUTTONDOWN:
                if button1.rect.collidepoint(pygame.mouse.get_pos()):
                    return False,False #no bonus mode
                elif button2.rect.collidepoint(pygame.mouse.get_pos()):
                    return True, False #bonus mode on
                elif button3.rect.collidepoint(pygame.mouse.get_pos()):
                    if not credit.roll(DISPLAYSURF,clock):
                        return False,True
                    else:
                        pygame.mixer.music.load("music/menu.mp3")
                        pygame.mixer.music.play(-1)#restart music
                        towns.font = font
                        

        #update and drawing
        objects.update()
        DISPLAYSURF.fill(constants.SKY_BLUE)
        
        objects.draw(DISPLAYSURF)
        DISPLAYSURF.blit(title,titleRect)
        DISPLAYSURF.blit(version,versionPos)
        pygame.display.flip()
        clock.tick(60)
        pygame.display.update()
        
        
                
        
