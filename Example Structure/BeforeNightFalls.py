import pygame, time, os, sys

from consts import *
from gameClasses import *
from worldio import *

# pygame.font.init()
# pygame.display.init()
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()                      #initialize pygame

screen = pygame.display.set_mode((576, 700))
Clock = pygame.time.Clock()

running = True
game = Game()

while running and game.running:
    Clock.tick(30)
    events = pygame.event.get()
    extraevents = []
    for event in events:
        handled = False
        if event.type == pygame.QUIT:
            running = False
            handled = True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                stime = time.time()
                pygame.image.save(screen, "Screenshot_%d.png" % stime)
                print "Wrote Screenshot_%d.png" % stime
                handled = True
        
        if not handled:
            extraevents.append(event)
    
    game.handleEvents(extraevents)
    
    game.draw(screen)
    
    pygame.display.update()