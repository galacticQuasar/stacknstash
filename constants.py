import pygame

SCREEN_HEIGHT = 750
SCREEN_WIDTH = 700

multi = False #bonus mode

#colours
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
SKY_BLUE = (0,85,255)
GREEN = (0,255,0)
RED = (255,0,0)
DEEP_RED = (153,0,0)
PURPLE = (160,32,225)
YELLOW = (255,255,0)
CYAN = (0,239,255)
ORANGE = (255,165,0)

mainInvenPos = (180,290)
mainDunPos = (50,20)
#base size for unit square
blockSize = 30
#inventories for game
inven1 = ['*          *',
          '*          *',
          '*          *',
          '*          *',
          '*          *',
          '*          *',
          '*          *',
          '*          *',
          '*          *',
          '*          *',
          '************',
          pygame.image.load('sprites/inventory.png')]
#blocks for the game
image = pygame.image.load('sprites/blocks/block1.png')
#reverse of another block
image = pygame.transform.flip(image,True,False)
block1 = [' @@',
          '@@ ',
          '   ',
          '   ',
          True,
          image,
          GREEN
          ]

block2 = [' @@',
          ' @@',
          '   ',
          '   ',
          None,
          pygame.image.load('sprites/blocks/block2.png'),
          YELLOW]

block3 = [' @@',
          ' @ ',
          ' @ ',
          '   ',
          None,
          pygame.image.load('sprites/blocks/block3.png'),
          BLUE]

block4 = [' @ ',
          ' @ ',
          ' @ ',
          ' @ ',
          True,
          pygame.image.load('sprites/blocks/block4.png'),
          CYAN]
block5 = [' @ ',
          ' @@',
          ' @ ',
          '   ',
          None,
          pygame.image.load('sprites/blocks/block5.png'),
          PURPLE]

block6 = ['@@ ',
          ' @@',
          '   ',
          '   ',
          True,
          pygame.image.load('sprites/blocks/block1.png'),
          RED]
image = pygame.image.load('sprites/blocks/block3.png')
image = pygame.transform.flip(image,True,False)
image = pygame.transform.rotate(image,180)
block7 = [' @ ',
          ' @ ',
          ' @@',
          '   ',
          None,
          image,
          ORANGE]
#concise storage for blocks
blockList = [block1,block2,block3,block4,block5,block6,block7]

v = '1.3.2' #version no
