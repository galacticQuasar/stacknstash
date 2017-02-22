import pygame,random
from pygame.locals import *
import constants,blocks,inventory,dungeons,characters,towns,menu

def main():
    pygame.init()

    DISPLAYSURF = pygame.display.set_mode([constants.SCREEN_WIDTH,constants.SCREEN_HEIGHT])
    pygame.display.set_caption("Stack n' Stash")

    #stores the different inventories that can be used in the game
    invenList = []
    invenList.append(inventory.Inventory(constants.inven1))
    #keeps track of the current inventory
    currentInvenNo = 0
    currentInven = invenList[currentInvenNo]

    #stores inventory sprites to be updated
    spriteList = pygame.sprite.LayeredUpdates()
    spriteList.add(currentInven)
    #leave the current inventory on top
    spriteList.change_layer(currentInven,1)

    size = constants.blockSize
    #tells if something is blocking spawning
    spawnRect1 = pygame.Rect(size,0,size*4,size*4)
    spawnRect2 = pygame.Rect(currentInven.rect.width -size*5,0,size*4,size*4)
    hold = inventory.Hold(constants.inven1)
    spriteList.add(hold)
    pause = False #way to pause the game
    

    equips = {#match skill with block type
        "ATK" : constants.block4,
        "DEF" : constants.block2,
        "SPD" : constants.block5}
    potion = {#images for potions
        "P_HP" : pygame.image.load('sprites/potions/red.png'),
        "P_ATK" : pygame.image.load('sprites/potions/Purple.png'),
        "P_DEF" : pygame.image.load('sprites/potions/Green.png'),
        "P_SPD" : pygame.image.load('sprites/potions/Yellow.png')
        }

    #potion information
    pPos = (constants.mainDunPos[0],constants.mainDunPos[1] + 110)
    pTime = 30 #length potions work in seconds
    #bars for how long potion will work
    aBar = pygame.Rect(pPos[0],pPos[1],100,15)
    dBar = pygame.Rect(pPos[0],pPos[1] + 15,100,15)
    sBar = pygame.Rect(pPos[0],pPos[1] + 30,100,15)
    
    #time left for potion at end
    active = {#what potion is working and other info
        "P_ATK" : [False,aBar,0],
        "P_DEF" : [False,dBar,0],
        "P_SPD" : [False,sBar,0]
        }

    #caps frame rate
    clock = pygame.time.Clock()
    done = False

    debug = False

    #sounds
    door = pygame.mixer.Sound('music/effects/door.ogg')
    equip = pygame.mixer.Sound('music/effects/equip.ogg')
    bottle = pygame.mixer.Sound('music/effects/uncork.ogg')

    currentBlock = None
    movement = (0,0)
    #information for dungeoneering
    dungeon = True
    cleared = 0
    hero = characters.Hero()
    merchant = towns.Merchant()
    potioner = towns.PotionGuy()
    level = dungeons.Level(cleared,hero,hold)
    timeLeft = 0

    font = pygame.font.SysFont('ARIAL', 30)
    towns.font = font #set the font for towns

    #run menu
    altMode,done = menu.Menu(DISPLAYSURF,clock,font)
    constants.multi = altMode #referencing the bonus mode

    if altMode:
        hero.changex = 0
        hero.multi = True
        timeLeft = 50*1000 + pygame.time.get_ticks()#give 50 seconds for first level

    pygame.mixer.music.load(dungeons.levelMusic[0])
    pygame.mixer.music.play(-1)
    while not done:
        #block spawning
        #if nothing is taking up either spawning space
        if spawnRect1.collidelist(currentInven.rectlist) == -1 and currentInven.changex == 0:
            if len(hold.blockList) > 0:
                newBlock = hold.blockList.pop(0)
                currentInven.add(newBlock)
                newBlock.inventory = currentInven
                diffx = size + 20 - newBlock.rect.x #move the block to left of the inventory
                diffy = -newBlock.rect.y
                newBlock.move(diffx,diffy)
                newBlock.changex,newBlock.changey = 0,0
        elif spawnRect2.collidelist(currentInven.rectlist) == -1 and currentInven.changex == 0:
            if len(hold.blockList) > 0:
                newBlock = hold.blockList.pop(0)
                currentInven.add(newBlock)
                newBlock.inventory = currentInven
                #move to the right
                diffx = currentInven.rect.width- size - 20 - newBlock.rect.right
                diffy = -newBlock.rect.y
                newBlock.move(diffx,diffy)
                newBlock.changex,newBlock.changey = 0,0

        #dungeon/city management
        #advance level once player has reached end
        if hero.rect.right  >= level.rect.width - 20:
            dungeon = not dungeon # flip dungeon boolean
            if not dungeon:
                #remove penalty
                for i in hero.stats:
                    if i != "MAX_HP":
                        hero.stats[i] += level.penalty
                level = towns.Town(cleared,hero,merchant,potioner)
                merchant.level = level#assign the level to merchant
                potioner.level = level
                merchant.rect.x = 200
                potioner.rect.x = 300
                
                hero.rect.x = 10
                hero.changex = 0
                hero.image.fill(constants.BLACK)
                hero.image.blit(hero.spriteSheet,(0,0),(12,712,44,58))
                hero.width = 12
                hold.blockList.clear()
                door.play() #exited dungeon so open door
                
            else:#make new dungeon
                cleared += 1
                level = dungeons.Level(cleared,hero,hold)
                hero.rect.x = 10
                hero.changex = hero.speed
                #reset time for next level adding 2 sec for every level cleared
                timeLeft = (50 + 2*cleared)*1000 + pygame.time.get_ticks()
        elif hero.rect.x < 0:#don'tlet hero walk off screen
            hero.rect.x = 0

        #event management
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
                
            elif event.type == MOUSEBUTTONDOWN and not hero.dead:
                #adjusts mouse position in relation to the inventory
                point = (pygame.mouse.get_pos()[0] - constants.mainInvenPos[0],pygame.mouse.get_pos()[1] - constants.mainInvenPos[1])
                for block in currentInven.rectlist:
                    #check if the mouse is clicked on a rectangle
                    if block.collidepoint(point):
                        for sprite in currentInven.updatelist:
                            if block in sprite.rects:
                                currentBlock = sprite
                                currentBlock.selected = True
                                currentBlock.coloured(True,40)
                                movement = pygame.mouse.get_pos()
                                break
                        break

            elif event.type == MOUSEBUTTONUP: #unselect if mouse unclicked
                if currentBlock != None:
                    currentBlock.selected = False
                    currentBlock.coloured(False,40)
                    if currentBlock.moving:
                        currentBlock.moving = False
                        currentBlock.inventory.add(currentBlock)
                        coll = currentBlock.collDetect()[0]
                        if coll:
                            currentBlock.inventory.remove(currentBlock)
                            currentBlock.inventory = hold
                            hold.add(currentBlock)

                    currentBlock = None

            elif event.type == MOUSEMOTION and not hero.dead:
                if currentBlock != None:
                    moveChange = pygame.mouse.get_pos()
                    #gets the change in mouse position to tell where the block moves
                    changex = moveChange[0] - movement[0]
                    changey = moveChange[1] - movement[1]
                    #limits speed of block movement
                    if changex > 30:
                        changex = 30
                    elif changex < -30:
                        changex = -30
                    if changey > 30:
                        changey = 30
                    elif changey < -30:
                        changey = -30
                    #ignore other blocks if moving btwn inventories
                    if currentBlock.moving:
                        currentBlock.moveOverride(changex,changey)
                    else:
                        currentBlock.move(changex,changey)
                    movement = moveChange
                    
            
            elif event.type == KEYDOWN:
                #if we press Q or W then rotate the block
                if event.key == K_q:
                    if currentBlock != None:
                        currentBlock.rotate('anti')
                        #reverses movement if blocked
                        if not currentBlock.moving:
                            if currentBlock.collDetect()[0]:
                                currentBlock.rotate('clock')
                elif event.key == K_w:
                    if currentBlock != None:
                        currentBlock.rotate('clock')
                        if not currentBlock.moving:
                            if currentBlock.collDetect()[0]:
                                currentBlock.rotate('anti')
                            
                if event.key == K_a and not hero.dead:  #move inventory left
                    #if the list isn't already the last in the list
                    if currentInvenNo != len(invenList)-1 and currentInven.changex == 0:
                        #affect everything left of current inventory
                        for inven in invenList[:currentInvenNo]:
                            inven.changey = 1
                        currentInven.changex = -1
                        currentInven.changey = -1
                        currentInvenNo += 1
                        currentInven = invenList[currentInvenNo]
                        #affect everything right of current inventory
                        for inven in invenList[currentInvenNo:]:
                            inven.changey = -1
                        currentInven.changex = -1
                        currentInven.changey = 1
                        currentBlock = replace(currentBlock,currentInven,hold)
                elif event.key == K_s and not hero.dead:  #move inventory right
                    if currentInvenNo != 0 and currentInven.changex == 0:
                        for inven in invenList[currentInvenNo:]:
                            inven.changey = 1
                            inven.changex = 0
                        currentInven.changex = 1
                        currentInven.changey = -1
                        currentInvenNo -= 1
                        currentInven = invenList[currentInvenNo]
                        for inven in invenList[:currentInvenNo]:
                            inven.changey = -1
                        currentInven.changex = 1
                        currentInven.changey = 1
                        currentBlock = replace(currentBlock,currentInven,hold)

                elif event.key == K_e: #equip item
                    if currentBlock != None:
                        if currentBlock.rect.y < constants.blockSize and currentBlock.skill in ['ATK',"DEF",'SPD']: #if item is equippable
                            currentBlock.coloured(False,40) #darken
                            equip.play() #play equip sound
                            if hero.armour[currentBlock.skill] == None:
                                hero.armour[currentBlock.skill] = currentBlock #equip selected item and add bonus
                                hero.stats[currentBlock.skill] += 2 * currentBlock.rank
                                if currentBlock.skill == "SPD": #improve walking speed with speed boost
                                    hero.speed += currentBlock.rank/3
                                currentInven.remove(currentBlock)
                                currentBlock = None
                            else: #otherwise unequip current equipment
                                tempBlock = hero.armour[currentBlock.skill]
                                hero.armour[currentBlock.skill] = currentBlock #equip selected item and add bonus
                                hero.stats[currentBlock.skill] += 2 * currentBlock.rank
                                if currentBlock.skill == "SPD":
                                    hero.speed += currentBlock.rank/3
                                currentInven.remove(currentBlock)
                                #reposition new block in the position of the old block
                                diffx,diffy = currentBlock.rect.x,currentBlock.rect.y
                                diffx -= tempBlock.rect.x
                                diffy -= tempBlock.rect.y
                                currentInven.add(tempBlock)
                                tempBlock.move(diffx,diffy)
                                while tempBlock.turned != currentBlock.turned: #rotate to match new block
                                    if tempBlock.turned < currentBlock.turned:
                                        tempBlock.rotate('anti')
                                    elif tempBlock.turned > currentBlock.turned:
                                        tempBlock.rotate('clock')
                                currentBlock = tempBlock
                                hero.stats[currentBlock.skill] -= 2*currentBlock.rank
                                if currentBlock.skill == "SPD":
                                    hero.speed -= currentBlock.rank/3
                                currentBlock = None
                elif event.key == K_t:#trading
                    if currentBlock != None:
                        if currentBlock.rect.y < constants.blockSize:
                            if merchant.sale == None:
                                merchant.total += currentBlock.value
                                currentBlock.kill()
                                currentInven.remove(currentBlock)
                                currentBlock = None
                elif event.key == K_g:
                    if merchant.sale == None:
                        currentBlock == None #deselect block
                        for block in currentInven.updatelist:
                            merchant.total += block.value
                            block.kill()
                            currentInven.remove(block)
                        currentInven.rectlist = []
                            
                                
                elif event.key == K_DELETE:#delete block
                    if currentBlock != None:
                        currentBlock.kill()
                        currentInven.remove(currentBlock)
                        currentBlock = None

                elif event.key == K_r:#filling/using potions
                    if currentBlock != None:
                        if currentBlock.rect.y < constants.blockSize:
                            #if buying a potion and bottle is empty
                            if not potioner.full and currentBlock.skill == 'empty' and potioner.skill != None:
                                potioner.finish = False #don't immediately skip next line
                                if hero.gold < 10: #not enough money
                                    potioner.full = True
                                    potioner.success = False
                                else:
                                    hero.gold -= 10
                                    currentBlock.image = potion[potioner.skill]
                                    currentBlock.tempImage = currentBlock.image.copy()
                                    currentBlock.skill = potioner.skill
                                    potioner.full = True
                                    potioner.success = True
                            #trigger effect of potion
                            elif currentBlock.skill == 'P_HP' and dungeon:
                                bottle.play()
                                hero.currentHP += 15 #heal 15 hp
                                if hero.currentHP > hero.stats['MAX_HP']:
                                    hero.currentHP = hero.stats['MAX_HP']
                                currentBlock.skill = 'empty'
                                currentBlock.image = pygame.image.load("sprites/Potions/empty.png")
                                currentBlock.tempImage = currentBlock.image.copy()
                            elif currentBlock.skill in ['P_ATK','P_DEF','P_SPD'] and dungeon:
                                bottle.play()
                                effect = currentBlock.skill
                                if not active[effect][0]: #if potion not active
                                    active[effect][0] = True
                                    #set timer for 20 seconds
                                    active[effect][-1] = pygame.time.get_ticks() + pTime *1000
                                    ability = effect[2:] #cut string for effect
                                    hero.stats[ability] += 6 #give bonus to player
                                    active[effect][1].width = 100
                                currentBlock.image = pygame.image.load("sprites/Potions/empty.png")
                                currentBlock.tempImage = currentBlock.image.copy()
                                currentBlock.skill = 'empty'
                                
                
                elif event.key == K_z:#talking
                    if not dungeon:
                        if abs(hero.rect.centerx - level.sign.rect.centerx) < 30 and not hero.talking:
                            hero.startTalk()
                            level.talking = "sign"
                        elif merchant.talking:
                            merchant.finish = True #tell merchant decision is made
                        elif potioner.talking:
                            potioner.finish = True
                        elif hero.talking:#move to next line of words
                            level.speechPos += 1
                        for seller in [merchant,potioner]:
                            if abs(hero.rect.centerx - seller.rect.centerx) < 30 and not hero.talking:
                                hero.startTalk()
                                seller.talking = True

                    if hero.dead: #reset the game
                        cleared = 0
                        for inven in invenList:
                            inven.kill()#remove every inventory
                        invenList = [currentInven]
                        currentInven.empty()
                        merchant.invenNo = 1 #reset how many inventories player has bought
                        spriteList.add(currentInven)
                        spriteList.change_layer(currentInven,1)
                        currentInvenNo = 0
                        hold.blockList.clear()

                        for i in ['P_ATK','P_DEF','P_SPD']:
                            if active[i][0]:#reset active potions
                                active[i][0] = False
                                active[i][-1] = 0
                                ability = i[2:]
                                hero.stats[ability] -= 5#remove bonus
                        #run menu
                        altMode,done = menu.Menu(DISPLAYSURF,clock,font)
                        constants.multi = altMode #referencing the bonus mode
                        
                        hero = characters.Hero()#make a new hero
                        level = dungeons.Level(cleared,hero,hold)#make new level

                        towns.font = font#reset text size

                        if altMode:#reset time for altMode
                            hero.changex = 0
                            timeLeft = 50*1000 + pygame.time.get_ticks()
                            
                elif event.key == K_x and not dungeon:
                    if merchant.talking:
                        merchant.cancel()
                    elif potioner.talking:
                        potioner.cancel()
                        potioner.full = True
                    if hero.talking: # cancel the hero talking
                        hero.talking = False
                        level.talking = None
                        level.speechPos = 0
                        level.text = None

                elif event.key == K_SPACE and not hero.attack and hero.fighting and altMode:#if able to attack
                    hero.attack = True
                    hero.fight()

                elif event.key == K_p:
                    pause = not pause
                    if pause: #pausing the game
                        if altMode: #store time left
                            timeDiff = timeLeft - pygame.time.get_ticks()
                        potionDiff = []
                        for i in ['P_ATK','P_DEF','P_SPD']:
                            if active[i][0]: #store the time left for the potion
                                potionDiff.append(active[i][-1] - pygame.time.get_ticks())
                            else:
                                potionDiff.append(0)
                    elif not pause: #unpausing
                        if altMode:
                            timeLeft = pygame.time.get_ticks() + timeDiff
                        for i in ['P_ATK','P_DEF','P_SPD']:
                            if active[i][0]:
                                pos = ['P_ATK','P_DEF','P_SPD'].index(i)
                                #reference the time difference in the same order as list
                                active[i][-1] = pygame.time.get_ticks() + potionDiff[pos]

                elif event.key == K_BACKQUOTE:
                    debug = not debug
                                
                #moving left and right
                move = (not hero.talking and (not dungeon or altMode))#can hero move
                if event.key == K_RIGHT and move:#works if playing alternate mode
                    hero.changex = hero.speed 
                elif event.key == K_LEFT and move:
                    hero.changex = -hero.speed

                for seller in [merchant,potioner]:#check both salesmen
                    if event.key == K_DOWN:
                        if seller.talking and seller.maxChoice > 0: #move where the arrow is
                            #replace arrow with blank space
                            seller.options[seller.choice] = seller.options[seller.choice].replace('>',' ')
                            if seller.choice < seller.maxChoice:
                                seller.choice += 1
                            else:#reset to start
                                seller.choice = 0
                            seller.options[seller.choice] = seller.options[seller.choice].replace(' ','>')
                                
                    elif event.key == K_UP:
                        if seller.talking and seller.maxChoice > 0:
                            seller.options[seller.choice] = seller.options[seller.choice].replace('>',' ')
                            if seller.choice > 0:
                                seller.choice -= 1
                            else:#reset to start
                                seller.choice = len(seller.options) - 1
                            seller.options[seller.choice] = seller.options[seller.choice].replace(' ','>')
                            
                    elif event.key == K_RIGHT and seller.talking and seller.maxChoice > 2:
                        seller.options[seller.choice] = seller.options[seller.choice].replace('>',' ')
                        if seller.choice < seller.maxChoice - 1: 
                            seller.choice += 2
                        else:
                            seller.choice -= 2
                        seller.options[seller.choice] = seller.options[seller.choice].replace(' ','>')

                    elif event.key == K_LEFT and seller.talking and seller.maxChoice > 2:
                        seller.options[seller.choice] = seller.options[seller.choice].replace('>',' ')
                        if seller.choice > seller.maxChoice - 2:
                            seller.choice -= 2
                        else:
                            seller.choice += 2
                        seller.options[seller.choice] = seller.options[seller.choice].replace(' ','>')         

            if event.type == KEYUP:
                #conditions for being able to stop walking
                move = ((not dungeon or altMode) and not (hero.fighting or hero.talking))
                if event.key == K_RIGHT  and move:
                    hero.changex = 0
                    hero.image.fill(constants.BLACK)
                    hero.image.blit(hero.spriteSheet,(0,0),(12,712,44,58))
                    hero.width = 12
                elif event.key == K_LEFT and move:  
                    hero.changex = 0
                    hero.image.fill(constants.BLACK)
                    hero.image.blit(hero.spriteSheet,(0,0),(12,712,44,58))
                    hero.width = 12 #if hero was moving left keep them facing left
                    hero.image = pygame.transform.flip(hero.image,True,False)

        #merchant deals
        if merchant.pending:
            if hero.gold < merchant.price: # can't afford
                merchant.success = False
                merchant.pending = False
                
            elif spawnRect1.collidelist(currentInven.rectlist) != -1 and merchant.skill != "INVEN": #if enough space
                if spawnRect2.collidelist(currentInven.rectlist) != -1:
                    merchant.success = False
                    merchant.maxChoice = 0
                else:#space with second rect
                    merchant.success = True
                    bought = blocks.Equipment(merchant.sale[1],merchant.skill,equips[merchant.skill],currentInven)
                    currentInven.add(bought)
                    diffx = currentInven.rect.width- size - 20 - bought.rect.right
                    diffy = -bought.rect.y
                    bought.moveOverride(diffx,diffy)
                    hero.gold -= merchant.price
                    
            elif merchant.skill != "INVEN": #space with first rect
                merchant.success = True
                bought = blocks.Equipment(merchant.sale[1],merchant.skill,equips[merchant.skill],currentInven)
                currentInven.add(bought)
                diffx = size + 20 - bought.rect.x
                diffy = -bought.rect.y
                bought.moveOverride(diffx,diffy)
                hero.gold -= merchant.price
                
            elif merchant.skill == "INVEN": #adding inventories
                merchant.success = True
                hero.gold -= merchant.price
                newInven = inventory.Inventory(constants.inven1)
                merchant.invenNo += 1#add 1 to no of bought inventories
                for i in invenList[currentInvenNo + 1:]:#move everything right of inventory
                    i.changey = 1
                invenList.insert(currentInvenNo + 1,newInven)#insert 1 left of current inven
                newInven.changex = 1
                newInven.changey = -1
                spriteList.add(newInven)
            merchant.pending = False #not pending anymore
            
        elif potioner.pending:
            if hero.gold < potioner.price:
                potioner.success = False
                potioner.pending = False
            elif spawnRect1.collidelist(currentInven.rectlist) != -1:
                if spawnRect2.collidelist(currentInven.rectlist) != -1:
                    potioner.success = False
                    potioner.maxChoice = 0
                else: #space with second rect
                    potioner.success = True
                    bought = blocks.Potion(currentInven)
                    currentInven.add(bought)
                    diffx = currentInven.rect.width- size - 20 - bought.rect.right
                    diffy = -bought.rect.y
                    bought.moveOverride(diffx,diffy)
                    hero.gold -= potioner.price
            else: #space with first rect
                potioner.success = True
                bought = blocks.Potion(currentInven)
                currentInven.add(bought)
                diffx = size + 20 - bought.rect.x
                diffy = -bought.rect.y
                bought.moveOverride(diffx,diffy)
                hero.gold -= potioner.price
            potioner.pending = False

        #potion countdown
        for i in ['P_ATK','P_DEF','P_SPD']:
            if active[i][0]:#potion active
                if active[i][-1] < pygame.time.get_ticks():#time is up
                    active[i][0] = False
                    ability = i[2:]
                    hero.stats[ability] -= 5#remove bonus
                    continue
                active[i][1].width = (active[i][-1] - pygame.time.get_ticks())/(pTime*10)#make start 100 pixels

        #check if died
        if hero.currentHP <= 0 and not hero.dead:
            topCleared,topGold = newScores(cleared, hero.gold)#update high scores
            score = towns.longText(["GAME OVER",#give game score(measured in money and level raeched)
                                    "",
                                    "Money: "+ str(hero.gold)+ "  Richest: " + topGold,
                                    "Dungeons cleared: " + str(cleared) + "  Furthest: " + topCleared,
                                    "press Z to restart the game"])
            score.rect.center = (constants.SCREEN_WIDTH/2,constants.SCREEN_HEIGHT/2)
            #score.image.set_colorkey(constants.WHITE)
            hero.dead = True
            hero.changex = 0
            hero.diffx = 0
            hero.width = 12
            hero.rect.y = hero.basey
            if not altMode:
                hero.target.fighting = False
            else:
                timeLeft = 0 #remove clock

        if altMode and dungeon and timeLeft > pygame.time.get_ticks():#if time left and bonus mode
            #convert to seconds and make an image
            time = font.render(str(round((timeLeft-pygame.time.get_ticks())/1000,2)),False,constants.WHITE)

        elif altMode and dungeon:#otherwise kill the player
            hero.currentHP = 0
                                                
        if not pause:
            #update things
            spriteList.update()

            #output
            DISPLAYSURF.fill(constants.SKY_BLUE)
            # put inventory onto screen
            spriteList.draw(DISPLAYSURF)
            #separately draw selected rect onto screen
            if currentBlock != None:
                if currentBlock.moving:
                    currentBlock.update()
                    for rect in currentBlock.rects:
                        moveRect = rect.move(constants.mainInvenPos)
                        pygame.draw.rect(DISPLAYSURF,currentBlock.colour,moveRect)
                    moveRect = currentBlock.rect.move(constants.mainInvenPos)
                    DISPLAYSURF.blit(currentBlock.image,moveRect)
            if active['P_ATK'][0]:#draw bars for potions
                pygame.draw.rect(DISPLAYSURF,constants.PURPLE,active['P_ATK'][1])
            if active['P_DEF'][0]:
                pygame.draw.rect(DISPLAYSURF,constants.GREEN,active['P_DEF'][1])
            if active['P_SPD'][0]:
                pygame.draw.rect(DISPLAYSURF,constants.YELLOW,active['P_SPD'][1])
            
                
            level.update()
            DISPLAYSURF.blit(level.image,level.rect)
            if timeLeft > pygame.time.get_ticks() and dungeon and altMode:
                #display time in top right corner
                DISPLAYSURF.blit(time,(constants.mainDunPos[0] + 530 - 80,constants.mainDunPos[1]))
            if hero.dead: #hero died
                DISPLAYSURF.blit(score.image,score.rect)

            if debug:#do anything for debugging
                hero.gold += 10
                hero.currentHP += 10
                debug = False

            pygame.display.flip()
            clock.tick(60)
            pygame.display.update()
    pygame.quit()

def replace(currentBlock,currentInven,hold):
    if currentBlock != None:
        #if the block is at the top of the inventory
        if currentBlock.centre.top < constants.blockSize and not currentBlock.moving:
            currentBlock.moving = True
            #remove block from old inventory
            currentBlock.inventory.remove(currentBlock)
        if currentBlock.moving:
                currentBlock.inventory = currentInven
        else:
            currentBlock.selected = False
            currentBlock.coloured(False,40)
            currentBlock = None
    return currentBlock

def newScores(newLevel,newGold):
    file = open('sprites/highScore.txt','r')
    oldScore = file.read(6)#get first 6 numbers
    file.close()
    
    if newGold > 999:#don't keep any record with over 999 gold (filthy hackers)
        newGold = 999
    if newLevel > int(oldScore[:3]):#check first three numbers
        oldScore = str(newLevel).zfill(3) + oldScore[3:] #zfill fills with zeros up to 3
    if newGold > int(oldScore[3:]):
        oldScore = oldScore[:3] + str(newGold).zfill(3)
        
    file = open('sprites/highScore.txt','w')
    file.write(oldScore)
    file.close()
    return oldScore[:3],oldScore[3:]
    
    
    
if __name__ == "__main__":
	main()



