import sys

import pygame

from consts import *
from worldio import *
from gameClasses import World

try:
    gs = int(sys.argv[1])
    world = World(gs,None,None,100)
except ValueError:
    world = readWorld(sys.argv[1],World)

pygame.display.init()
screen = pygame.display.set_mode((576, 576))
Clock = pygame.time.Clock()

running = True

while running:
    Clock.tick(60)
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = False
        
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            running = False
        
        elif event.key == pygame.K_q:
            stime = time.time()
            pygame.image.save(screen, "Screenshot_%d.png" % stime)
            print "Wrote Screenshot_%d.png" % stime
        
    elif event.type == pygame.MOUSEBUTTONDOWN:
        x,y = event.pos
        x /= world.gridsize
        y /= world.gridsize
        if world.grid[x][y] == MAT_SOLID:
            mat = MAT_EMPTY
        else:
            mat = MAT_SOLID
        
        world.grid[x][y] = mat
        
    world.draw(screen)
    
    pygame.display.update()

print writeWorld(world)