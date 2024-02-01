import pygame as pg

#tetromino preview is the next tetromino and hold tetromino
class TetrominoPreview(pg.sprite.Sprite):
    def __init__(self, xPos, yPos, blockSizeScaleFactor):
        super().__init__()
        self.xPos = xPos
        self.yPos = yPos
        self.blockSizeScaleFactor = blockSizeScaleFactor
        self.type = None
        self.justSwapped = False

    def setType(self, type):
        self.type = type
        if type == 'empty':
            self.image = pg.image.load(f'images/{type}.png').convert_alpha()
        else:
            self.image = pg.image.load(f'images/{type}Preview.png').convert_alpha()
        self.image = pg.transform.scale(self.image, (self.image.get_width() * self.blockSizeScaleFactor, self.image.get_height() * self.blockSizeScaleFactor))
        self.rect = self.image.get_rect(center = (self.xPos, self.yPos))
    
    def getType(self):
        return self.type