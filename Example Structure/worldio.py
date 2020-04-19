import os, json

from consts import *
from gameEntities import *

WORLDSPATH = os.path.join('.','Levels')

def readWorld(name, World, gm=None):
    with open(os.path.join(WORLDSPATH,name,"world.json"),'r') as conf:
        options = json.loads(conf.read())
    
    world = World(options['size'],tuple(options['spawnpoint']),options['maxhistory'],options['maxlives'])
    
    emptychar = options.get("emptychar","-")
    solidchar = options.get("solidchar","&")

    if gm != None:
        gm.text = options.get("text",[])
        for ent in options["entities"]:
            if ent['type'] == "levelend":
                LevelFinish(gm,tuple(ent['pos']))
            elif ent['type'] == "switch":
                Switch(gm,tuple(ent['pos']),ent.get('target',None),ent['oneuse'],ent.get('targetposlist',None))
            elif ent['type'] == "triggerText":
                pos = ent.get('pos',None)
                if pos != None:
                    pos = tuple(pos)
                
                
                TriggerText(gm,ent['text'],ent.get("constant",False),pos, ent.get('newlife',-1))
    
    with open(os.path.join(WORLDSPATH,name,"grid.txt"),'r') as gridfile:
        for line in gridfile:
            if line.startswith("#"):
                continue
            
            lno,line = line.strip().split(':')
            y = int(lno)
            line = line.replace(' ','').replace(',','')
            for x,c in enumerate(line):
                if c == emptychar:
                    mat = MAT_EMPTY
                elif c == solidchar:
                    mat = MAT_SOLID
                elif c == "*":
                    print x,y
                    mat = MAT_SOLID
                    
                world.grid[x][y] = mat
    
    return world

def writeWorld(world):
    retstr = "#   "+"".join(str(i).ljust(20) for i in xrange(1+len(world.grid)/10))
    retstr += "\n#   "+" ".join(str(i%10) for i in xrange(len(world.grid))) +"\n"
    for y in xrange(len(world.grid)):
        lno = "%s: "%str(y).rjust(2)
        charlist = []
        for x in xrange(len(world.grid)):
            if world.grid[x][y] == MAT_SOLID:
                charlist.append("&")
            else:
                charlist.append("-")
        
        line = " ".join(charlist)
        
        retstr += lno+line+"\n"
    
    return retstr
            