import pygame as pg
from Block import Block
import Tetromino
from TetrominoPreview import TetrominoPreview
from GhostTetromino import GhostTetromino
import sys
from random import choice
import numpy as np
from time import sleep


class Game():
    def __init__(self):

        #initializing variables
        self.gameState = True
        self.blockSizeScaleFactor = 0.9375
        self.blockSize = pg.image.load('images/I.png').get_width() * self.blockSizeScaleFactor
        #offsets for the block grid's placement on scren
        self.xOffset = screenWidth/2 - self.blockSize * 5
        self.yOffset = 30 - self.blockSize * 3
        self.tetrominoList = ['I', 'O', 'L', 'J', 'S', 'Z', 'T']
        self.tetrominoSpawnBag = ['I', 'O', 'L', 'J', 'S', 'Z', 'T']
        #lockdown timer is extra time to be given to the player before a tetromino locks down
        self.tetrominoLockdownTimer = 500
        self.score = 0
        #fall timer is the amount of time before tetromino is automatically moved down due to gravity, fast is the amount of time when the down arrow is held
        self.tetrominoFallTimer = 1000
        self.tetrominoFastFallTimer = 100
        self.level = 1
        self.lineClears = 0
        #represents whether or not the last placed piece caused a tetris
        self.justTetrised = False
        #active during a streak of 'difficult' line clears
        self.difficultStreakActive = False
        self.clearStreakActive = False
        #length of the clear streak
        self.clearStreak = 0
        self.font = pg.font.Font('font/Seven Segment.ttf', 35)

        #sound affects and music
        self.music = pg.mixer.Sound('audio/music.mp3')
        self.music.play(loops=-1)
        self.music.set_volume(0.225)
        self.gameOverSound = pg.mixer.Sound('audio/gameOver.mp3')
        self.gameOverSound.set_volume(0.2)
        self.moveHorizontalSound = pg.mixer.Sound('audio/moveHorizontal.mp3')
        self.moveHorizontalSound.set_volume(0.3)
        self.rotateTetrominoSound = pg.mixer.Sound('audio/rotateTetromino.mp3')
        self.rotateTetrominoSound.set_volume(0.3)
        self.lockDownSound = pg.mixer.Sound('audio/lockdown.mp3')
        self.lockDownSound.set_volume(0.5)
        self.clearLinesSound = pg.mixer.Sound('audio/clearLines.mp3')
        self.clearLinesSound.set_volume(0.3)
        self.tetrisSound = pg.mixer.Sound('audio/tetris.mp3')
        self.tetrisSound.set_volume(0.3)


        self.backgroundSprite = pg.image.load('images/background.png')
        self.backgroundSprite = pg.transform.scale(self.backgroundSprite, (screenWidth, screenHeight))
        self.backgroundRect = self.backgroundSprite.get_rect(topleft = (0,0))

        #blockMatrix is the 10x25 grid of blocks which all tetrominoes are on
        self.blockMatrix = [ [Block('empty', self.blockSize, row, col, self.xOffset, self.yOffset) for col in range(10)] for row in range(25) ]
        self.blockGroup = pg.sprite.Group()
        for row in self.blockMatrix:
            for block in row:
                self.blockGroup.add(block)

        #score and level text
        self.scoreSprite = self.font.render('Score: 0000', False, 'white', 'black')
        self.scoreRect = self.scoreSprite.get_rect(center = (screenWidth - self.xOffset/2 - 10, 300))
        self.levelSprite = self.font.render(f'Level: {self.level}', False, 'white', 'black')
        self.levelRect = self.levelSprite.get_rect(midleft = (screenWidth - self.xOffset/2 - self.scoreRect.width/2 - 10, 375))

        #nextTetromino is the tetromino that appears in the top right and will be spawned next
        self.nextTetrominoSprite = TetrominoPreview(screenWidth - self.xOffset/2, self.yOffset + 61 + self.blockSize * 5 - self.blockSize/3, self.blockSizeScaleFactor)
        self.pickNextTetromino()
        self.nextTetrominoGroup = pg.sprite.GroupSingle()
        self.nextTetrominoGroup.add(self.nextTetrominoSprite)
        self.nextTetrominoTextSprite = self.font.render('NEXT', False, 'white')
        self.nextTetrominoTextRect = self.nextTetrominoTextSprite.get_rect(center = (self.nextTetrominoGroup.sprite.rect.centerx, self.nextTetrominoGroup.sprite.rect.centery + 80))

        #hold tetromino is the tetromino in the top left and is currently being held
        self.holdTetrominoSprite = TetrominoPreview(self.xOffset/2, self.yOffset + 61 + self.blockSize * 5 - self.blockSize/3, self.blockSizeScaleFactor)
        self.holdTetrominoSprite.setType('empty')
        self.holdTetrominoGroup = pg.sprite.GroupSingle()
        self.holdTetrominoGroup.add(self.holdTetrominoSprite)
        self.holdTetrominoTextSprite = self.font.render('HOLD', False, 'white')
        self.holdTetrominoTextRect = self.holdTetrominoTextSprite.get_rect(center = (self.holdTetrominoGroup.sprite.rect.centerx, self.holdTetrominoGroup.sprite.rect.centery + 80))

        self.controlsTextSprite = pg.image.load('images/controls.png')
        self.controlsTextSprite = pg.transform.scale(self.controlsTextSprite, (235, 180))
        self.controlsTextRect = self.controlsTextSprite.get_rect(midtop = (self.holdTetrominoGroup.sprite.rect.centerx - 4, 300))

        #game over screen
        self.gameOverRect = pg.Rect(screenWidth/2 - 100, screenHeight/2 - 50, 200, 150)
        self.gameOverBorderRect = pg.Rect(screenWidth/2 - 100 - 3, screenHeight/2 - 50 - 3, 206, 156)
        self.gameOverTextSprite = self.font.render('Game Over', False, 'white')
        self.gameOverTextRect = self.gameOverTextSprite.get_rect(center = (screenWidth/2, screenHeight/2))
        self.retryTextSprite = self.font.render('Retry', False, 'white', 'black')
        self.retryTextRect = self.retryTextSprite.get_rect(center = (screenWidth/2, screenHeight/2 + 50))
        self.retryTextBorderRect = pg.Rect(self.retryTextRect.left - 2, self.retryTextRect.top - 2, self.retryTextRect.width + 4, self.retryTextRect.height + 4)

        #the hollow preview that shows where the tetromino will be is the ghost tetromino
        self.ghostTetromino = GhostTetromino()
        #active tetromino is the tetromino the player is currently controlling
        self.activeTetromino = Tetromino.Tetromino()
        self.createTetromino()

    #draws everything to the screen when called
    def updateScreen(self):
        screen.fill((60,60,60))
        self.run()
        pg.display.flip()

    #called when player loses, sets gameState to False and erases active, hold, next, and ghost tetrominoes and plays the game over animation
    def gameOver(self):
        self.gameOverSound.play()
        blockList = [block for row in self.blockMatrix for block in row if block.type != 'empty' and block not in self.activeTetromino.getBlocks()]
        self.blinkBlocks(blockList, extend = True)
        self.gameState = False

        self.ghostTetromino.clear()
        self.activeTetromino.clear()
        self.activeTetromino.rotationState = 0
        self.activeTetromino.resets = 0
        self.activeTetromino.lockDownState = False
        self.activeTetromino.TSpinOverride = False
        self.activeTetromino.justRotated = False
        for row in self.blockMatrix:
            for block in row:
                block.typeChange('empty')
                block.isCenter = False
                block.active = False
                block.blinkType = None

        self.holdTetrominoGroup.sprite.setType('empty')
        self.nextTetrominoGroup.sprite.setType('empty')
        pg.event.clear()

    #sets gameState to True, reinitializes variables and starts over the game when called
    def resetGame(self):
        self.gameState = True
        self.score = 0
        self.tetrominoFallTimer = 1000
        self.tetrominoFastFallTimer = 100
        self.level = 1
        self.lineClears = 0
        self.justTetrised = False
        self.difficultStreakActive = False
        self.clearStreakActive = False
        self.clearStreak = 0

        self.addScore(0)
        self.levelSprite = self.font.render(f'Level: {self.level}', False, 'white', 'black')
        self.music.play(loops=-1)

        self.pickNextTetromino()
        self.createTetromino()

    #draws a black and white border (if outline is True), or just a black rectangle (if outline is False)
    def drawBorder(self, x, y, width, height, outline = False):
        if outline:
            outerRect = pg.Rect(x-6, y-6, width + 12, height + 12)
            pg.draw.rect(screen, 'white', outerRect)
            middleRect = pg.Rect(x-5, y-5, width + 10, height + 10)
            pg.draw.rect(screen, 'black', middleRect)
            innerRect = pg.Rect(x-2, y-2, width + 4, height + 4)
            pg.draw.rect(screen, 'white', innerRect)
        
        else:
            finalRect = pg.Rect(x, y, width, height)
            pg.draw.rect(screen, 'black', finalRect)

    #draws either the black rectangles behind hold and next tetrominoes and the blockMatrix (is outline is False), or the score and level borders (if outline is true)
    def updateBorders(self, outline):
        if outline:
            self.drawBorder(self.scoreRect.left, self.scoreRect.top, self.scoreSprite.get_width(), self.scoreSprite.get_height(), outline)
            self.drawBorder(self.levelRect.left, self.levelRect.top, self.levelSprite.get_width(), self.levelSprite.get_height(), outline)
        else:
            self.drawBorder(self.holdTetrominoSprite.xPos - 75, self.holdTetrominoSprite.yPos - 55, 150, 110, outline)
            self.drawBorder(self.nextTetrominoSprite.xPos - 75, self.nextTetrominoSprite.yPos - 55, 150, 110, outline)
            self.drawBorder(self.xOffset, self.yOffset + self.blockSize * 5 - self.blockSize/3, self.blockSize * 10, self.blockSize * 20 + self.blockSize/3, outline)

    #adds specified score and updates the sprite
    def addScore(self, amount):
        #zeroString is the amount of zeros to add to the front of the score if the score is less than 4 digits. (Ex. score of 36 would get turned into 0036)
        zeroString = ''
        if self.difficultStreakActive and amount > 5: amount *= 1.5
        self.score = self.score + amount
        if len(str(self.score)) < 4:
            for i in range(4-len(str(self.score))):
                zeroString += '0'
        scoreString = f'Score: {zeroString + str(self.score)}'
        self.scoreSprite = self.font.render(scoreString, False, 'white', 'black')

    #swaps the tetromino in hold with the activeTetromino
    def addTetrominoToHold(self):
        swapType = self.activeTetromino.getType()

        #deletes active tetromino
        for block in self.activeTetromino.getBlocks():
            block.typeChange('empty')
            block.active = False
            block.isCenter = False
            block.blinkType = None
        self.activeTetromino.clear()

        #spawns hold tetromino to the playfeild
        if not self.holdTetrominoSprite.getType() == 'empty':
            self.createTetromino(self.holdTetrominoSprite.getType())
        else:
            self.createTetromino()
        
        #set hold tetromino to what the active tetromino was
        self.holdTetrominoSprite.setType(swapType)
        self.holdTetrominoSprite.justSwapped = True



    #check if all blocks are empty and add the proper amount of score
    def detectPerfectClear(self, linesCleared):
        if False not in [ block.type == 'empty' for row in self.blockMatrix for block in row ]:
            if not self.justTetrised:
                match linesCleared:
                    case 1: self.addScore(800 * self.level)
                    case 2: self.addScore(1200 * self.level)
                    case 3: self.addScore(1800 * self.level)
                    case 4: self.addScore(2000 * self.level)
            else:
                self.addScore(3200 * self.level)

    #switches all the blocks in the given block list to empty and back depending on toggle
    def blinkBlocksToggle(self, blockList, toggle):
        if toggle:
            for block in blockList:
                if block.blinkType != None:
                    block.typeChange(block.blinkType)
                else:
                    block.typeChange('empty')
        else:
            for block in blockList:
                block.typeChange('empty')

    #play the blinking animation for every block in the given blocklist
    def blinkBlocks(self, blockList, extend = False):
        self.blinkBlocksToggle(blockList, False)
        self.updateScreen()
        sleep(0.10)

        self.blinkBlocksToggle(blockList, True)
        self.updateScreen()
        sleep(0.10)

        self.blinkBlocksToggle(blockList, False)
        self.updateScreen()
        sleep(0.10)

        self.blinkBlocksToggle(blockList, True)
        self.updateScreen()
        sleep(0.10)

        if extend:
            self.blinkBlocks(blockList)

    #returns a list of all blocks that are creating a full row of blocks, or blocks that are about to be removed due to a line clear
    #group in rows groups the blocks in the structure [[row 1 of blocks] [row 2 of blocks] [row 3 of blocks] [row 4 of blocks]]
    def getBlockList(self, groupInRows = False):
        blockList = []
        for row in self.blockMatrix:
            if False not in [ (block.type != 'empty') for block in row ]:
                for block in row:
                    blockList.append(block)
        if blockList and groupInRows:
            blockList = [ blockList[i:i+10] for i in range(0, len(blockList), 10)]

        return blockList
    
    #to be called after every tetromino lockdown, removes any lines that are full and moves the above lines down
    def clearLines(self):
        blockList = self.getBlockList()
        
        if blockList:
            if len(blockList) <= 30: self.clearLinesSound.play()
            else: self.tetrisSound.play()

            self.blinkBlocks(blockList)

            #group the blocks in blocklist by rows
            blockList = [ blockList[i:i+10] for i in range(0, len(blockList), 10)]
            
            match len(blockList):
                case 1: self.addScore(100*self.level)
                case 2: self.addScore(300*self.level)
                case 3: self.addScore(500*self.level)
                case 4: self.addScore(800*self.level)

            for row in blockList:
                for block in row:
                    block.typeChange('empty')

                #gravBlockList is the list of blocks that need to be moved down after a line clear due to gravity
                gravBlockList = []
                #add all blocks above the row currently being cleared to gravBlockList
                for irow in range(block.row):
                    for icol in range(10):
                        iblock = self.blockMatrix[irow][icol]
                        if iblock.type != 'empty':
                            gravBlockList.append(iblock)
                #moves all gravBlocks down
                for gravBlock in reversed(gravBlockList):
                    self.moveBlock(gravBlock, 'down', False)

                self.lineClears += 1
                #if the player clears 10 lines, level up, increase falling speed
                if self.lineClears % 10 == 0:
                    self.level += 1
                    self.levelSprite = self.font.render(f'Level: {self.level}', False, 'white', 'black')
                    self.tetrominoFallTimer = int(((0.8 - ((self.level - 1) * 0.007))**(self.level - 1)) * 1000) if self.level < 19 else self.tetrominoFallTimer
                    self.tetrominoFastFallTimer = self.tetrominoFallTimer//10
            
            #clearing events so key presses inputted during the clearing animation are not processed
            pg.event.clear()
            return True
        pg.event.clear()
        return False



    #picks tetromino in the top right next preview
    def pickNextTetromino(self):
        #when a tetromino is picked to be spawned (the tetromino is picked from the spawnBag), it is removed from the spawnBag. 
        #when the spawnBag is emptied, it is refilled to match the contents of tetrominoList 
        nextTetrominoType = choice(self.tetrominoSpawnBag)
        self.tetrominoSpawnBag.remove(nextTetrominoType)
        self.nextTetrominoSprite.setType(nextTetrominoType)
        if not self.tetrominoSpawnBag: self.tetrominoSpawnBag = [i for i in self.tetrominoList]

    #spawns in the next tetromino.
    #if inputType is specified it will spawn a tetromino of that type
    def createTetromino(self, inputType = None):
            #position offset of the tetromino being spawed
            xOffset = 3
            yOffset = 3
            cantSpawn = False

            if not inputType:
                type = self.nextTetrominoSprite.getType()
                shape = Tetromino.tetrominoShapes[type]
                self.pickNextTetromino()
            else:
                type = inputType
                shape = Tetromino.tetrominoShapes[type]

            #loops through the specified shape in Tetromino.tetrominoShapes to get the coordinates of each block to be spawned and checks if anything is already there            
            for row in range(len(shape)):
                for col in range(len(shape[row])):
                    if shape[row][col] != ' ':
                        if not self.checkIfOpen(row+yOffset, col+xOffset):
                            cantSpawn = True

            #loops through the specified shape in Tetromino.tetrominoShapes to get the coordinates of each block to be spawned and spawns them
            for row in range(len(shape)):
                for col in range(len(shape[row])):
                    if shape[row][col] != ' ':
                        block = self.blockMatrix[row+yOffset][col+xOffset]
                        block.typeChange(type)
                        self.activeTetromino.addBlock(block)
                        if shape[row][col] == 'c':
                            block.isCenter = True

            #initialize tetromino variables
            self.activeTetromino.rotationState = 0
            self.activeTetromino.resets = 0
            self.activeTetromino.lockDownState = False
            self.activeTetromino.TSpinOverride = False
            self.activeTetromino.justRotated = False

            pg.time.set_timer(MOVEBLOCKS, self.tetrominoFallTimer)

            #if the tetromino spawns in the lockdown state
            if not self.validDownMovementCheck():
                pg.time.set_timer(LOCKDOWNTIMER, self.tetrominoFallTimer + self.tetrominoLockdownTimer)
                self.activeTetromino.lockDownState = True
            
            pg.time.set_timer(DELAYEDAUTOSHIFT, 0)
            pg.time.set_timer(AUTOREPEATRATE, 0)

            self.createGhostTetromino()
            self.updateScreen()

            if cantSpawn:
                self.music.stop()
                self.gameOver()

    #creates the ghost tetromino
    def createGhostTetromino(self):
        if self.ghostTetromino.getBlocks():
            self.clearGhost()

        for block in self.activeTetromino.getBlocks():
            self.ghostTetromino.addBlock(block)
        self.moveGhostTetromino()

    #places the ghost tetromino in the proper position
    def moveGhostTetromino(self):
        while self.validDownMovementCheck(self.ghostTetromino):
            orderedBlockList = self.createOrderedList('down', self.ghostTetromino)

            for block in orderedBlockList:
                self.moveGhostBlock(block)

    #move a blocks ghost properties
    def moveGhostBlock(self, block):
        nextPosBlock = self.blockMatrix[block.row+1][block.column]
        nextPosBlock.typeChange('ghost')
        if not block.active:
            block.typeChange('empty')
        nextPosBlock.isGhost = True
        block.isGhost = False
        self.ghostTetromino.addBlock(nextPosBlock)
        self.ghostTetromino.removeBlock(block)

    #delete current ghost tetromino
    def clearGhost(self):
        for block in self.ghostTetromino.getBlocks():
            block.isGhost = False
            if not block.active: block.typeChange('empty')
        self.ghostTetromino.clear()



    #calls the approprite movement check function based on direction
    def validMovementCheck(self, direction):
        match direction:
            case 'down':
                return self.validDownMovementCheck()
            case 'right':
                return self.validHorizontalMovementCheck(1)
            case 'left':
                return self.validHorizontalMovementCheck(-1)

    #checks if the tetromino can move down
    def validDownMovementCheck(self, tetromino = 'default'):
        if tetromino == 'default':
            tetromino = self.activeTetromino

        #fails if next pos is out of bounds or not empty
        for block in tetromino.getBlocks():
            if block.row >= 24: return False
            nextBlock = self.blockMatrix[block.row+1][block.column]
            if nextBlock not in tetromino.getBlocks():
                if not nextBlock.type == 'empty' and not nextBlock.type == 'ghost':
                    return False
        return True
    
    #checks if the tetromino can move left or right
    def validHorizontalMovementCheck(self, direction):

        #fails if next pos is out of bounds or not empty
        for block in self.activeTetromino.getBlocks():
            if (block.column >= 9 and direction == 1) or (block.column <= 0 and direction == -1): return False
            nextBlock = self.blockMatrix[block.row][block.column+direction]
            if nextBlock not in self.activeTetromino.getBlocks():
                if not nextBlock.type == 'empty' and not nextBlock.type == 'ghost':
                    return False
        return True

    #takes a list of blocks and orders them such that looping through the list and moving those blocks causes no collisions with the blocks in the list
    def createOrderedList(self, priority, tetromino = 'default'):
        if tetromino == 'default':
            tetromino = self.activeTetromino

        orderedList = []
        match priority:
            case 'down':
                #sorts the list by row numbers, higher numbers come first
                orderedList = sorted([ (block.row, block) for block in tetromino.getBlocks() ], key = lambda x: x[0], reverse = True)

            case 'right':
                orderedList = sorted([ (block.column, block) for block in tetromino.getBlocks() ], key = lambda x: x[0], reverse = True)

            case 'left':
                #this one is not reversed because we want the leftmost blocks to move left before any others
                orderedList = sorted([ (block.column, block) for block in tetromino.getBlocks() ], key = lambda x: x[0])
            
        #formats the list from [(row, block), (row, block)] to [block, block]
        orderedList = [ i[1] for i in orderedList ]
            
        return orderedList
 
    #moves a single block in the specified direction
    def moveBlock(self, block, direction, inTetromino):
        match direction:
                case 'down': direction = (1,0)
                case 'right': direction = (0,1)
                case 'left': direction = (0,-1)
        
        blockType = block.type
        nextPosBlock = self.blockMatrix[block.row+direction[0]][block.column+direction[1]]

        nextPosBlock.typeChange(blockType)
        nextPosBlock.blinkType = blockType

        block.typeChange('empty')
        block.blinkType = None

        if block.active:
            block.active = False
            nextPosBlock.active = True

        if block.isCenter:
            nextPosBlock.isCenter = True
            block.isCenter = False

        if inTetromino:
            self.activeTetromino.addBlock(nextPosBlock)
            self.activeTetromino.removeBlock(block)

    #function is called when a tetromino locks down and handles all the logic
    def lockDownTetromino(self):
        self.clearGhost()

        #if tetromino locks down too high game is over
        if False not in [block.row < 5 for block in self.activeTetromino.getBlocks()]:
            self.music.stop()
            self.gameOver()

        if self.gameState:
            TSpinPerformed = False
            linesCleared = len(self.getBlockList(True))

            if self.activeTetromino.getType() == 'T' and self.activeTetromino.justRotated:
                TSpinPerformed = self.detectTSpin()
            
            if linesCleared == 4: self.justTetrised = True
            else: self.justTetrised = False

            if linesCleared == 4 or (TSpinPerformed and linesCleared > 0):
                self.difficultStreakActive = True

            if not TSpinPerformed or linesCleared < 4:
                self.difficultStreakActive = False

            self.holdTetrominoSprite.justSwapped = False

            #tetromino is no longer active
            for block in self.activeTetromino.getBlocks():
                block.active = False
                block.isCenter = False
            self.activeTetromino.clear()

            #detect clear streak and add appropriate amount of points
            self.clearStreakActive = self.clearLines()
            if self.clearStreakActive:
                self.clearStreak += 1
                self.addScore(50 * self.clearStreak * self.level)
            else:
                self.clearStreak = 0

            #detect perfect clear and add appropriate amount of points
            self.detectPerfectClear(linesCleared)

            self.updateScreen()
            self.lockDownSound.play()
            sleep(0.1)
            pg.event.clear()
            self.createTetromino()

    #moves tetromino in the given direction. if movement is called by the lockdown event lockdown is True
    def moveTetromino(self, direction, lockdown = False):
        if self.validMovementCheck(direction):
            
            self.activeTetromino.justRotated = False

            #move each block in the tetromino
            orderedBlockList = self.createOrderedList(direction)
            for block in orderedBlockList:
                self.moveBlock(block, direction, True)
                
            #if tetromino just moved down
            if direction == 'down':
                #if move is called from the lockdown event
                if lockdown:
                    pg.time.set_timer(MOVEBLOCKS, self.tetrominoFallTimer)

                pg.time.set_timer(LOCKDOWNTIMER, 0)
                self.activeTetromino.lockDownState = False

                #check to enter lockdown state
                if not self.validDownMovementCheck():
                    self.activeTetromino.lockDownState = True
                    pg.time.set_timer(LOCKDOWNTIMER, self.tetrominoFallTimer + self.tetrominoLockdownTimer)

            #if tetromino just moved left or right
            elif direction in ('left', 'right') and self.gameState: 
                self.moveHorizontalSound.play()
                #check to enter lockdown state
                if not self.validDownMovementCheck():
                    self.activeTetromino.resets += 1

                if self.activeTetromino.resets < 15:
                    if not self.validDownMovementCheck():
                        self.activeTetromino.lockDownState = True
                        pg.time.set_timer(LOCKDOWNTIMER, self.tetrominoFallTimer + self.tetrominoLockdownTimer)

                    if self.activeTetromino.lockDownState and self.validDownMovementCheck():
                        self.activeTetromino.lockDownState = False

                else:
                    self.hardDropTetromino()

                
        #if cant move and the direction was down lock down tetromino
        elif direction == 'down':
            self.lockDownTetromino()
            return True
        
        return False

    #moves the tetromino as far down as possible and locks it down
    def hardDropTetromino(self):
        hitBottom = False
        while not hitBottom:
            hitBottom = self.moveTetromino('down')
            if not hitBottom: self.addScore(2)



    #checks if the block at given row and column is empty or a ghost or in active tetromino
    def checkIfOpen(self, row, col):
        if (0 <= row < 25 and 0 <= col < 10):
            checkBlock = self.blockMatrix[row][col]
            if (checkBlock.type == 'empty' or checkBlock in self.activeTetromino.getBlocks() or checkBlock.isGhost):
                return True
        return False

    #returns a list of blocks surrounding the given checkBlock that are in activeTetromino
    #checkBlock can be a tuple if its row and column are out of bounds/ not actually in blockMatrix
    def getSurroundingActiveBlocks(self, checkBlock):
        surroundingBlocks = []

        if isinstance(checkBlock, tuple):
            row = checkBlock[0]
            column = checkBlock[1]
        else:
            row = checkBlock.row
            column = checkBlock.column

        for block in self.activeTetromino.getBlocks():
            if (row - 1 <= block.row <= row + 1) and (column - 1 <= block.column <= column + 1):
                surroundingBlocks.append(block)
        return surroundingBlocks

    #returns a list of the blocks diagonally connected to the center of the the T tetromino
    #x is a block in tetromino,  c is the center block,   z is the corners
    #
    #               z x z
    #               x c x
    #               z   z
    def getTCorners(self):
        cornerBlocks = []
        centerBlock = self.activeTetromino.getCenter()

        for row in range(centerBlock.row-1, centerBlock.row+2):
            for column in range(centerBlock.column-1, centerBlock.column+2):
                if (row == centerBlock.row - 1 or row == centerBlock.row + 1) and (column == centerBlock.column - 1 or column == centerBlock.column + 1):
                    if 0 <= row < 25 and 0 <= column < 10:
                        cornerBlocks.append(self.blockMatrix[row][column])
                    else:
                        cornerBlocks.append((row, column))
        return cornerBlocks

    #called after every lockdown of a 'T' tetromino; detects t spin and type of tspin and adds appropriate points
    def detectTSpin(self):
        cornerBlocks = self.getTCorners()
        TSpinPoints = {'full': [400, 800, 1200, 1600], 'mini': [100, 200, 400, 0]}
        backCornerBlocks = []
        frontCornerBlocks = []
        TSpinType = ''
        
        #if a block is a back corner it is touching 2 active blocks, but if its a front corner its touching 3
        for block in cornerBlocks:
            surroundingActiveBlocks = self.getSurroundingActiveBlocks(block)
            if len(surroundingActiveBlocks) == 2: backCornerBlocks.append(block)
            if len(surroundingActiveBlocks) == 3: frontCornerBlocks.append(block)
        
        #if any of the corners are open remove them from the list
        for block in reversed(backCornerBlocks):
            if isinstance(block, tuple):
                row = block[0]
                column = block[1]
            else:
                row = block.row
                column = block.column
            
            if self.checkIfOpen(row, column):
                backCornerBlocks.remove(block)

        for block in reversed(frontCornerBlocks):
            if isinstance(block, tuple):
                row = block[0]
                column = block[1]
            else:
                row = block.row
                column = block.column
            
            if self.checkIfOpen(row, column):
                frontCornerBlocks.remove(block)

        if (len(frontCornerBlocks) == 2 and len(backCornerBlocks) >= 1) or self.activeTetromino.TSpinOverride:
            TSpinType = 'full'
        elif len(frontCornerBlocks) == 1 and len(backCornerBlocks) == 2:
            TSpinType = 'mini'

        #add appropriate amount of points based on tspin type and lines cleared by the tspin
        if TSpinType != '':
            self.addScore(TSpinPoints[TSpinType][len(self.getBlockList(True))] * self.level)
            return True
        return False
        


    #takes a list of coordinates on the block matrix and rotates them about a center coord; written by chatGPT
    def rotateTetrominoCoords(self, direction, preRotatedCoords, centerCoord):
        rotatedCoords = []

        for x, y in preRotatedCoords:
            rotatedCoords.append( [x - centerCoord[0], y - centerCoord[1]] )

        rotationMatrix = np.array([[0, 1], [-1, 0]]) if direction == 'right' else np.array([[0, -1], [1, 0]])

        rotatedCoords = [[int(x * rotationMatrix[0, 0] + y * rotationMatrix[0, 1]),
                          int(x * rotationMatrix[1, 0] + y * rotationMatrix[1, 1])]
                         for x, y in rotatedCoords]
        
        for coord in rotatedCoords:
            coord[0] = coord[0] + centerCoord[0]
            coord[1] = coord[1] + centerCoord[1]

        return rotatedCoords

    #implementation of the SRS (Super Rotation System)
    def rotateTetromino(self, direction):
        type = self.activeTetromino.getType()
        #picks the offset table to use from Tetromino.tetrominoRotationOffsets
        if type == 'L' or type == 'J' or type == 'S' or type == 'Z' or type == 'T':
            table = 'default'
        else: table = type

        #generate the rotated coords of the tetromino
        preRotatedCoords = [ [block.row, block.column] for block in self.activeTetromino.getBlocks() ]
        centerCoord = [[block.row, block.column] for block in self.activeTetromino.getBlocks() if block.isCenter][0]
        rotatedCoords = self.rotateTetrominoCoords(direction, preRotatedCoords, centerCoord)

        #set the rotation state of the tetromino after rotating
        rotationState = self.activeTetromino.rotationState
        nextRotationState = (rotationState+1)%4 if direction == 'right' else rotationState-1 if rotationState != 0 else 3

        #generate final list of offsets based off SRS guideline
        rotationOffsetTable = Tetromino.tetrominoRotationOffsets[table]
        currentStateOffsets = [ offset for offset in rotationOffsetTable[rotationState] ]
        nextStateOffsets = [ offset for offset in rotationOffsetTable[nextRotationState] ]
        finalRotationOffsets = [ ( -(currentStateOffsets[i][0] - nextStateOffsets[i][0]), currentStateOffsets[i][1] - nextStateOffsets[i][1] ) for i in range(len(currentStateOffsets))]

        #loop through the offsets, shift the tetromino by the offset and if it can be placed there place it and stop the loop
        for offset in finalRotationOffsets:
            
            #if the tetromino can be placed at the offset
            if self.gameState and False not in [ self.checkIfOpen(coord[0]+offset[0], coord[1]+offset[1]) for coord in rotatedCoords ]:
                self.rotateTetrominoSound.play()
            
                finalRotatedCoords = [ (coord[0]+offset[0], coord[1]+offset[1]) for coord in rotatedCoords ]
                #if the tetromino went to the last offset then it will be a full T spin no matter what
                self.activeTetromino.TSpinOverride = offset == finalRotationOffsets[-1]
                self.activeTetromino.justRotated = True

                #delete active tetromino
                for block in self.activeTetromino.getBlocks():
                    block.typeChange('empty')
                    block.active = False
                    block.isCenter = False
                    block.blinkType = None
                self.activeTetromino.clear()

                #recreate active tetromino at rotated coords
                for coord in finalRotatedCoords:
                    block = self.blockMatrix[coord[0]][coord[1]]
                    block.typeChange(type)
                    block.active = True
                    block.blinkType = block.type
                    if coord[0] == centerCoord[0] + offset[0] and coord[1] == centerCoord[1] + offset[1]: block.isCenter = True
                    self.activeTetromino.addBlock(block)
                self.activeTetromino.rotationState = nextRotationState
                
                #lock down state logic
                if self.activeTetromino.lockDownState:
                    self.activeTetromino.resets += 1

                    #if we rotate out of a lockdownable position
                    if game.validMovementCheck('down'):
                        self.activeTetromino.lockDownState = False
                        pg.time.set_timer(LOCKDOWNTIMER, 0)

                    #rotating can reset the lockdown timer
                    #limit lock down timer resets to 15
                    if self.activeTetromino.resets < 15:
                        if not game.validMovementCheck('down'):
                            pg.time.set_timer(LOCKDOWNTIMER, self.tetrominoLockdownTimer + self.tetrominoFallTimer)
                    else:
                        self.hardDropTetromino()

                #if we rotate into a 'lock-downable' position
                elif not self.validDownMovementCheck():
                    self.activeTetromino.lockDownState = True
                    pg.time.set_timer(LOCKDOWNTIMER, self.tetrominoFallTimer + self.tetrominoLockdownTimer)
                        
                break

    #draws everything on the screen
    def run(self):
        self.updateBorders(outline = False)
        self.blockGroup.draw(screen)
        screen.blit(self.backgroundSprite, self.backgroundRect)
        
        
        self.nextTetrominoGroup.draw(screen)
        self.holdTetrominoGroup.draw(screen)

        self.updateBorders(outline = True)
        screen.blit(self.scoreSprite, self.scoreRect)
        screen.blit(self.levelSprite, self.levelRect)
        screen.blit(self.nextTetrominoTextSprite, self.nextTetrominoTextRect)
        screen.blit(self.holdTetrominoTextSprite, self.holdTetrominoTextRect)
        screen.blit(self.controlsTextSprite, self.controlsTextRect)

        if not self.gameState:

            pg.draw.rect(screen, 'white', self.gameOverBorderRect)
            pg.draw.rect(screen, 'black', self.gameOverRect)
            screen.blit(self.gameOverTextSprite, self.gameOverTextRect)
            pg.draw.rect(screen, 'white', self.retryTextBorderRect)
            screen.blit(self.retryTextSprite, self.retryTextRect)
            

