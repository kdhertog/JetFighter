'''
This file contains the game class. This is the highest level class, used for

'''

import pygame

import constants as cts

class Game():

    def __init__(self):
        self.view = "main_menu"
    
    def handleEvents(self,events):
        handle = 13
    
    def draw(self,surf):
        #if self.view == "main_menu":    
        #surf.fill(cts.col_menubg)
        draw = 12

    def update(self):
        pygame.display.update()
    