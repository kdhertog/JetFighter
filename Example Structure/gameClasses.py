import pygame
import pygame.gfxdraw
from consts import *
from worldio import *
from textrect import render_textrect

class World(object):
    def __init__(self,gsize,sp,mh,ml):
        self.gridsize = gsize #Avaliable sizes: 1, 2, 3, 4, 6, 8, 9, 12, 16, 18, 24, 32, 36, 48, 64, 72, 96, 144, 192, 288
        self.spawnpoint = sp
        self.grid = []
        for i in xrange(576/gsize):
            self.grid.append([0]*(576/gsize))
        
        self.maxhistory = mh
        self.ticks = 0
        self.maxlives = ml
    
    def isOpen(self,x,y):
        if x < 0 or x >= len(self.grid) or y < 0 or y >= len(self.grid):
            return False
            
        if self.grid[x][y] == MAT_EMPTY:
            return True
        else:
            return False
    
    def draw(self,surf):
        for x in xrange(len(self.grid)):
            for y in xrange(len(self.grid)):
                if self.grid[x][y] == MAT_SOLID:
                    col = COL_SOLID
                elif self.grid[x][y] == MAT_EMPTY:
                    col = COL_EMPTY
                pygame.draw.rect(surf,col,((x*self.gridsize,y*self.gridsize),(self.gridsize,self.gridsize)))
        
    def tick(self):
        self.ticks += 1
        
        
class Player(object):
    def __init__(self, world, gamemanager, generation=0):
        self.world = world
        self.curpos = world.spawnpoint
        self.history = [self.curpos]
        self.maxhistory = self.world.maxhistory
        self.isShadow = False
        self.gm = gamemanager
        self.generation = generation
    
    def move(self,d):
        if d != D_NONE:
            nx,ny = self.curpos
            if d == D_UP or d == D_DOWN:
                ny += (d/abs(d))
            elif d == D_RIGHT or d == D_LEFT:
                nx += (d/abs(d))
        
        if d != D_NONE and not self.world.isOpen(nx,ny):
            return False
        else:
            if d != D_NONE:
                self.curpos = (nx,ny)
            
                self.gm.eventManager.call("plrmove",(self,not self.isShadow))
    
            if not self.isShadow:
                self.history.append(d)
                if self.maxhistory != -1 and len(self.history)-1 == self.maxhistory:
                    self.isShadow = True
                
                return True
    
    def draw(self,surf,iscurrent):
        if iscurrent:
            col = COL_PLAYER
        else:
            alpha = 255 - max(30*((self.world.ticks/self.maxhistory) - self.generation),30)
            col = list(COL_PLAYER) + [alpha]
            
        gs = self.world.gridsize
        
        if iscurrent:
            pygame.draw.circle(surf,col,getCenterOfSquare(self.curpos,gs),gs/2)
        else:
            pygame.draw.circle(surf,col,getCenterOfSquare(self.curpos,gs),int(gs/3))
    
    def seek(self, i):
        i = min(len(self.history)-1,max(0,i)) #Constrain
        move = self.history[i]
        if type(move) == tuple:
            self.curpos = move
            self.gm.eventManager.call("plrmove",(self,self==self.gm.curplr))
        else:
            self.move(self.history[i])
            
    def sync(self):
        if self.isShadow:
            localtick = self.world.ticks%self.maxhistory
            self.seek(localtick)

class GameEventManager(object):
    def __init__(self):
        self.eventcallbacks = {}
    
    def call(self, evt, args):
        if evt not in self.eventcallbacks:
            return
            
        for callback in self.eventcallbacks.get(evt,[]):
            callback(*args)
    
    def registerCallback(self, evt, callback):
        if evt not in self.eventcallbacks:
            self.eventcallbacks[evt] = []
        
        self.eventcallbacks[evt].append(callback)
    
    def clearCallbacks(self):
        self.eventcallbacks = {}