pg.init()

MOVEBLOCKS = pg.USEREVENT + 1
FASTMOVEBLOCKS = pg.USEREVENT + 2
DELAYEDAUTOSHIFT = pg.USEREVENT + 3
AUTOREPEATRATE = pg.USEREVENT + 4
LOCKDOWNTIMER = pg.USEREVENT + 5

screenWidth = 800
screenHeight = 720
screen = pg.display.set_mode((screenWidth, screenHeight))
clock = pg.time.Clock()
game = Game()
#either 'right' for right arrow or 'left' for left arrow
latestPressed = ''

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        elif event.type == pg.KEYDOWN:
            if game.gameState:
                if event.key == pg.K_RIGHT:
                    pg.time.set_timer(AUTOREPEATRATE, 0)
                    game.moveTetromino('right')
                    if game.gameState:
                        game.createGhostTetromino()
                        pg.time.set_timer(DELAYEDAUTOSHIFT, 167)
                        latestPressed = 'right'

                if event.key == pg.K_LEFT:
                    pg.time.set_timer(AUTOREPEATRATE, 0)
                    game.moveTetromino('left')
                    if game.gameState:
                        game.createGhostTetromino()
                        pg.time.set_timer(DELAYEDAUTOSHIFT, 167)
                        latestPressed = 'left'

                if event.key == pg.K_DOWN:
                    pg.time.set_timer(MOVEBLOCKS, 0)
                    game.moveTetromino('down')
                    if game.gameState:
                        game.addScore(1)
                        pg.time.set_timer(FASTMOVEBLOCKS, game.tetrominoFastFallTimer)

                if event.key == pg.K_x:
                    game.rotateTetromino('right')
                    if game.gameState:
                        game.createGhostTetromino()

                if event.key == pg.K_z:
                    game.rotateTetromino('left')
                    if game.gameState:
                        game.createGhostTetromino()

                if event.key == pg.K_UP:
                    if not game.holdTetrominoSprite.justSwapped:
                        game.addTetrominoToHold()

                if event.key == pg.K_SPACE:
                    game.hardDropTetromino()

        keys = pg.key.get_pressed()
        if event.type == pg.KEYUP and game.gameState:
            if event.key == pg.K_DOWN:
                pg.time.set_timer(FASTMOVEBLOCKS, 0)
                pg.time.set_timer(MOVEBLOCKS, game.tetrominoFallTimer)
                #if down key is released in lockdownable position
                if not game.validMovementCheck('down'):
                    pg.time.set_timer(LOCKDOWNTIMER, game.tetrominoLockdownTimer + game.tetrominoFallTimer)
                    game.activeTetromino.lockDownState = True
            
            if (event.key == pg.K_LEFT and latestPressed == 'left') or (event.key == pg.K_RIGHT and latestPressed == 'right'):
                pg.time.set_timer(DELAYEDAUTOSHIFT, 0)
                pg.time.set_timer(AUTOREPEATRATE, 0)

        #if clicking on the retry button
        if not game.gameState and event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if game.retryTextRect.collidepoint(event.pos):
                pg.time.set_timer(MOVEBLOCKS, 0)
                pg.time.set_timer(FASTMOVEBLOCKS, 0)
                pg.time.set_timer(DELAYEDAUTOSHIFT, 0)
                pg.time.set_timer(AUTOREPEATRATE, 0)
                pg.time.set_timer(LOCKDOWNTIMER, 0)
                game.resetGame()



        if event.type == MOVEBLOCKS and not game.activeTetromino.lockDownState:
            game.moveTetromino('down')
            #level 19 is the last speed increase and is supposed to move the tetromino every 0.8 milliseconds which isnt possible so just move twice every MOVEBLOCKS event called at level 18 speed
            if game.level >= 19 and game.validDownMovementCheck():
                game.moveTetromino('down')

        if event.type == FASTMOVEBLOCKS and keys[pg.K_DOWN]:
            if not game.activeTetromino.lockDownState:
                game.moveTetromino('down')
                game.addScore(1)

        if event.type == LOCKDOWNTIMER:
            game.moveTetromino('down', lockdown=True)

        if event.type == DELAYEDAUTOSHIFT:
            game.moveTetromino(latestPressed)
            game.createGhostTetromino()
            pg.time.set_timer(AUTOREPEATRATE, 33)
            pg.time.set_timer(DELAYEDAUTOSHIFT, 0)

        if event.type == AUTOREPEATRATE:
            game.moveTetromino(latestPressed)
            game.createGhostTetromino()
        
    game.updateScreen()