import pygame,constants,random

class Block(pygame.sprite.Sprite):
    def __init__(self,inventory,source):
        super().__init__()

	    #define level environment
        self.inventory = inventory
        self.centre = None
        self.selected = True
        #tells us if moving between inventories
        self.moving = False
        startPos = constants.mainInvenPos
        self.axle = source[-3]#how to position block
        self.image = source[-2].copy()
        self.colour = source[-1]
        #backup for manipulating the image
        self.tempImage = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.x,self.rect.y = 0,0
        self.rects = []
        self.size = constants.blockSize

        self.skill = None
        self.value = random.randint(1,5)

        self.white = []#stores how close each colour is to white
        for i in self.colour:
            self.white.append(i)

        #define movement
        self.changex = 0
        self.changey = 0
        
        #read in map and centre around one point on the grid
        #all blocks are on 3x4 grid
        for row in range(4):
            for column in range(3):
                if source[row][column] == '@':
                    #make a large rectangle for the centre for reference of other blocks
                    if column == 1 and self.centre == None:
                        Max = row
                        while Max < len(source) - 3:
                            if source[Max][1] == ' ':
                                break
                            Max += 1
                        self.centre = pygame.Rect((column+1)*self.size,0,self.size,self.size*(Max-row))
                        self.rects.append(self.centre)
                        continue
                    elif column == 1:
                        continue
                    #makes a rectangle for each point
                    #rectangles start 1 column over and have to be moved where the inventory is
                    point = pygame.Rect((column+1)*self.size,row*self.size,self.size,self.size)
                    self.rects.append(point)
        #stores corners of rectangles that overlap for rotating
        self.rotateList = []
        for rect in self.rects:
            if rect == self.centre:
                continue
            if rect.top == self.centre.top:
                if rect.right == self.centre.left:
                    self.rotateList.append(['top','left',rect])
                else:
                    self.rotateList.append(['top','right',rect])
            elif rect.right == self.centre.right:
                if rect.bottom == self.centre.top:
                    self.rotateList.append(['right','top',rect])
                else:
                    self.rotateList.append(['right','bottom',rect])
            elif rect.bottom == self.centre.bottom:
                if rect.right == self.centre.left:
                    self.rotateList.append(['bottom','left',rect])
                else:
                    self.rotateList.append(['bottom','right',rect])
            elif rect.left == self.centre.left:
                if rect.bottom == self.centre.top:
                    self.rotateList.append(['left','top',rect])
                else:
                    self.rotateList.append(['left','bottom',rect])
            else:#not on any corner
                self.rotateList.append([None,'right',rect])
                    
        #if not the centre then rotate from the right
        if self.axle == None:
            self.axle = 'right'
            self.rect.topleft = self.centre.topleft
        elif self.axle is True: #align to the centre
            self.rect.midbottom = self.centre.midbottom
            self.axle = 'centre'

        #tells how much to rotate
        self.turned = 0
        
    def update(self):
        
        if not self.selected:
            #drop down if possible with gravity
            self.changey += 1
            self.move(self.changex,self.changey)

        #saves block if moved out of inventory
        if self.inventory.changex == 0:
            if self.rect.bottom > self.inventory.rect.height - self.size:
                #moves block back inside inventory
                diff = self.inventory.rect.height - self.rect.bottom - self.size
                self.moveOverride(0,diff)
                self.changex = 0
            if self.rect.left < self.size:
                diff = self.size - self.rect.left
                self.moveOverride(diff,0)    
            if self.rect.right > self.inventory.rect.width - self.size:
                diff = self.inventory.rect.width - self.rect.right - self.size
                self.moveOverride(diff,0)
            if self.rect.top < 0:
                diff = -self.rect.top
                self.changey = 0
                self.moveOverride(0,diff)

        #updates position in the inventory
        if not self.moving:
           #for debugging
           #pygame.draw.rect(self.inventory.image,constants.GREEN,self.rect)
           for rect in self.rects:
               pygame.draw.rect(self.inventory.image,self.colour,rect) 
           self.inventory.image.blit(self.image,self.rect)

           
        

    def move(self,diffx,diffy):
        #keeps speed of movement
        self.changex = diffx
        self.changey = diffy

        #moving horizontally
        for rect in self.rects:
            rect.move_ip(diffx,0)
        self.rect.move_ip(diffx,0)
        coll,target,hit = self.collDetect()
        if coll:
            #stop movement
            self.changex = 0
            #moving right
            if diffx > 0:
                diff = target.left - hit.right
            #moving left
            else:
                diff = target.right - hit.left
            for rect in self.rects:
                rect.move_ip(diff,0)
            self.rect.move_ip(diff,0)
                
        #moving vertically
        for rect in self.rects:
            rect.move_ip(0,diffy)
        self.rect.move_ip(0,diffy)
        coll,target,hit = self.collDetect()
        if coll:
            self.changey = 0
            self.changex = 0
            #moving down
            if diffy > 0:
                diff = target.top - hit.bottom
            #moving up
            else:
                diff = target.bottom - hit.top
            for rect in self.rects:
                rect.move_ip(0,diff)
            self.rect.move_ip(0,diff)
            
        return True

    #moves block regardless of anything else        
    def moveOverride(self,diffx,diffy):
        for rect in self.rects:
            rect.move_ip(diffx,diffy)
        self.rect.move_ip(diffx,diffy)
    
    #detects if the current position has any collisions after removing it from the level
    def collDetect(self):
        coll = False
        for block in self.rects:
            try:#don't force to stop crashes
                self.inventory.rectlist.remove(block)
            except ValueError:
                pass
            #check if the updated coordinates are already occupied
            if block.collidelist(self.inventory.rectlist) != -1:
                coll = True
                index = block.collidelist(self.inventory.rectlist)
                target = self.inventory.rectlist[index]
                hit = block
            elif block.collidelist(self.inventory.wallList) != -1:
                coll = True
                index = block.collidelist(self.inventory.wallList)
                target = self.inventory.wallList[index]
                hit = block
            self.inventory.rectlist.append(block)
        if coll:
            return True,target,hit
        return False,None,None

    def rotate(self,direction):
        
        #rotating clockwise moves left to right through rotation list
        if direction == 'clock':
            sign = 1
        else:
            sign = -1
        #swaps length and height of centre to rotate    
        newWidth = self.centre.height
        self.centre.height = self.centre.width
        self.centre.width = newWidth

        rotation = ['top','right','bottom','left']       
        for pair in self.rotateList:
            if pair[0] != None:
                order = rotation.index(pair[0])
            else:
                order = 0
            order += (1*sign)   #moves along in the list
            if order == len(rotation):
                order = 0
            if pair[0] != None:
                pair[0] = rotation[order]
            
            order = rotation.index(pair[1]) #repeat for second value
            order += (1*sign)
            if order == len(rotation):
                order = 0
            pair[1] = rotation[order]

            rect = pair[2]
            if pair[0] == 'top':
                rect.top = self.centre.top
            elif pair[0] == 'left':
                rect.left = self.centre.left
            elif pair[0] == 'bottom':
                rect.bottom = self.centre.bottom
            elif pair[0] == 'right':
                rect.right = self.centre.right

            if pair[1] == 'top':
                rect.bottom = self.centre.top
                if pair[0] == None:
                    rect.centerx = self.centre.centerx
            elif pair[1] == 'left':
                rect.right = self.centre.left
                if pair[0] == None:
                    rect.centery = self.centre.centery
            elif pair[1] == 'bottom':
                rect.top = self.centre.bottom
                if pair[0] == None:
                    rect.centerx = self.centre.centerx
            elif pair [1] == 'right':
                rect.left = self.centre.right
                if pair[0] == None:
                    rect.centery = self.centre.centery
            
                
        newWidth = self.rect.height #adjust the image
        self.rect.height = self.rect.width
        self.rect.width = newWidth
        #going clockwise
        if direction == 'clock':
            self.turned += 3
            if self.turned >= 4:
                self.turned -= 4
        else:  #rotate around other direction
            self.turned += 1
            if self.turned >= 4:
                self.turned -= 4
        self.image = pygame.transform.rotate(self.tempImage,90*self.turned)
        #find difference to the centre then move rects to there
        if self.axle == 'centre':
            diffx,diffy = self.rect.center
            diffx -= self.centre.centerx
            diffy -= self.centre.centery
            self.moveOverride(diffx,diffy)
            self.rect.move_ip(-diffx,-diffy)
        else:
            order = rotation.index(self.axle)
            order += (1*sign)
            if order == len(rotation):
                order = 0
            self.axle = rotation[order]
            if self.axle == 'left':
                diffx,diffy = self.rect.center
                diffx -= self.centre.left
                diffy -= self.centre.centery
                self.moveOverride(diffx,diffy)
                self.rect.move_ip(-diffx,-diffy)
            elif self.axle == 'top':
                diffx,diffy = self.rect.center
                diffy -= self.centre.top
                diffx -= self.centre.centerx
                self.moveOverride(diffx,diffy)
                self.rect.move_ip(-diffx,-diffy)
            elif self.axle == 'bottom':
                diffx,diffy = self.rect.center
                diffy -= self.centre.bottom
                diffx -= self.centre.centerx
                self.moveOverride(diffx,diffy)
                self.rect.move_ip(-diffx,-diffy)
            else:
                diffx,diffy = self.rect.center
                diffx -= self.centre.right
                diffy -= self.centre.centery
                self.moveOverride(diffx,diffy)
                self.rect.move_ip(-diffx,-diffy)

    #brightens the block depending on the scale
    #bright tells if it becomes brighter or darker
    def coloured(self,bright,scale):
        newC = tuple()
        if bright:
            for i in self.colour:
                tone = i + scale
                if tone > 255:
                    tone = 255
                newC += (tone,)

        else:
            for i in self.colour:
                if i != 255:#only do things differently if it is white
                    tone = i - scale

                else:
                    tone = self.white[self.colour.index(i)]
                newC += (tone,) # add tuples together
        self.colour = newC

class Equipment(Block):
    def __init__(self,rank,skill,source,inventory):
        super().__init__(inventory,source)
        self.rank = rank
        self.skill = skill
        self.value *= 3
        if self.skill == "DEF":
            self.image = pygame.image.load("sprites/items/shield.png").convert_alpha()
        elif self.skill == "ATK":
            self.image = pygame.image.load("sprites/items/sword.png").convert_alpha()
        elif self.skill == "SPD":
            self.image = pygame.image.load("sprites/items/wings.png").convert_alpha()
        star = pygame.image.load("sprites/items/star.png").convert_alpha()
        for i in range(rank -1,0,-1): #add on stars to display rank
            posRect = pygame.Rect((i-1)*5,self.rect.bottom - 20,20,20)
            self.image.blit(star,posRect)
        self.tempImage = self.image.copy()

class Potion(Block):
    def __init__(self,inventory):
        super().__init__(inventory,constants.block2)
        self.skill = 'empty'
        self.value*= 2
        self.image = pygame.image.load("sprites/Potions/empty.png")
        self.tempImage = self.image.copy()
