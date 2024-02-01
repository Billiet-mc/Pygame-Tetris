import pygame as pg

#the blockMatrix is an array of instances of the block class
class Block(pg.sprite.Sprite):
    def __init__(self,  type, size, row, column, xOffset, yOffset):
        super().__init__()
        self.active = False
        self.type = type
        self.blinkType = None
        self.isCenter = False
        self.isGhost = False

        self.size = size
        self.row = row
        self.column = column
        self.xOffset = xOffset
        self.yOffset = yOffset

        self.image = pg.image.load(f'images/{type}.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(topleft = (column*size+xOffset, row*size+yOffset))
    
    def typeChange(self, type):
        if type != 'ghost' or (type == 'ghost' and not self.active):
            self.type = type
            self.image = pg.image.load(f'images/{type}.png').convert_alpha()
            self.image = pg.transform.scale(self.image, (self.size, self.size))
            self.rect = self.image.get_rect(topleft = (self.column*self.size+self.xOffset, self.row*self.size+self.yOffset))
        


