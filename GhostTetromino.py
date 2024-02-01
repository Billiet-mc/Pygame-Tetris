import pygame as pg

class GhostTetromino(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.blockList = []

    def addBlock(self, block):
        self.blockList.append(block)

    def getBlocks(self):
        return self.blockList
    
    def removeBlock(self, block):
        self.blockList.remove(block)
    
    def clear(self):
        self.blockList.clear()