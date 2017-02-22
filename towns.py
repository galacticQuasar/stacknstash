import pygame,constants,dungeons,blocks
from pygame.locals import *

font = None
def longText(sample): # convert multiple lines of text into one image

    width = 0 # width of final surface
    images = []#store the images of the texts
    for line in sample:#loop through text sample
        text = font.render(line,False,constants.BLACK)
        images.append(text)
        if text.get_width() > width:
            #make the width size of largest line
            width = text.get_width()
    img = pygame.Surface((width,32*len(sample) + 20))
    img.fill(constants.WHITE)
    final = dungeons.box(img)
    for i in range(len(images)):
        line = images[i]
        posRect = line.get_rect()# centres the text
        posRect.midtop = (round(width/2),i*32)
        final.image.blit(line,posRect)
    return final

signText = [[
    "Helloooo there, I'm your",
    "Friendly Neibourhood Signpost!",
    'Seeee reverse for statistics!'
    ],
    ['...','*cough cough*']]

class Town(pygame.sprite.Sprite):
    def __init__(self,cleared,hero,merchant,potioner):
        super().__init__()
        height = constants.mainInvenPos[1] - constants.mainDunPos[1] - 10
        width = 11*constants.blockSize + 200
        #make a surface to cover both the dungeon area and hold
        self.image = pygame.Surface((width,height))
        self.rect = self.image.get_rect()
        self.rect.topleft = constants.mainDunPos
        baseTile = pygame.image.load(dungeons.levelDesigns[cleared%3]).convert_alpha()
        pygame.mixer.music.load('music/town.mp3')
        pygame.mixer.music.play(-1)
        
        self.objects = pygame.sprite.LayeredUpdates()
        self.text = None # stores text
        #stores the hero and other objects
        self.low = pygame.Surface((11*constants.blockSize+200,110))
        self.lowRect = self.low.get_rect()
        self.lowRect.y = self.rect.height - self.lowRect.height
        self.lowRect.x = 0

        #stuff for shifting the world
        self.worldShift = 0
        self.maxShift = 100

        #stores the background
        width = 0
        while width < self.maxShift+550:
            background = dungeons.box(baseTile)
            background.rect.topleft = (width,0)
            self.objects.add(background)
            self.objects.change_layer(background,-2)
            width += background.rect.width
        #add characters
        self.hero = hero
        self.objects.add(self.hero)
        self.hero.currentHP += 10#restore 10hp
        if self.hero.currentHP > self.hero.stats['MAX_HP']:
            self.hero.currentHP = self.hero.stats['MAX_HP']
        
        self.merchant = merchant
        self.decide = None
        self.objects.add(merchant)
        self.objects.change_layer(merchant,-1)
        self.potioner = potioner
        self.objects.add(potioner)
        self.objects.change_layer(potioner,-1)
        
        self.sign = dungeons.box(pygame.image.load("sprites/signpost.png"))
        self.sign.rect.x = 90
        self.sign.rect.y = 110 - self.sign.rect.height - 5
        self.objects.add(self.sign)
        self.objects.change_layer(self.sign,-1)
        self.talking = None #tells who the hero is talking to
        self.speechPos = 0

        self.money = pygame.Surface((90,32)).convert()
        self.money.set_colorkey(constants.BLACK)
        self.coins = pygame.image.load("sprites/items/Coins.PNG").convert_alpha()
        #displays amount of money in top right
        self.money = dungeons.box(self.money)
        self.money.rect.right = self.rect.right - 75
        self.money.rect.y = 0
        self.objects.add(self.money)

        #health bar
        self.healthBar = pygame.Rect(0,0,100,15)

    def update(self):
        self.objects.update()
        self.objects.draw(self.low)
         #once quarter across screen shift screen
        if self.hero.rect.x > round(self.rect.width/4) and self.worldShift < self.maxShift:
            self.shift(round(self.rect.width/4) - self.hero.rect.x) #make the shift negative
        #shift opposite way for moving left
        elif self.hero.rect.x < round(self.rect.width/4) and self.worldShift > 0:
            self.shift(round(self.rect.width/4) - self.hero.rect.x)
        if self.talking == "sign":
            heroInfo  = []
            for i in self.hero.stats:
                heroInfo.append(i+' : ' + str(self.hero.stats[i]))
            signText[1] = heroInfo
            self.signTalk()
        #draw everything onto main image
        self.image.fill(constants.WHITE)
        self.healthBar.width = round(100 *(self.hero.currentHP/self.hero.stats['MAX_HP']))
        pygame.draw.rect(self.low,constants.RED,self.healthBar)
        self.image.blit(self.low,self.lowRect)
        heroCoin = font.render(str(self.hero.gold),False,constants.WHITE)
        self.money.image.fill(constants.BLACK)
        self.money.image.blit(self.coins,(0,0))
        self.money.image.blit(heroCoin,(40,0))
        if self.text != None:
            self.image.blit(self.text.image,self.text.rect)
        if self.decide != None:
            self.image.blit(self.decide.image,self.decide.rect)

                                 
    def shift(self,shiftx):
        for item in self.objects:
            item.rect.x += shiftx
        #make world shift a positive value
        self.worldShift -= shiftx
        self.money.rect.x -= shiftx

    #conversations with NPC's                           
    def signTalk(self):
        if self.speechPos < len(signText):#if not at the end of the speech
            self.text = longText(signText[self.speechPos])#convert to an image
            self.text.rect.midtop = (round(self.rect.width/2),0)#place text at middle
        else: #at end so reset everything
            self.speechPos = 0
            self.hero.talking = False
            self.talking = None
            self.text = None

