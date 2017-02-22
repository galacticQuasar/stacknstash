import pygame,constants

class Inventory(pygame.sprite.Sprite):
    
    def __init__(self,source):
        super().__init__()
        
        size = constants.blockSize
        startPos = constants.mainInvenPos
        self.image = source[-1].convert_alpha()
        self.background = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = startPos
        #list of the rectangles inside the inventory
        self.rectlist = []
        self.wallList = []
        #list of other objects in Inventory that need to be updated
        self.updatelist = pygame.sprite.Group()

        #tells which direction we are changing
        self.changex = 0
        self.changey = 0
        #constants needed for shrinking and growing inventory
        repeat = (8*constants.blockSize)/10
        #only repeats shrinking until block is at certain position
        self.shiftL = round(((self.rect.width/3 + 10))/repeat)
        self.shiftR = round((self.rect.width +10)/repeat)
        #for slightly adjusting the blocks
        self.miniShift = round((size/repeat)*(2/3))
        self.vertShift = round((5*constants.blockSize)/repeat)
        self.counter = 0
        #surfaces for moving the main surface
        self.changeSurface = self.image.copy()

        #define limits of inventory with 5 pixel line
        self.boundaries = pygame.Rect(constants.blockSize -5,-5,10*constants.blockSize+10,11*constants.blockSize+10)
        
        #iterate through inventory to include walls
        for row in range(len(source)-1):
            for column in range(len(source[row])):
                if source[row][column] == '*':
                    wall = pygame.Rect(column*size,(row+1)*size,size,size)
                    self.wallList.append(wall)         
    def update(self):
        if self.changex != 0:
            if self.changey == -1:
                self.shrink()
            elif self.changey == 1:
                self.grow()
        #moving up/down
        elif  self.changex == 0 and self.changey != 0:
            self.vertical()

        #reset image to original size for accurate positioning of blocks
        self.image = pygame.transform.scale(self.image,(self.background.get_width(),self.background.get_height()))
        self.rect.width,self.rect.height = self.image.get_width(),self.image.get_height()
        self.image.fill(constants.SKY_BLUE)
        self.image.blit(self.background,(0,-10))

        
        pygame.draw.rect(self.image,constants.DEEP_RED,self.boundaries,5)
        #update blocks
        self.updatelist.update()
        self.image = pygame.transform.scale(self.image,self.changeSurface.get_size())
        self.rect.width,self.rect.height = self.image.get_width(),self.image.get_height()


    def add(self,newBlock):
        #add all necessary details for a new block
        for rect in newBlock.rects:
            self.rectlist.append(rect)
        self.updatelist.add(newBlock)

    def remove(self,oldBlock):
        for rect in oldBlock.rects:
            try:#don't force to stop crashes
                self.rectlist.remove(rect)
            except ValueError:
                pass

        self.updatelist.remove(oldBlock)

    def empty(self):
        for block in self.updatelist:
            block.kill()#remove block entirely
        self.rectlist = []

    def shrink(self):
        #shift slightly down
        self.rect.y += self.miniShift
        #if we haven't reached the left side of the screen
        if self.rect.right > constants.mainInvenPos[0] - 10 and self.changex < 0:
            self.changeSurface = pygame.transform.scale(self.changeSurface,(self.rect.width - 10,self.rect.height - 10))
            self.rect.x -= self.shiftL
        #or if we haven't reached the right side of the screen
        elif self.rect.left < constants.mainInvenPos[0] + self.background.get_width() +10 and self.changex > 0:
            self.changeSurface = pygame.transform.scale(self.changeSurface,(self.rect.width - 10,self.rect.height - 10))
            self.rect.x += self.shiftR
        else:   #stop moving
            self.changex = 0
            self.changey += 1

    def grow(self):
        #shift slightly up
        self.rect.y -= self.miniShift
        #moving right
        if self.rect.left != constants.mainInvenPos[0] and self.changex > 0:
            self.changeSurface = pygame.transform.scale(self.changeSurface,(self.rect.width + 10,self.rect.height + 10))
            self.rect.x += self.shiftL
        #moving left
        elif self.rect.left != constants.mainInvenPos[0] and self.changex < 0:
            self.changeSurface = pygame.transform.scale(self.changeSurface,(self.rect.width + 10,self.rect.height + 10))
            self.rect.x -= self.shiftR
        else:   #stop moving
            self.changey -= 1
            self.changex = 0

    def vertical(self):
        self.counter += 1
        if self.changey > 0:
            self.rect.y += self.vertShift
        else:
            self.rect.y -= self.vertShift
        #Checks if repeated enough times
        if self.counter >= (5*constants.blockSize/self.vertShift):
            self.changey = 0
            self.counter = 0

#stores blocks that aren't in any inventory
#subclass of inventory to make more compatible with blocks
class Hold(Inventory):
    def __init__(self,source):
        super().__init__(source)
        self.image = pygame.Surface((constants.blockSize*11 + 200,constants.blockSize*2))
        self.rect = self.image.get_rect()
        #aligns hold with currently selected inventory
        self.rect.x = constants.mainInvenPos[0] - 100
        self.rect.y = constants.mainInvenPos[1] - self.rect.height - 50
        
        #highest no of displayable blocks across one line
        self.max  = 9
        self.blockList = []

    def update(self):
        size = constants.blockSize
        self.image.fill(constants.WHITE)
        self.image = pygame.transform.scale(self.image,(size*18 + 400,size*4))
        for i in range(self.max):
            #stop if the count goes over the list length
            if i >= len(self.blockList):
                break
            point = self.blockList[i].rect.center
            #moves blocks into place with some space between blocks
            if point != ( 1.5*size + (3*size +15)*i,self.rect.height):
                diffx = 1.5*size + (3*size +15)*i - point[0]
                diffy = self.rect.height - point[1]
                self.blockList[i].moveOverride(diffx,diffy)
            for rect in self.blockList[i].rects:
                pygame.draw.rect(self.image,self.blockList[i].colour,rect)
            self.image.blit(self.blockList[i].image,self.blockList[i].rect)
        self.image = pygame.transform.scale(self.image,(size*9+200,size*2))

    def add(self,newBlock):
        for block in newBlock.rects:
            self.rectlist.append(block)
        self.blockList.append(newBlock)
                    
