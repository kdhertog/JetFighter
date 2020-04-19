'''
This is the main file used for running the game


'''
# pylint: disable=

#--- Imports
import pygame

import constants as cts
import game


#--- Initialisation
pygame.init()       #Initialize pygame           # pylint: disable=maybe-no-member

screen = pygame.display.set_mode((cts.screenwidth, cts.screenheight)) #Initialise the game screen
clock = pygame.time.Clock() #Initialise clock

game = game.Game()

#--- Main loop
running = True
while running:

    events = pygame.event.get() #Get events
    gameEvents = []

    for event in events:
        
        if event.type == pygame.QUIT:   #Quitting the game              # pylint: disable=maybe-no-member
            running = False

        # Add other events that are separate from the game, i.e. making screenshots

        else:
            gameEvents.append(event)

    game.handleEvents(gameEvents) #Let the game class handle events         # pylint: disable=too-many-function-args
    
    game.draw(screen) #Game class function that draws new situation to screen         # pylint: disable=too-many-function-args
    
    game.update() #Update screen to display
