"""
 scene.py
 Allows for the creation of Scenes and SceneObjects for use with SceneManager.
 This is where the wrappers for the basic objects are made, and this is what SceneManager
 deals with for the most part.
"""

import pygame
from pygame.locals import *

import guibb

"""
Contains information about the object to be rendered.
Used for SceneManager.
"""
class SceneObject():
    def __init__ (self, name, pos, visible, obj, layer=0, events = {}, velocity = (0,0)):
        self.name = name
        self.pos = pos
        self.visible = visible
        self.obj = obj
        self.layer = layer
        self.events = events
        self.child_list = []
        self.velocity = velocity

    @property
    def surface (self):
        if type(self.obj) != pygame.Surface:
            return self.obj.image
        else:
            return self.obj
          
    def scale_self(self,newres):
        xsize,ysize = self.size
        ratio = 1
        if newres[0] == -1 or newres[1] == -1: # allows for scaling of whole 
            if newres[0] == -1:                 # image to fit desired x or y
                ratio = newres[1]/float(self.size[1])
            elif newres[1] == -1:
                ratio = newres[0]/float(self.size[0])
            xsize = self.size[0]*ratio
            ysize = self.size[1]*ratio
        else:
            xsize = newres[0]
            ysize = newres[1]

        #print 'final size=(',xsize,',',ysize,')'
        self.surface = pygame.transform.scale(self.surface,(xsize,ysize))

    def touches (self, pos): #checks if a point is inside the bounds of an obj.
        mx, my = pos
        ox, oy = self.pos
        width, height = self.size
        return mx >= ox and mx <= (ox + width) and my >= oy and my <= (oy + height)


    def collide(self,sobj): #checks if two objects overlap at all
        mx, my = sobj.pos
        ox, oy = self.pos

        mw, mh = sobj.size
        ow, oh = self.size

        collidex = False
        collidey = False

        for m in xrange(mx,(mx+mw)):     #for each point on width of thing
            if m > ox and m < (ox+ow): # does it overlap?
                collidex = True

        for m in xrange(my,(my+mh)):
            if m > oy and m < (oy+oh):
                collidey = True

        if collidex and collidey:
            return True
        else:
            return False
            
    @property
    def size (self):
        return self.surface.get_size()

    def add_child(self,obj,offset,scale=1,layerup=0): #this is where we add objects as children
        obj.offset = offset                            #the advantage of this is that they are updated
        obj.scale = scale                              #with the parent, simplfying moving groups.

        obj.layer = self.layer + layerup + 1 #always above parent, layerup allows above other kids

        x = self.pos[0] + offset[0]
        y = self.pos[1] + offset[1]
        obj.pos = (x,y)
        if scale != 1: #scale of parent (untested)
            obj.scale_self(self.size[0]*scale,self.size[1]*scale)

        self.child_list.append(obj)
        return self.child_list.index(obj)

    @property
    def children(self):
        return self.child_list

    @property
    def has_children(self):
        if self.child_list != []:
            return True
        else:
            return False

    def update_children(self):  #called each frame, moves kids in accordance with parent.
        for child in self.child_list:
            x = self.pos[0] + child.offset[0]
            y = self.pos[1] + child.offset[1]
            child.pos = (x,y)
            if child.scale != 1: #(untested)
                child.scale_self((self.size[0]*child.scale,self.size[1]*child.scale))
    
    def remove_all_children(self):
        self.child_list = []

    def remove_child(self,child):
        if child in self.child_list: 
            self.child_list.remove(child)
        else:
            print child,"does not exist in child_list"

    def remove_child_byindex(self,childex):
        if len(self.child_list) >= (childex-1):
            self.child_list.pop(childex)
        else:
            print childex,"is not a valid child index"

    def __str__(self):
        return str("SceneObject %s @ (%d,%d), layer %d" % (self.name, self.pos[0], self.pos[1], self.layer))