descriptMer = [
    ['Great for dicing cheese',
     'and cutting vegetables'],
    ['Doubles as a','XXXXL plate'],
    ['Wings make everything',
     'better ...and faster'],
    ['So you can buy more',' of my things']
    ]

class Merchant(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("sprites/characters/merchant.PNG")
        self.image = pygame.transform.scale2x(self.image)
        self.rect = self.image.get_rect()
        self.rect.y = 110 -self.rect.height - 5
        self.rect.x = 200
        self.wares = [ #list of equipment possible to sell
            "ATK",
            "DEF",
            "SPD",
            "INVEN"
            ]
        self.sale = []#describes what hero is buying
        self.buying = False # is the hero selling?
        self.talking = False #if talking to the hero
        self.choice = 0 #number in a list that has been chosen
        self.maxChoice = 1 #highest number choice can be
        self.options = []
        self.finish = False # if player made their decision
        self.total = 0
        self.price = 0 #price of an item
        self.invenNo = 1 #number of inventories(has maximum amount)
        self.skill = None
        self.pending = False #if we need to wait for confirmation for purchase
        self.success = None

    def update(self):
        lvl = self.level
        if self.talking:
            
            if self.success is True: #check first if sale finished
                speech = ["Would you like to", "do anything else?"]
                lvl.text = longText(speech) #position text one third across screen
                lvl.text.rect.center = (round(lvl.rect.width/3),50)
                if len(self.options) == 0:#only define if list is empty
                    self.options = [">No"," Yes"]
                lvl.decide = longText(self.options)
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    if not bool(self.choice):#player chose to end
                        self.cancel()
                    else:#otherwise reset variables to start again
                        self.choice = 0
                        self.buying = False
                        self.sale = []
                        self.success = None
                        self.options = []
                        self.skill = None
                        self.finish = False
                    
            elif self.success is False:
                if self.invenNo == 4:
                    speech = ['You already have plenty of inventories!']
                elif lvl.hero.gold < self.price:
                    speech = ['You need more cash']
                else:    
                    speech = ['You dun goofed',
                              'free up some more space']
                lvl.text = longText(speech)
                lvl.text.rect.center = (round(lvl.rect.width/2),50)
                if self.finish:
                    self.cancel()
                    self.finish = False
            
            #if not yet buying or selling 
            elif self.sale == [] and not self.buying:
                speech = ["Would you like to", "buy or sell?"]
                lvl.text = longText(speech) #position text one third across screen
                lvl.text.rect.center = (round(lvl.rect.width/3),50)
                if len(self.options) == 0:#only define if list is empty
                    self.options = [">Buy"," Sell"]
                lvl.decide = longText(self.options)
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    self.buying = not bool(self.choice) # choice is only 0 or 1
                    lvl.decide = None
                    self.options = []
                    if not self.buying:
                        self.sale = None
                        self.maxChoice = 0
                    else:
                        self.maxChoice = 3#prepare for selling
                    self.choice = 0
                    self.finish = False
                    
            elif self.sale == None: #selling
                speech = ["What do you want to sell?",
                          "",
                          "total:"+str(self.total)]
                lvl.text = longText(speech)
                lvl.text.rect.center = (round(lvl.rect.width/2),70)
                if self.finish: # give accumilated total to player
                    lvl.hero.gold += self.total
                    self.total = 0#reset total
                    self.finish = False
                    self.success = True
                    self.maxChoice = 1
                    
            elif self.buying == True and self.sale == [] and self.success == None:#find item to buy
                speech = descriptMer[self.choice]
                lvl.text = longText(speech)
                lvl.text.rect.center = (round(lvl.rect.width/4) + 10,50)
                if self.options == []:
                    self.options = [">Sword"," Shield"," Wings"," Inven."] #same order as wares list
                part1 = longText(self.options[:2])
                part2 = longText(self.options[2:])#split into two sections to display separately
                full = dungeons.box(pygame.Surface((part1.rect.width + part2.rect.width + 10,32*2 + 5)).convert())
                full.image.set_colorkey(constants.WHITE)
                full.image.fill(constants.WHITE)
                full.image.blit(part1.image,(0,0))
                part2.rect.right = full.rect.right
                full.image.blit(part2.image,part2.rect)
                lvl.decide = full
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    self.sale.append(self.options[self.choice])#get item from options
                    self.skill = self.wares[self.choice]
                    self.options = []
                    self.maxChoice = 3
                    if self.skill == "INVEN":
                        self.sale.append(None)#don't need a rank for inventory
                        self.maxChoice = 1
                        self.price = 75*self.invenNo
                        if self.invenNo == 4:#if there are 4 inventories
                            self.success = False
                            self.sale = []
                            lvl.decide = None
                    self.choice = 0
                    self.finish = False

            elif len(self.sale) == 1: #get rank of item
                speech = ["What Quality?"]
                lvl.text = longText(speech)
                lvl.text.rect.center = (round(lvl.rect.width/4),50)
                if self.options == []:
                    self.options = [">4"," 3"," 2"," 1"]#1 is best quality
                part1 = longText(self.options[:2])
                part2 = longText(self.options[2:])
                full = dungeons.box(pygame.Surface((part1.rect.width + part2.rect.width + 10,32*2 + 5)).convert())
                full.image.set_colorkey(constants.WHITE)
                full.image.fill(constants.WHITE)
                full.image.blit(part1.image,(0,0))
                part2.rect.right = full.rect.right
                full.image.blit(part2.image,part2.rect)
                lvl.decide = full
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    self.sale.append(self.choice+1)#actual number 1 above choice value
                    self.price = 25*self.sale[1]#costs 25g * the rank
                    self.options = []
                    self.maxChoice = 1
                    self.choice = 0
                    self.finish = False

            elif len(self.sale) == 2 and self.success == None:
                if self.skill == "INVEN":
                    speech = ["Buy the Inventory?","cost: "+str(self.price)+ "g"]
                else:
                    speech = ["Buy the rank " +str(4- self.sale[1] + 1)+' '+ self.sale[0][1:] + '?'
                              ,"cost: " + str(self.price) + "g"]
                lvl.text = longText(speech) #position text one third across screen
                lvl.text.rect.center = (round(lvl.rect.width/3),50)
                if len(self.options) == 0:#only define if list is empty
                    self.options = [">No"," Yes"]
                lvl.decide = longText(self.options)
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    if bool(self.choice):
                        self.pending = True
                    else:
                        self.cancel()
                    self.finish = False
                    self.options = []
                    lvl.decide = None
                    self.choice = 0
                    
    def cancel(self): #reset every value
        self.choice = 0
        self.maxChoice = 1
        self.sale = []
        self.options = []
        self.level.decide = None
        self.level.text = None
        self.talking = False
        self.level.hero.talking = False
        self.buying = False
        self.total = 0
        self.price = 0
        self.skill = None
        self.success = None
        self.finish = False

descriptPot = [
    ['Gives you more energy'],
    ['Makes you so alluring',"enemies can't defend"],
    ['Smells so bad', "enemies won't","want to attack"],
    ['Makes you run faster','to the next toilet']
    ]
class PotionGuy(Merchant):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("sprites/characters/potioner.PNG")
        self.image = pygame.transform.scale2x(self.image)
        self.rect.y = 110 -self.rect.height - 5
        self.rect.x = 200
        self.wares = ['P_HP',
                      'P_ATK',
                      'P_DEF',
                      'P_SPD']
        self.full = None #if a bottle needs to be filled

    def update(self):
        lvl = self.level
        if self.talking:
            #check if finished buying
            if self.success is True:
                speech = ["Would you like to", "buy anything else?"]
                lvl.text = longText(speech) #position text one third across screen
                lvl.text.rect.center = (round(lvl.rect.width/3),50)
                if len(self.options) == 0:#only define if list is empty
                    self.options = [">No"," Yes"]
                lvl.decide = longText(self.options)
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    if not bool(self.choice):#player chose to end
                        self.cancel()
                    else:#otherwise reset variables to start again
                        self.choice = 0
                        self.buying = False
                        self.sale = []
                        self.success = None
                        self.options = []
                        self.finish = False
                    
            elif self.success is False:
                if lvl.hero.gold < self.price:
                    speech = ["Your funds are lacking"]
                else:
                    speech = ["You need more inventory space"]
                lvl.text = longText(speech)
                lvl.text.rect.center = (round(lvl.rect.width/2),50)
                if self.finish:
                    self.cancel()
                    self.finish = False
            #if not yet buying or selling 
            elif self.sale == [] and not self.buying:
                speech = ["Would you like to", "purchase potions or bottles?"]
                lvl.text = longText(speech) #position text one third across screen
                lvl.text.rect.center = (round(lvl.rect.width/3),50)
                if len(self.options) == 0:#only define if list is empty
                    self.options = [">Bottles"," Potions"]
                lvl.decide = longText(self.options)
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    self.buying = bool(self.choice) #0 for potions 1 for bottles
                    lvl.decide = None
                    self.options = []
                    if not self.buying: #buying a bottle
                        self.sale = ['bottle',None]
                        self.price = 30
                        self.maxChoice = 1
                    else:
                        self.maxChoice = 3#prepare for potions
                        self.sale.append('potion')
                        self.price = 10
                    self.choice = 0
                    self.finish = False
                    
            elif len(self.sale) == 1:#find potion to buy
                speech = descriptPot[self.choice]
                lvl.text = longText(speech)
                lvl.text.rect.center = (round(lvl.rect.width/4) + 10,50)
                if self.options == []:
                    self.options = [">Health"," Love"," Stench"," Laxative"] #same order as wares list
                part1 = longText(self.options[:2])
                part2 = longText(self.options[2:])
                full = dungeons.box(pygame.Surface((part1.rect.width + part2.rect.width + 10,32*2 + 5)).convert())
                full.image.set_colorkey(constants.WHITE)
                full.image.fill(constants.WHITE)
                full.image.blit(part1.image,(0,0))
                part2.rect.right = full.rect.right
                full.image.blit(part2.image,part2.rect)
                lvl.decide = full
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    self.sale.append(self.options[self.choice])#get type from options
                    self.skill = self.wares[self.choice]
                    self.options = []
                    lvl.decide = None
                    self.choice = 0
                    self.finish = False
                    self.full = False #need to fill a bottle
                    self.maxChoice = 1
                    self.choice = 0


            elif self.sale[0] == 'bottle':
                speech = ['buy a bottle for 30g?']
                lvl.text = longText(speech) #position text one third across screen
                lvl.text.rect.center = (round(lvl.rect.width/3),50)
                if len(self.options) == 0:#only define if list is empty
                    self.options = [">No"," Yes"]
                lvl.decide = longText(self.options)
                lvl.decide.rect.center = (round(3*lvl.rect.width/4),50)
                if self.finish:
                    if bool(self.choice):
                        self.pending = True
                    else:
                        self.cancel()
                    self.finish = False
                    self.options = []
                    lvl.decide = None
                    self.maxChoice = 1
                    self.choice = 0
            elif self.sale[0] == 'potion':
                speech = ['buy the ' + self.sale[1][1:] + ' potion for 10g?',
                          '(give me a bottle to accept)']
                lvl.text = longText(speech)
                lvl.text.rect.center = (round(lvl.rect.width/2),50)
                #deal with everything else in mainGame
                    