class GameManager(object):
    def __init__(self,game,levels,buttonfont):
        self.game = game
        self.surf = pygame.Surface((576, 576),pygame.SRCALPHA)
        self.text = []
        self.eventManager = GameEventManager()
        
        self.levels = levels
        self.worldindex = 0
        
        self.loadLevel()
        
        self.deathflash = 0
        self.deathflashinc = 25
        self.deathflashstate = 0
        
        self.newWorld = False
        
        self.resetbutton = pygame.Rect((476,546),(100,30))
        self.resetbutton_surf = pygame.Surface(self.resetbutton.size)
        self.resetbutton_surf.fill(COL_BLEVELRESET)
        pygame.draw.rect(self.resetbutton_surf,(0,0,0),((0,0),(100,30)),5)
        text = buttonfont.render("Reset",1,(0,0,0))
        x = 50-text.get_rect().centerx
        y = 15-text.get_rect().centery
        self.resetbutton_surf.blit(text,(x,y))
    
    def click(self,pos):
        if self.resetbutton.collidepoint(pos):
            self.loadLevel()
    
    def move(self,dir):
        if self.deathflashstate:
            return False
            
        move_succeeded = self.curplr.move(dir) 
        if not move_succeeded:
            return False
        
        if self.newWorld:
            self.newWorld = False
            return
            
        self.curworld.tick()
        
        
        if self.curplr.isShadow:
            oldgen = self.curplr.generation
            if oldgen + 1 == self.curworld.maxlives:
                self.loadLevel(setNewWorld=False)
                return
            
            self.eventManager.call("newlife",(oldgen+1,))
            self.curplr = Player(self.curworld, self,oldgen+1)
            self.players.append(self.curplr)
    
        for plr in self.players:
            plr.sync()
        
        self.eventManager.call("tickdone",(self.curworld,))
        return True
    
    def loadLevel(self, next=False, flash=True, setNewWorld=True):
        self.deathflash = 0
        self.deathflashstate = 1
        
        if next:
            self.worldindex += 1
            
        try:
            level = self.levels[self.worldindex]
        except IndexError:
            self.game.wingame()
            return
        
        self.eventManager.clearCallbacks()
        self.curworld = readWorld(level,World,self)
        self.curplr = Player(self.curworld,self)
        self.players = [self.curplr]
        
        self.newWorld = setNewWorld
        
    def draw(self):
        self.surf.fill((0,0,0))
        self.curworld.draw(self.surf)
        self.eventManager.call("draw",(self.surf,))
        self.curplr.draw(self.surf,True)
        for plr in self.players:
            if plr is self.curplr:
                continue
            plr.draw(self.surf,False)
        
        if self.deathflashstate:
            self.deathflash += self.deathflashinc*self.deathflashstate
            if self.deathflash <= 20 and self.deathflashstate == -1:
                self.deathflashstate = 0
            elif self.deathflash >= 230:
                self.deathflashstate = -1
            
            self.surf.fill((0,0,0,self.deathflash))
        
        self.surf.blit(self.resetbutton_surf,self.resetbutton)
        
    def winlevel(self):
        self.game.winlevel(self.levels[self.worldindex])
        self.loadLevel(True)

