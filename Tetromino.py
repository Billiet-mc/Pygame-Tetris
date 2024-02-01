class Tetromino:
    def __init__(self):
        self.rotationState = 0
        #number of rotations
        self.resets = 0
        self.lockDownState = False
        self.TSpinOverride = False
        self.justRotated = False
        self.blockList = []

    def addBlock(self, block):
        block.active = True
        self.blockList.append(block)

    def getBlocks(self):
        return self.blockList
    
    def removeBlock(self, block):
        self.blockList.remove(block)

    def clear(self):
        self.blockList.clear()

    def getType(self):
        return self.blockList[0].type

    def getCenter(self):
        for block in self.blockList:
            if block.isCenter:
                return block




tetrominoShapes = {
'I': ['    ',
      'xcxx'],

'O': [' xx',
      ' cx' ],

'L': ['  x',
      'xcx' ],

'J': ['x',
      'xcx' ],

'S': [' xx',
      'xc' ],

'Z': ['xx',
      ' cx'],

'T': [' x',
      'xcx']

}

#the rows of the matrices represent the rotation states (initial, 90 degrees clockwise, 180 degrees, 270 degrees clockwise)
#the columns of the matrices are the offsets in order (offset 1, offset 2, offset 3, etc.)
# the offsets are (rowOffset, columnOffset) pairs, or (yOffset, xOffset)
# deriving the proper rotation yOffset from these values gives you the proper values assuming that higher rows have higher numbers, like in a traditional graph.
# however in my implementation the higher the row's internal number the lower it is on the screen (row 4 is one row below row 3 as opposed to one row above row 3).
# So whenever I calculate the yOffset I have to multiply it by negative one afterwards
# the xOffset is fine as is when calculated

tetrominoRotationOffsets = {
'default': [[( 0, 0), ( 0, 0), ( 0, 0), ( 0, 0), ( 0, 0)],
            [( 0, 0), ( 0,+1), (-1,+1), (+2, 0), (+2,+1)],
            [( 0, 0), ( 0, 0), ( 0, 0), ( 0, 0), ( 0, 0)],
            [( 0, 0), ( 0,-1), (-1,-1), (+2, 0), (+2,-1)]],

'I':       [[( 0, 0), ( 0,-1), ( 0,+2), ( 0,-1), ( 0,+2)],
            [( 0,-1), ( 0, 0), ( 0, 0), (+1, 0), (-2, 0)],
            [(+1,-1), (+1,+1), (+1,-2), ( 0,+1), ( 0,-2)],
            [(+1, 0), (+1, 0), (+1, 0), (-1, 0), (+2, 0)]],

'O':       [[( 0, 0)],
            [(-1, 0)],
            [(-1,-1)],
            [( 0,-1)]]

}