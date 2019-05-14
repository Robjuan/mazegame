"""
these are the very base classes that all sceneobjects are built on.
in fact, sceneobjects are effectively a container for these, and the attribs of these
are rarely changed, more often it is the sobj that changes.

box is just that, label is plain or clickable text, textbox is an editable line of text.
there was a textarea (multi-line textbox) in beta, used in hangman, but no real use here.
and thus removed to prevent bloat
"""

import pygame
from pygame.locals import *

"""
 padding[0] = top
        [1] = left
        [2] = bottom
        [3] = right

 (just like CSS)
"""
def real_size (size, padding):
    return (size[0] + padding[1] + padding[3], size[1] + padding[0] + padding[2])

class Box(pygame.sprite.Sprite):
    def __init__ (self, size,color=(0,0,0), path=None,boxtype=-1,tile=False):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.color = color
        self.image = None
        self.path = path
        self.boxtype = boxtype
        self.update()
        if tile:
            self.tile()
    
    def update(self):
        if self.path:
            self.image = pygame.image.load(self.path)
            self.image.convert_alpha()
        elif self.image:
            self.image.fill(self.color)
        else:
            self.image = pygame.Surface(self.size,flags=SRCALPHA)
            self.image.fill(self.color)
        self.rect = self.image.get_rect()

    def tile(self):
        self.edgematches = [[],[],[],[]]
        """
        #edgematches[0] = topmatch
                    [1] = leftmatch
                    [2] = bottommatch
                    [3] = rightmatch
        """
        
class Label(pygame.sprite.Sprite):
    def __init__ (self, font, color, text):
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        self.font = font
        self.color = color
        self.image = None
        self.size = None
        self.update()
    
    def update(self):
        self.image = self.font.render(self.text, True, self.color)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
    
    def update_text(self, text):
        self.text = text
        self.update()
    
    def update_color(self, color):
        self.color = color
        self.update()
            
        self.image = pygame.Surface(self.size)
        
        
class Textbox(pygame.sprite.Group):
    def __init__(self, font, textcolor, bgcolor, disabledcolor, disabled=False, autosize=True, size=None, text="",padding=(0,0,0,0)):
        # first, create label
        pygame.sprite.Group.__init__ (self)
        self.font = font
        self.text = text
        self.fgcolor = textcolor
        self.bgcolor = bgcolor
        self.nocolor = disabledcolor
        
        self.disabled = disabled
        self.current_color = self.nocolor
        
        self.autosize = autosize
        self.padding = padding
        self.size = size       
        self.NUM_FRAMES_BLINK = 20
        self.frames_blink = self.NUM_FRAMES_BLINK
        self.blinking = False
        
        self.update()
    
    def swap_enabled(self):
        if self.disabled:
            return
        
        if self.current_color == self.nocolor:
            self.current_color = self.fgcolor
        else:
            self.current_color = self.nocolor
    
    def update_text(self, text):
        self.text = text
        self.update()
    
    def update_color(self, color):
        self.color = color
        self.update()
    
    def update(self):
        self.label = Label (self.font, self.current_color, self.text)
        
        if not self.blinking:
            self.label.text = self.text
            self.label.update()
        else:
            self.label.text = self.text + "|"
            self.label.update()
        
        self.empty()
        
        if self.autosize:
            self.size = self.label.image.get_size()
            
        # recreate background box
        if self.bgcolor != None:
            self.bg = Box (real_size(self.size, self.padding), self.bgcolor)
        
        self.label.rect.topleft = (self.padding[1], self.padding[0])
        
        # check to see if we should add it back because there is a bgcolor change
        if self.bgcolor != None:
            self.add (self.bg)
            
        self.add (self.label)
        
        self.create_image()
    
    def move_down (self, amount):
        for obj in self:
            x, y = obj.rect.topleft
            obj.rect.topleft = (x, y + amount)
            print "new topleft=", obj.rect.topleft
    
    def create_image(self):
        if len(self) > 1:
            self.image = pygame.Surface(self.bg.image.get_size())
            self.draw (self.image)
        else:
            self.image = self.label.image
        self.size = self.image.get_size()
    
    def blink_cursor(self):
        self.frames_blink -= 1
        if self.frames_blink == 0:
            self.blinking = not self.blinking
            self.frames_blink = self.NUM_FRAMES_BLINK
            self.update()
    
    def text_add (self, text):
        self.text += text
    
    def text_backspace (self):
        self.text = self.text[:-1]

