"""
gamescene.py
Provides a re-usable class to build levels of the game.
this is where the vast majority of the processing goes on.
this sets up all the objects that are handled by scenemanager for rendering,
and does all the truth-testing on players actions to make sure they follow the rules of the game.
"""
from math import sqrt
from pygame.locals import *
from scenebb import Scene

class GameScene(Scene):
    def __init__(self,game,level):
        Scene.__init__(self,game,setup=False)
        self.add_label("escape",(10,10),"Main Menu",self.textcolor,fontsize=20,
                         event=self.load_menu)
        #these are movement, both WASD and arrow keys work.
        self.add_keybind(K_d,lambda x:self.shift("right"))
        self.add_keybind(K_a,lambda x:self.shift("left"))
        self.add_keybind(K_w,lambda x:self.shift("up"))
        self.add_keybind(K_s,lambda x:self.shift("down"))

        self.add_keybind(K_UP,lambda x:self.shift("up"))
        self.add_keybind(K_LEFT,lambda x:self.shift("left"))
        self.add_keybind(K_DOWN,lambda x:self.shift("down"))
        self.add_keybind(K_RIGHT,lambda x:self.shift("right"))

        #this is to stop doing stuff when key released
        self.add_keyupbind(K_d,self.stop_hero)
        self.add_keyupbind(K_a,self.stop_hero)
        self.add_keyupbind(K_w,self.stop_hero)
        self.add_keyupbind(K_s,self.stop_hero)

        self.add_keyupbind(K_UP,self.stop_hero)
        self.add_keyupbind(K_LEFT,self.stop_hero)
        self.add_keyupbind(K_DOWN,self.stop_hero)
        self.add_keyupbind(K_RIGHT,self.stop_hero)

        self.add_keybind(K_SPACE,self.toggle_shift)
        #change between moving hero / tiles
        
        self.add_keybind(K_h,self.debug_fun)
        
        if self.herocolor:
        	self.herodispmode = "color"
       	elif self.heroimage:
       		self.herodispmode = "image"
        
    def load_level(self,level):
        tilemap = self.load_tiles(level)
        width = sqrt(len(tilemap))      
        #self.gridsize must be >= 3
        self.gridsize = int((480/width)/len(tilemap[1][1]) - ((1/width)*2))
        self.generate_tiles(tilemap,width)
        self.add_label("levelname",(10,40),str(self.levelname),self.titlecolor)
        self.speed = self.gridsize/8
        self.mode = 0 # 1/0 hero/tiles
        self.blipcount = 0 # frames in current blip_*
        self.heightdex = 0 # row of current tile
        self.acrossdex = 0 # column of current tile
        if self.heroimage:
            self.herodispmode = "image"
            self.herodex = self.current_tile.add_child(self.add_object("hero","image",(0,0),{"path":self.heroimage}),
                      (self.gridsize*2+(self.gridsize/2),self.gridsize*2+(self.gridsize/2)),layerup=1)
            self.objects["hero"].scale_self((self.gridsize/2,self.gridsize/2))
        else:
            self.herodispmode = "color"
            self.herodex = self.current_tile.add_child(self.add_object('hero',
                                              'box',(0,0),{"color":self.herocolor,
                                                           "visible":True,
                                                           "size":(self.gridsize/2,self.gridsize/2)})
                     ,(self.gridsize*2+(self.gridsize/2),self.gridsize*2+(self.gridsize/2)),layerup=1)
       
        self.toggle_shift() #start on hero, and blip him
        
    def tick_timer(self,event=None): #called every frame, if timer exists
        self.time+=1
        self.objects["timer"].obj.update_text("Time: "+str(self.time/60))
        
    def debug_fun(self,event=None):
        print "derpbugging, keybinds obviously active"
        print 'blipcount =',self.blipcount
        print 'render event =',self.hero.events["render"]
        
    def load_menu(self,event=None):
        pass #overwritten by children.
    def end_level(self,time):
        pass #overwritten by children.
    
    def toggle_shift(self,event):
        #mode 1 is hero, mode 0 is tiles
        if self.mode == 1:
            self.mode = 0
        elif self.mode == 0:
            self.mode = 1
        """
        essential for moving after crossing tile boundary
        finds the hero, updates the row/column co-ords of the tile
        """
        for row in self.gridlist:
            for tile in row:
                if tile:
                    for child in tile.children:
                        if child.name == "hero":
                            self.acrossdex = row.index(tile)
                            self.heightdex = self.gridlist.index(row)
                            return                  
                        
    def shift(self,direction): #allows one keybind for moving both
        if self.mode == 1:
            self.hero_move(direction)
        elif self.mode == 0:
            self.shift_tile(direction)

    @property
    def hero (self):
        return self.current_tile.children[self.herodex]

    @property
    def current_tile (self):
        return self.gridlist[self.heightdex][self.acrossdex]

    def stop_hero(self,event): #stops movement and collision checking
        if self.mode ==1:
            self.hero.velocity = (0,0)
            self.hero.events["render"] = None
            
    def hero_move(self,direction): #tells the hero to move, sets up collision checking
        if direction == "left":
            self.hero.velocity = (-self.speed,0)
        if direction == "right":
            self.hero.velocity = (self.speed,0)
        if direction == "up":
            self.hero.velocity = (0,-self.speed)
        if direction == "down":
            self.hero.velocity = (0,self.speed)
        self.hero.events["render"] = self.check_collide
        
    """
    boxtypes:
     0 = basic
     1 = top trigger
     2 = left trigger
     3 = bottom trigger
     4 = right trigger
     5 = door
    """
    def blip_hero(self): #makes hero inflate for a second,
                         #shows player what they're controlling
        if self.blipcount != 0: #every call in between first and 30th.
            self.blipcount+=1
        if self.blipcount == 0: #first call
            self.keybinds_active = False
            self.hero.scale_self((self.hero.size[0]*2,self.hero.size[1]*2))
            self.hero.obj.color = (179,255,179)
            self.hero.obj.update()
            self.blipcount+=1
        if self.blipcount == 15: #15 frames, 0.25s @ 60fps (locked to in gamebb.py)
            self.keybinds_active = True
            self.hero.scale_self((self.hero.size[0]/2,self.hero.size[1]/2))
            self.hero.obj.color = self.herocolor
            self.hero.obj.update()
            self.hero.events["render"] = None
            self.blipcount = 0

    def blip_tiles(self): #same as blip hero, but does edges of the tiles.
        if self.blipcount != 0: #same purpose, same implementation.
            self.blipcount+=1   #the render event is still stored in the hero.events["render"]
        if self.blipcount == 0: #because this means that the blip_hero and blip_tiles will 
            self.blipcount +=1  # never run concurrently. which would confuse the user.
            self.keybinds_active = False
            for tile in self.flattilelist:
                for child in tile.children:
                    if child.obj.boxtype == 1 or child.obj.boxtype == 2 or child.obj.boxtype == 3 or child.obj.boxtype == 4:
                        child.obj.color = (179,255,179)
                        child.obj.update()
        if self.blipcount == 15:
            self.keybinds_active = True
            for tile in self.flattilelist:
                for child in tile.children:
                    if child.obj.boxtype == 1 or child.obj.boxtype == 2 or child.obj.boxtype == 3 or child.obj.boxtype == 4:
                        child.obj.color = self.trigcolor
                        child.obj.update()
            self.hero.events["render"] = None
            self.blipcount = 0

    def check_collide(self,event=None):
        """
        ######################
        # COLLISION CHECKING #
        ######################
         basic order of function:
         1) get info about current location
         2) "move" hero to new location (haven't rendered yet)
         3) check if now hero is on top of any blocks
         4) if so, check what kind of block and do appropriate action
         4a) for regular blocks this is just stop.
         4b) for doors this is end the level
         4c) for edge triggers, this is check if there is a valid tile to move on to, and if it matches up
            and if it matches up, delete current hero, make new one in appropriate spot on new tile
         5) that's it.
        """
        oldx,oldy = self.hero.offset
        self.hero.offset = (oldx+self.hero.velocity[0],oldy+self.hero.velocity[1])
        diffx = self.hero.offset[0] - oldx
        diffy = self.hero.offset[1] - oldy
        #print 'veloc =',self.hero.velocity
        self.oldacross = self.acrossdex
        self.oldheight = self.heightdex 
        for child in self.current_tile.children:
            if child.name == "hero":
                continue
            elif self.hero.collide(child):
                #print 'colliding'
                tilemove = False
                self.hero.offset = (oldx,oldy)
                #print 'collision, old = (',oldx,',',oldy,') new = ',self.hero.offset
                if child.obj.boxtype == 5: #door
                    #print 'winning'
                    self.end_level(self.time)
                elif child.obj.boxtype == 0: #regular box
                    self.hero.offset = (self.hero.offset[0]-diffx,self.hero.offset[1]-diffy)
                    self.stop_hero(None)
                elif child.obj.boxtype == 4:#right trigger
                    self.hero.offset = (oldx-self.speed,oldy)
                    if not self.acrossdex+1 >= len(self.gridlist[self.heightdex]):
                        if self.gridlist[self.heightdex][self.acrossdex+1]:
                            if self.current_tile.obj.edgematches[3] == self.gridlist[self.heightdex][self.acrossdex+1].obj.edgematches[1]:
                                self.acrossdex += 1
                                tilemove = True
                                newoffset = (self.gridsize+self.speed,oldy)

                elif child.obj.boxtype == 2: #left trigger
                    self.hero.offset = (oldx+self.speed,oldy)
                    if not self.acrossdex-1 < 0:
                        if self.gridlist[self.heightdex][self.acrossdex-1]:
                            if self.current_tile.obj.edgematches[1] == self.gridlist[self.heightdex][self.acrossdex-1].obj.edgematches[3]:
                                self.acrossdex -= 1
                                tilemove = True
                                newoffset = (self.current_tile.size[0]-(self.gridsize*2),oldy)

                elif child.obj.boxtype == 1:#up trigger
                    self.hero.offset = (oldx,oldy+self.speed)
                    if not self.heightdex-1 < 0:
                        if self.gridlist[self.heightdex-1][self.acrossdex]:
                            if self.current_tile.obj.edgematches[0] == self.gridlist[self.heightdex-1][self.acrossdex].obj.edgematches[2]:
                                self.heightdex -= 1
                                tilemove = True
                                newoffset = (oldx,self.current_tile.size[1]-(self.gridsize*2))

                elif child.obj.boxtype == 3:#down trigger
                    self.hero.offset = (oldx,oldy-self.speed)
                    if not self.heightdex+1 >= len(self.gridlist):
                        if self.gridlist[self.heightdex+1][self.acrossdex]:
                            if self.current_tile.obj.edgematches[2] == self.gridlist[self.heightdex+1][self.acrossdex].obj.edgematches[0]:
                                self.heightdex += 1
                                tilemove = True
                                newoffset = (oldx,self.gridsize+self.speed)

                if tilemove:
                #if have hit edge trigger and have a tile to move on to.
                #print self.heightdex, self.acrossdex,"= index"
                    self.gridlist[self.oldheight][self.oldacross].remove_child_byindex(self.herodex)
                    if self.herodispmode == "image":
                        self.herodex = self.current_tile.add_child(self.add_object("hero","image",(0,0),{"path":self.heroimage}),
                                                                          newoffset,layerup=1)
                        self.objects["hero"].scale_self((self.gridsize/2,self.gridsize/2))
                    else:
                        self.herodex = self.current_tile.add_child(self.add_object('hero',
                                                          'box',(0,0),{"color":self.herocolor,
                                                                       "visible":True,
                                                                       "size":(self.gridsize/2,self.gridsize/2)})
                                                                          ,newoffset,layerup=1)
                    tilemove = False
                return
    
    def toggle_shift(self,event=None):
        """
        UPDATE DEX'S IN HERE
        this prevents the thingo erroring up when you move hero after moving tiles.
        finds the hero, and updates the current tile co-ords.
        without this, it would attempt to move the "hero" child on a tile that was
        no longer at the co-ords it had stored
        """
        for row in self.gridlist:
            for tile in row:
                if tile:
                    for child in tile.children:
                        if child.name == "hero":
                            self.acrossdex = row.index(tile)
                            self.heightdex = self.gridlist.index(row)
        #mode 1 is hero, mode 0 is tiles
        #blips inform user of what they're currently controlling.
        if self.mode == 1:
            self.stop_hero(None)
            self.hero.events["render"] = self.blip_tiles
            self.mode = 0
        elif self.mode == 0:
            self.hero.events["render"] = self.blip_hero
            self.mode = 1

        """               
        gridlist is a list of rows, then each row is a list of tiles
        so it's self.gridlist[row][tile], like list[y][x]
        2-dimensional array.
        """
    def check_space(self,direction,gridlist=None):
        if gridlist == None:
            gridlist = self.gridlist
        for tile in self.flattilelist:
            for row in gridlist:
                if row.count(tile) == 1: #if > 1, error plz, should never happen (means same sobj twice)
                    across = row.index(tile)
                    height = gridlist.index(row)
                    if direction == "right":
                        if across+1 >= len(row):
                            pass #at end                        
                        elif row[across+1]:
                            pass #something to the right
                        else:
                            newindex = across+1
                            return tile,(height,across),newindex
                    if direction == "left":
                        if across-1 < 0:
                            pass #at start
                        elif row[across-1]:
                            pass #something to the left
                        else:
                            newindex = across-1
                            return tile,(height,across),newindex
                    if direction == "up":
                        if height-1 < 0:
                            pass #top row
                        elif gridlist[height-1][across]:
                            pass #something above
                        else:
                            newheight = height-1
                            return tile,(height,across),newheight
                    if direction == "down":
                        if height+1 >= len(gridlist):
                            pass #bottom
                        elif gridlist[height+1][across]:
                            pass #something below
                        else:
                            newheight = height+1
                            return tile,(height,across),newheight
                        

    def shift_tile(self,direction):
        results = self.check_space(direction)
        if results: #if no results, then not moving
            tile = results[0]
            oldpos = results[1]
            newmove = results[2]
            """
            basically, will only have an arg if check_space is true and thus the movement is valid
            so, moves the tile in the appropriate direction by changing it's gridlist co-ords
            and replaces it's previous position with None, which will allow other tiles to move into that spot.            
            """
            if direction == "right":
                self.gridlist[oldpos[0]][newmove] = tile
                x = tile.pos[0] + tile.size[0] + self.gridsize/2
                y = tile.pos[1]               
            if direction == "left":
                self.gridlist[oldpos[0]][newmove] = tile
                x = tile.pos[0] - tile.size[0] - self.gridsize/2
                y = tile.pos[1]                
            if direction == "up":
                self.gridlist[newmove][oldpos[1]] = tile
                x = tile.pos[0]
                y = tile.pos[1] - tile.size[1] - self.gridsize/2                
            if direction == "down":
                self.gridlist[newmove][oldpos[1]] = tile
                x = tile.pos[0]
                y = tile.pos[1] + tile.size[1] + self.gridsize/2
                
            self.gridlist[oldpos[0]][oldpos[1]] = None
            tile.pos = (x,y)
            
    def load_tiles(self,file):
        """
         this is where we generate our tiles from our text file.
         sort of. This returns a 3-dimensional array, which is tiles>lines>icons.
         generate_tiles uses this.
         width and levelname are level-specific, and thus stored with the level layout
         comment is just to allow comments if i want.
         break is to signal when the tile ends.
        """
        f = open(file)
        tiles = []
        tile = []
        xlines = []
        yicons = []
        for line in f:
            line = line.strip()
            if "WIDTH" in line:
                #used to determine how many tiles wide grid will be
                word,self.width = line.split(" ")
                self.width = int(self.width)
            elif "LEVELNAME" in line:
                word,self.levelname = line.split(":")
            elif "COMMENT" not in line:
                #ie, if line with actual map
                for icon in line:
                    yicons.append(icon)
                xlines.append(yicons)
                yicons = []
        f.close()
        for line in xlines:
            if "BREAK" not in ''.join(line): # (occurs between tiles)
                tile.append(line)
            else:
                tiles.append(tile)
                tile = []
        return tiles
    """
    bitmap format (returned by load_tiles)
    list of tiles > list of lines > list of icons
    ie, "tile" is a list of lines, "line" is a list of icons
    """
    def generate_tiles(self,bitmap,width):
        """
        this is where we convert our bitmap of ascii characters into actual sceneobjects
        this is required so that scenemanager can render, move, update, scale, whatever them.
        however, the objects must be made in accordance with the list.
        thus, for each "tile" (1st level of lists), a tile parent object is made. This parent-child functionality
        of libscene allows us to update the parent and the children automatically follow.
        edgematches are generated here, simply a list of icons for edge comparisons.
        the different symbols represent different kinds of blocks.
        the T and M are used only for the big images on the first tutorial level, to intergrate them into the game
        rather than have a separate text wall or some such.
        """
        tilexpos = self.gridsize
        tileypos = 100+self.gridsize # gives space for title etc
        xoffset = -self.gridsize # to make 0 for first tile
        yoffset = 0

        tcount = 0
        count = 0

        self.flattilelist = []
        rowlist = []
        self.gridlist = []

        for tile in bitmap:
            if tile != []:
                tcount +=1
                # add a tile, this will be the parent
                tilerect = self.add_object('t'+str(tcount),"tile",(tilexpos,tileypos),
                                               {"color":self.trackcolor,
                                                "visible":True,
                                                "size":(len(tile[0])*self.gridsize,len(tile)*self.gridsize)})
                self.flattilelist.append(tilerect)
                rowlist.append(tilerect)
                # generate edgematches, for moving between tiles
                tilerect.obj.edgematches[0].append(tile[1])
                tilerect.obj.edgematches[2].append(tile[-2])
                for row in tile:
                    tilerect.obj.edgematches[1].append(row[1])
                    tilerect.obj.edgematches[3].append(row[-2])
                    for icon in row:
                        colour = self.trigcolor # (edge trigger colour)
                        count +=1
                        xoffset+=self.gridsize
                        if icon == "#": #basic block
                            boxtype = 0
                            colour = self.wallcolor
                        elif icon == "$": #top trigger
                            boxtype = 1
                        elif icon == "%": #left trigger
                            boxtype = 2
                        elif icon == "&": #bottom trigger
                            boxtype = 3
                        elif icon == "@": #right
                            boxtype = 4
                        elif icon == "-":
                            continue #dont create box in empty space
                        elif icon == "D": # door
                            boxtype = 5
                            colour = self.trackcolor
                            star = tilerect.add_child(self.add_object("win","image",(0,0),
                                {"path":"resource/images/winstar.png","boxtype":boxtype}),
                                (xoffset,yoffset),layerup=1)
                            tilerect.children[star].scale_self((self.gridsize,self.gridsize))
                            continue
                        elif icon == "T":  #only used in tut one for controls (toggle)
                            tilerect.add_child(self.add_object("toggle","image",(0,0),
                                {"path":"resource/images/togglekey.png"}),
                                (xoffset,yoffset),layerup=1)
                            continue
                        elif icon == "M":  #only used in tut one for controls (movement)
                            tilerect.add_child(self.add_object("move","image",(0,0),
                            {"path":"resource/images/movekeys.png"}),
                            (xoffset,yoffset),layerup=1)
                            continue
                        #after defining attribs based on icon, box made and is a child of the tile
                        tilerect.add_child(self.add_object(count,'box',
                                                         (0,0),
                                                         {"color":colour,
                                                          "visible":True,
                                                          "size":(self.gridsize,self.gridsize),
                                                          "boxtype":boxtype}),
                                                                   (xoffset,yoffset))

                   #this is shifting position after each box.
                    xoffset=-self.gridsize
                    yoffset+=self.gridsize
                xoffset=-self.gridsize
                yoffset=0
                # this detects when we've reached the desired end of the row (of tiles),
                # and then starts a new row.
                if tcount%width == 0:
                    tilexpos = self.gridsize
                    tileypos += tilerect.size[1] + self.gridsize/2                    
                    self.gridlist.append(rowlist)
                    rowlist = []
                else:
                    tilexpos += tilerect.size[0] + self.gridsize/2
        
        self.gridlist.append(rowlist) #catch last line after all tiles added
        for line in self.gridlist:    #put None in empty spaces on the gridlist
            if len(line) < width:
                add = int(width - len(line))
                for i in xrange(0,add):
                    line.append(None)

        for tile in self.flattilelist:
            for edgematch in tile.obj.edgematches:
                edgematch = edgematch[1:-2] #remove first+last (edge triggers)

        
        #print 'num tiles = ',len(self.flattilelist)
        #print self.gridlist