class Scene:
    """
    this contains all the information sceneman needs to rander objects.
    some of it is pulled from theme_man.
    """
    def __init__ (self, game, setup=True, prev_scene=None,keybinds_active=True,theme_man=None):
        self.objects = {}
        self.keybinds = []
        self.keybinds_active = keybinds_active
        self.game = game
        self.prev_scene = prev_scene
        
        #XXX: ideally, should not access game from inside libscene
        self.textcolor = self.game.theme_man.themedict["TextColor"]
        self.titlecolor = self.game.theme_man.themedict["TitleColor"]
        self.wallcolor = self.game.theme_man.themedict["WallColor"]
        self.trackcolor = self.game.theme_man.themedict["TrackColor"]
        self.herocolor = self.game.theme_man.themedict["HeroColor"]
        self.heroimage = self.game.theme_man.themedict["HeroImage"]
        self.trigcolor = self.game.theme_man.themedict["TrigColor"]
        self.heroimage = self.game.theme_man.themedict["HeroImage"]
        if setup:
            self.load_scene()
        
    def load_scene (self):
        # This function should be overwritten by children.
        pass
        
    """
    SUPER FUNCTION
    this function is the big boss.
    it creates objects from thin air (and also the gui base classes and passed params)
    as you can see by the ludicrous number of available params below, it is incredibly flexible
    and can be used to create just about anything.
    not only that, due to it's using the gui base as it's main base of objects, it's very simple to
    expand, simply create a new class and a new objtype here, and you're away.
    """
    def add_object (self, name, objtype, pos, params, events=None):
        color = (0, 0, 0)
        #bg_color = (255, 255, 255)
        bg_color = None
        no_color = (123, 123, 123)
        visible = True
        obj = None
        onclick = None
        size = (0, 0)
        layer = 0
        padding = (5, 5, 5, 5)
        velocity = (0,0)
        boxtype = -1
        
        text = ""
        font_size = 16
        font_face = None
        font_file = None

        if events is None:
            events = {}
       
        if params.has_key("visible"):
            visible = params["visible"]
        
        if params.has_key("size"):
            size = params["size"]

        if params.has_key ("color"):
            color = params["color"]
        
        # fgcolor is an alias of color
        if params.has_key ("fgcolor"):
            color = params["fgcolor"]

        if params.has_key ("layer"):
            layer = params["layer"]
        
        if params.has_key ("text"):
            text = params["text"]
        
        if params.has_key ("fontsize"):
            font_size = params["fontsize"]
        
        if params.has_key ("fontface"):
            font_face = params["fontface"]
            
        if params.has_key ("fontfile"):
            font_file = params["fontfile"]
        
        if params.has_key ("bgcolor"):
            bg_color = params["bgcolor"]
        
        if params.has_key ("nocolor"):
            no_color = params["nocolor"]
        
        if params.has_key ("padding"):
            padding = params["padding"]

        if params.has_key ("velocity"):
            velocity = params["velocity"]

        if params.has_key ("boxtype"):
            boxtype = params["boxtype"]

        if objtype == "background":
            if params.has_key("path"):
                obj = pygame.image.load(params["path"]).convert()
            else:
                obj = pygame.Surface(self.game.screen.get_size())
                obj.fill(color)
            #obj.type = "background"

        elif objtype == "box":
            obj = guibb.Box(size,color,boxtype=boxtype)
            
        elif objtype == "tile":
            obj = guibb.Box(size,color,tile=True)
                            
        elif objtype == "image":
            obj = guibb.Box((0,0), color, path=params["path"],boxtype=boxtype)
        
        elif objtype == "textbox":
            if font_file is not None:
                font_face = font_file
            elif font_face is not None:
                font_face = pygame.font.match_font(font_face)
                
            obj = guibb.Textbox (pygame.font.Font(font_face, font_size), color, bg_color, no_color, padding=padding, text=text)
        
        elif objtype == "label":
            if font_file is not None:
                font_face = font_file
            elif font_face is not None:
                font_face = pygame.font.match_font(font_face)
            
            obj = guibb.Label (pygame.font.Font(font_face, font_size), color, text)
            
        else:
            raise TypeError("no such scene object type %s" % repr(objtype))

        newobj = SceneObject (name, pos, visible, obj, layer, events, velocity)
        self.objects[name] = newobj
        return newobj
    
    """
    This here is a whole heap of helper functions, things that are called a lot.
    qutting the scene, going to a new scene, having a background or some text
    also makes it pretty when you go <print sceneobject>
    """
    
    def add_escape_keybind (self):
        self.add_keybind (K_ESCAPE, lambda x: self.game.quit())
        
    def add_prevscene_keybind (self):
        self.add_keybind (K_ESCAPE, self.load_prev_scene)
    
    def load_prev_scene (self, *kargs):
        print "[scene.py] going to scene", self.prev_scene
        self.game.load_scene (self.prev_scene)
        
    def load_next_scene (self, newscene):
        newscene.prev_scene = self
        print "[scene.py] going to scene", newscene
        self.game.load_scene (newscene)

    def add_keybind (self, key, event):
        self.keybinds.append ((key, event, True))

    def add_keyupbind (self, key, event):
        self.keybinds.append ((key, event, False))

    def add_background (self, path, layer=-1):
        """
        Helper function that adds a background object to the scene object stack.
        """
        self.add_object ("background", "background", (0, 0), { "path": path, "layer": layer })

    def add_image (self, name, pos, path, event=None):
        """
        Helper function for easily adding images with a click event.
        """
        self.add_object (name, "image", pos, {"path": path}, {"click": event})

    def set_focus (self,obj):
        #xxx: should not access scene_man from scene.
        self.game.scene_man.set_focus(obj, None)
        
    def add_label (self,name,pos,text,color,font="resource/expressway.ttf",fontsize=48,event=None,visible=True):
        """
        Helper function for adding labels.
        """
        self.add_object(name,"label",pos,{
            "text":text,
            "color":color,
            "fontfile":font,
            "fontsize":fontsize,
            "visible":visible
            },{"click":event})

    def __str__ (self):
        return "%s with %d objects" % (self.__class__.__name__, len(self.objects))
