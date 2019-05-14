"""
 scenemanager.py
 Provides a simple API to have pygame and GUI objects attached to a 'scene',
 which can easily be rendered. It means that once an object is created inside a scene, scene_man
 will look at it each frame and decide to render it or not, depending on sobj.visible, and then
 act upon it as required. It also accesses pygame's event queue, and uses that to fire keybinds
 and mouse clicks.
"""

import pygame
import guibb

#events. These allow us to access information about the event when it is called in an instance of scene.
class Event():
    pass
    
class BlurEvent(Event):
    def __init__ (self, target):
        self.target = target

class MouseDownEvent(Event):
    def __init__ (self, target, x, y):
        self.target = target
        self.x = x
        self.y = y

class MouseHoverEvent(MouseDownEvent):
    pass

class KeyDownEvent(Event):
    def __init__ (self, target, key):
        self.target = target
        self.key = key

class KeyUpEvent(Event):
    def __init__ (self, target, key):
        self.target = target
        self.key = key

class TextSubmitEvent(Event):
    def __init__ (self, target, text):
        self.target = target
        self.text = text

class SceneManager():
    def __init__(self, screen, scene=None):
        self.screen = screen
        self.current_scene = scene
        self.current_focus = None
        self.last_focus = None
        self.current_hover = None
    #the render function. Called once a frame by the top level loop (gamebb.py)
    def render(self):
        """
        Blits all objects in the scene to the screen, ordered by layer.
        """
        # order by layer, and loop
        for sobj in sorted(self.get_objects(),key=lambda sasha:sasha.layer):
            # blit only visible objects
            if sobj.visible:
                if sobj.events.has_key("render") and sobj.events["render"] is not None:
                    sobj.events["render"]()
                if sobj.has_children:
                    sobj.update_children()
                if (type(sobj.obj) == guibb.Textbox) and self.current_focus is not None:
                    sobj.obj.blink_cursor()
                self.screen.blit (sobj.surface, sobj.pos)
                    
    def get_objects(self):
        """
        Returns all the objects in the scene as an array.
        """
        return self.current_scene.objects.values()
            
    def get_binds(self):
        return self.current_scene.keybinds
        
    #this is also called once per frame.
    #it looks at the event queue and acts accordingly.
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
         
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.last_focus = self.current_focus
                self.current_focus = None
                
                # see if we've clicked into anything
                mpos = pygame.mouse.get_pos()
                mx, my = mpos
                for sobj in self.get_objects():
                    if sobj.touches (mpos):
                        # and fire the object's event
                        if sobj.events.has_key ("click") and sobj.events["click"] is not None and sobj.visible:
                            sobj.events["click"](MouseDownEvent(sobj, mx, my))
                                                # work out if we're in a textbox
                        if (type(sobj.obj) == guibb.Textbox) and not sobj.obj.disabled:
                            self.set_focus (sobj, (mx, my))
                                        
            # See if we've lost focus from textbox, if so, change back color thing
            self._swap_last_focused()
            
            if event.type == pygame.MOUSEMOTION:
                # find out what lives at the current (x, y)
                mpos = pygame.mouse.get_pos()
                mx, my = mpos
                hover_set_already = False
                
                for sobj in self.get_objects():
                    if sobj.touches (mpos):
                        # see if we're touching our last hover object
                        if self.current_hover is not None and not self.current_hover.touches (mpos):
                            # tell the old object we are no longer hovering
                            if self.current_hover.events.has_key("hover_off") and self.current_hover.events["hover_off"] is not None and sobj.visible:
                                self.current_hover.events["hover_off"](MouseHoverEvent (self.current_hover, mx, my))
                                self.current_hover = None
                        
                        if hover_set_already:
                            continue
                        
                        #don't want to count hovering on background as event
                        if not sobj.name == "background":
                            self.current_hover = sobj
                            hover_set_already = True
                        
                        #can't fire hover_on for invis objs, would be too confusing
                        if sobj.events.has_key ("hover_on") and sobj.events["hover_on"] is not None and sobj.visible:
                            sobj.events["hover_on"](MouseHoverEvent (sobj, mx, my))

            textchanged = False
            if event.type == pygame.KEYDOWN:
                # see if we have any textboxes that need attenting to
                if self.current_focus is not None:
                    #binds for enterting text into a textbox
                    if event.key == pygame.K_BACKSPACE:
                        self.current_focus.obj.text_backspace()
                        textchanged = True
                    elif event.key == pygame.K_DELETE:
                        self.current_focus.obj.text_delete()
                        textchanged = True
                        
                    elif event.key == pygame.K_RETURN:                      
                        if self.current_focus.events.has_key('submit') and self.current_focus.events["submit"] != None:
                            retval = self.current_focus.events["submit"](TextSubmitEvent(self.current_focus, self.current_focus.obj.text))
                            if retval is True:
                                self._lose_current_focus()
                    
                    elif event.key == pygame.K_ESCAPE:
                        # just lose focus on escape
                        self._lose_current_focus()
                    
                    elif event.unicode != None and len(event.unicode) > 0:
                        self.current_focus.obj.text_add(event.unicode)
                        textchanged = True
            """
            bind is (key, event, up/down)
             up/down is a bool.
            keybinds_active allows us to prevent user input from inside the scene
            mostly used when playing an animation we don't want interrupted (eg blip_*)
            """
            if self.current_scene.keybinds_active:
                if event.type == pygame.KEYDOWN:
                    #see if the scene has a matching keybind
                    for bind in self.get_binds():
                        if bind[0] == event.key and bind[2]:
                            bind[1](KeyDownEvent(None, event.key))

                if event.type == pygame.KEYUP:
                    for bind in self.get_binds():
                        if bind[0] == event.key and not bind[2]:
                            bind[1](KeyUpEvent(None, event.key))
                            
            if textchanged:
                self.current_focus.obj.update()
                if self.current_focus.events.has_key("keydown") and self.current_focus.events["keydown"] is not None:
                    self.current_focus.events["keydown"](KeyDownEvent(self.current_focus, event.key))   
        
        return True
    
    def _swap_last_focused(self):
        if self.current_focus is None and self.last_focus is not None:
            if self.last_focus.events.has_key("blur") and self.last_focus.events["blur"] is not None:
                self.last_focus.events["blur"](BlurEvent(self.last_focus))

        if self.last_focus is not None:
            self.last_focus.obj.blinking = False
            self.last_focus.obj.swap_enabled()
            self.last_focus.obj.update()
            self.last_focus = None
    
    def _lose_current_focus(self):
        self.last_focus = self.current_focus
        self.current_focus = None
        self._swap_last_focused()

    def set_focus(self, sobj, pos):
        #obj = self.current_scene.objects[name]
        self.current_focus = sobj
        sobj.obj.swap_enabled()
        
        sobj.obj.update()