class Game(object):
    def __init__(self):
        self.running = True
        self.mainfont = pygame.font.SysFont("Arial", 16)
        self.dayfont = pygame.font.Font(os.path.join(".","Media","ConsolaMono","ConsolaMono-Bold.ttf"), 18)
        self.menufont = pygame.font.Font(os.path.join(".","Media","ConsolaMono","ConsolaMono-Bold.ttf"), 20)
        self.titlefont = pygame.font.Font(os.path.join(".","Media","Grundschrift.ttf"), 68)
        self.view = VIEW_MAINMENU
        self.gm = None
        self.mainmenu_buttons = {
                                 "play":pygame.rect.Rect((100,350),(150,70)),
                                 "reset":pygame.rect.Rect((330,430),(150,70)),
                                 "quit":pygame.rect.Rect((155,510),(150,70)),
                                }
        
        with open(os.path.join(".","Levels","levelset.txt"),'r') as f:
            self.alllevels = [l.strip() for l in f.readlines()]
        
        try:
            with open(os.path.join(".","Levels","progress.txt"),'r') as f: #I could get a better place for this...
                self.completedlevels = [l.strip() for l in f.readlines()]
        except:
            self.clearprogress()
        
        if self.completedlevels == self.alllevels:
            self.clearprogress()
        
        
        titletopper = pygame.Surface((576,140))
        titletopper.fill(COL_MENUBG)
        pygame.draw.rect(titletopper,COL_TTOPPER,((0,0),(144,80)))
        pygame.draw.rect(titletopper,COL_TTOPPER,((144,0),(144,120)))
        pygame.draw.rect(titletopper,COL_TTOPPER,((288,0),(144,95)))
        pygame.draw.rect(titletopper,COL_TTOPPER,((432,0),(144,140)))
        
        self.rendered_cache = {
                              'livesleft':self.dayfont.render("Echoes Left: ",1,COL_TEXT),
                              'title': [ self.titlefont.render("Before ",1,COL_TEXT),self.titlefont.render("Night ",1,COL_TEXT),self.titlefont.render("Falls",1,COL_TEXT) ],
                              'titletopper': titletopper
                              }
        
        
        self.sounds = {
                       "levelwin":pygame.mixer.Sound(os.path.join('Media','levelwin.ogg')),
                       "switch":pygame.mixer.Sound(os.path.join('Media','switch.ogg')),
                       "triggertext":pygame.mixer.Sound(os.path.join('Media','trigger.ogg'))
                      }
    
    def handleEvents(self, events):
        for event in events:
            if self.view == VIEW_MAINMENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for b in self.mainmenu_buttons:
                        if self.mainmenu_buttons[b].collidepoint(event.pos):
                            self.menuButton(b)
                            
            elif self.view == VIEW_END:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    self.view = VIEW_MAINMENU
                            
            elif self.view == VIEW_GAME:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.gm.click(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.view = VIEW_MAINMENU
                    elif event.key == pygame.K_UP:
                        self.gm.move(D_UP)
                    elif event.key == pygame.K_DOWN:
                        self.gm.move(D_DOWN)
                    elif event.key == pygame.K_RIGHT:
                        self.gm.move(D_RIGHT)
                    elif event.key == pygame.K_LEFT:
                        self.gm.move(D_LEFT)
                    elif event.key == pygame.K_SPACE:
                        self.gm.move(D_NONE)
    
    def startgame(self,levels):
        levels = [x for x in self.alllevels if x not in self.completedlevels]
        self.view = VIEW_GAME
        self.gm = GameManager(self,levels,self.dayfont)
    
    def winlevel(self,level):
        self.completedlevels.append(level)
        with open(os.path.join(".","Levels","progress.txt"),'w') as f:
            f.write("\n".join(self.completedlevels))
        self.sounds['levelwin'].play()
    
    def wingame(self):
        self.view = VIEW_END
        f = open(os.path.join(".","Levels","progress.txt"),'w')
        f.close()
    
    def clearprogress(self):
        f = open(os.path.join(".","Levels","progress.txt"),'w')
        f.close()
        self.completedlevels = []
    
    def menuButton(self,button):
        if button == "play":
            self.startgame(['First','Second','Third','Fourth'])
        if button == "reset":
            self.clearprogress()
        if button == "quit":
            self.running = False
        
    def draw(self, surf):
        if self.view == VIEW_MAINMENU:
            surf.fill(COL_MENUBG)
            for button in self.mainmenu_buttons:
                col = COL_BPLAY #Default
                text = button
                if button == "play":
                    col = COL_BPLAY
                    text = "Play!"
                elif button == "reset":
                    col = COL_BRESET
                    text = "Reset\nProgress"
                elif button == "quit":
                    col = COL_BQUIT
                    text = "Quit Game"
                
                pygame.draw.rect(surf,col,self.mainmenu_buttons[button])
                pygame.draw.rect(surf,(255,255,255),self.mainmenu_buttons[button].inflate(3,3),3)
                pygame.draw.rect(surf,(255,255,255),self.mainmenu_buttons[button].inflate(-8,-8),1)
                
                tsurf = render_textrect(text,self.menufont,self.mainmenu_buttons[button].inflate(-10,-10), COL_BTEXT, (0,0,0,0),1)
                surf.blit(tsurf,self.mainmenu_buttons[button])
            
            
            prog = self.menufont.render("Progress: %d out of %d levels"%(len(self.completedlevels),len(self.alllevels)),1,COL_TEXT)
            surf.blit(prog,(50,650))
            
            surf.blit(self.rendered_cache['titletopper'],(0,0))
            
            xoffset = 576/2 - sum([i.get_width() for i in self.rendered_cache['title']])/2
            for i,s in enumerate(self.rendered_cache['title']):
                surf.blit(s,(xoffset,150+(i*40)))
                xoffset += s.get_width()
            
        
        elif self.view == VIEW_END:
            surf.fill(COL_MENUBG)
            tsurf = render_textrect("You won!\nProgress has been reset.\nPress any key to continue back to the main menu.",self.menufont,surf.get_rect().inflate(-100,-100), COL_BTEXT, (0,0,0,0),1)
            surf.blit(tsurf,surf.get_rect())
            
        elif self.view == VIEW_GAME:
            gm = self.gm
            surf.fill(COL_BG)
            gm.draw()
            surf.blit(gm.surf,(0,0))
    
            for i,line in enumerate(gm.text):
                yoffset = i*self.mainfont.get_height()
                surf.blit(self.mainfont.render(line, 0, COL_TEXT),(10,590+yoffset))
    
            if gm.curworld.maxhistory != -1:
                hourleft = gm.curworld.maxhistory-gm.curworld.ticks%gm.curworld.maxhistory -1
                surf.blit(self.dayfont.render("Hours Left: %d"%hourleft,1,COL_TEXT),(10,10))
            if gm.curworld.maxlives > 0:
                livesleft = gm.curworld.maxlives - gm.curplr.generation-1
                surf.blit(self.rendered_cache['livesleft'],(10,25))
                x = 10+self.rendered_cache['livesleft'].get_width()
                y = 25+ self.dayfont.get_ascent()/2 + 6
                for i in xrange(livesleft):
                    pygame.draw.circle(surf,COL_PLAYER,(x+(i*13),y),6)