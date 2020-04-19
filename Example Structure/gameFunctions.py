from pygame.rect import Rect
def getSquareRect(pos, gsize, padding=0):
    x,y = pos
    x = x*gsize + padding
    y = y*gsize + padding
    run = gsize-(padding*2)
    return Rect((x,y),(run,run))

def getCenterOfSquare(pos,gsize):
    x,y = pos
    x = x*gsize + gsize/2
    y = y*gsize + gsize/2
    return x,y
