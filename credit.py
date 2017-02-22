import pygame
from pygame.locals import *
import constants,blocks,inventory,towns
'''list of order blocks to be dropped
    first no is pos in constants,blockList,then how much to rotate
    and the coordinates it ends up in the inventory'''
blockOrder =[
    [3,3,(0,9)], [2,0,(3,9)], [4,1,(5,10)],
    [6,0,(0,8)], [7,3,(5,8)], [4,1,(2,8)],
    [1,1,(8,8)], [7,0,(0,5)], [5,2,(8,6)],
    [3,1,(4,7)], [7,1,(3,6)], [6,1,(8,4)],
    [1,1,(1,5)], [5,2,(6,5)], [2,0,(5,4)],
    [1,0,(7,3)], [5,3,(2,4)], [3,3,(0,3)],
    [2,0,(5,2)], [1,1,(3,2)], [7,1,(7,2)],
    [4,1,(6,1)], [2,0,(1,2)], [5,1,(3,1)],
    [7,1,(0,1)]]

creditPages = [#strings of the lines for credits(max 8 lines)
    ['Lead Program design', 'Aaron Maynard',
     '',
     'Signpost', 'as itself',
     '',
     'Quasi-client', 'Abdullah Mohammad'],
    ['All third party music', 'and graphics supplied',
     'from OpenGameArt.org',
     '',
     'Music',
     '',
     '1st Dungeon', 'Gran Batalla','-xXUnderTowerXx'],
    ['2nd Dungeon, credits','and Main Menu', 'Hold The Line, Airship Song',
     'and Little Town - Bart K',
     '',
     '3rd Dungeon','Dragon King Dungeon','-TKZ Productions'],
    ['Town Theme','Little People at Work','-Horror Pen',
     '',
     'Sound Effects','Artisticdude'],
    ['Graphics',
     '',
     'Monsters and Items', 'David E. Gervais',
     '',
     'Backgrounds', 'Trent Gamblin'],
    ['Potions', 'sunburn',
     '',
     'Door', 'sujit1717',
     '',
     'Wings','nazzyc'],
    ['Sign','nemisys',
     '',
     'Testers',
     'Chuckstah',
    'And also a special thanks',
     'to the person on the other',
     'side of this screen']]



def makeBlock(info,inventory,source):
    '''compile the info from the blockOrder into a block
    and change the image with the source'''
    blockType = constants.blockList[(info[0]-1)] #list start at 0 so decrease value by 1
    base = blocks.Block(inventory,blockType)
    inventory.add(base)
    base.selected = False#unselect so it can fall
    for i in range(info[1]): #rotate to correct direction
        base.rotate('clock')
    #repositon block to position in info
    size = constants.blockSize

    base.moveOverride(-base.rect.x,-base.rect.y)#move block back to 0,0
    base.moveOverride(size*(info[-1][0]+1),size*info[-1][1])
   
        
    for rect in base.rects:
        #get a position to blit onto the block image
        posRect = rect.move(-base.rect.x,-base.rect.y)
        base.image.blit(source,posRect,rect)
    base.moveOverride(0,-base.rect.y - 30)#move above top of inventory
    return base #return the block

def roll(DISPLAYSURF,clock):
    
    font = pygame.font.SysFont('ARIAL', 25)
    inven1 = inventory.Inventory(constants.inven1)
    inven2 = inventory.Inventory(constants.inven1)
    invenList = [inven1,inven2]
    inven2.changex = 1
    inven2.changey = -1#shrink inven2 to the right
    objects = pygame.sprite.Group()
    objects.add(inven1)
    objects.add(inven2)

    pageList = []
    towns.font = font
    for section in creditPages:
        background = pygame.Surface((11*constants.blockSize,11*constants.blockSize)).convert_alpha()
        background.fill(constants.WHITE)
        page = towns.longText(section)
        #move text so it is in the correct position
        page.rect.midtop = (round(background.get_width()/2),constants.blockSize)
        background.blit(page.image,page.rect)
        pageList.append(background)

    pageNo = 0 #page number in index
    blockNo = 0 #block number
    rightInven = False#left inventory selected
    currentInven = invenList[int(rightInven)]
    currentPage = pageList[pageNo]
    info = blockOrder[blockNo]
    makeBlock(info,currentInven,currentPage)

    done = False
    pause = pygame.time.get_ticks() + 400#know when to spawn a new block

    pygame.mixer.music.load("music/credits.mp3")
    pygame.mixer.music.play(-1)

    while not done:
    
        if pause < pygame.time.get_ticks():
            pause = pygame.time.get_ticks() + 400#reset time
            blockNo += 1 #move along in the blocks
            if blockNo < len(blockOrder):
                info = blockOrder[blockNo] 
                makeBlock(info,currentInven,currentPage)
                
            else:
                pygame.time.wait(4000)#wait 4 seconds before changing inventory
                pageNo += 1#if at the end of the blocks then move to next page
                if pageNo < len(creditPages):
                    currentPage = pageList[pageNo]
                    if rightInven:#right inventory selected
                        inven2.changex,inven2.changey = 1,-1#move inventories right
                        inven1.changex,inven1.changey = 1,1
                    else:#left inventory selected, move left
                        inven1.changex,inven1.changey = -1,-1#move inventories right
                        inven2.changex,inven2.changey = -1,1
                    rightInven = not rightInven
                    currentInven = invenList[int(rightInven)]
                    currentInven.empty()#remove previous credits
                    blockNo = -1#make next iteration start at 0
                else:
                    return True#if at the end of the credit pages then exit to menu

        for event in pygame.event.get():
            
            if event.type == QUIT:
                return False # return done and quit
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return True
    
        objects.update()
        DISPLAYSURF.fill(constants.SKY_BLUE)
        objects.draw(DISPLAYSURF)
        pygame.display.flip()
        clock.tick(60)
        pygame.display.update()
    

    
