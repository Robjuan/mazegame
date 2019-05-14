"""
this is the top-level loop.
it imports all the managers and the default scene
then starts it all going.
it waits for a bool from scenemanager to quit
"""
import pygame

from scenebarebones import SceneManager,ScoreManager,SettingManager,ThemeManager
from scenes import Menu

class Game():
    def __init__ (self, width, height, default_scene=None):
        self.width = width
        self.height = height
        self.resolution = (width, height)
        self.running = True
        
        self.setup()
        if default_scene is not None:
            self.load_scene(default_scene)

    def setup (self):
        pygame.init()
        
        self.set_man = SettingManager()
        self.set_man.load_settings()
        self.fullscreen = self.set_man.setdict["Fullscreen"]
        
        if self.fullscreen:
            self.screen = pygame.display.set_mode(self.resolution,pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.resolution)               
        self.scene_man = SceneManager(self.screen)
        
        self.score_man = ScoreManager()

        self.theme_man = ThemeManager()
        self.theme_man.load_theme(self.set_man.setdict["Theme"])
        
        if self.theme_man.themedict["Music"]:
            pygame.mixer.music.set_volume(self.set_man.setdict["Volume"])
            if self.set_man.setdict["AutoPlayMusic"]:
                self.play_music(-1)
            
        self.clock = pygame.time.Clock()
          
    def stop_music(self,event=None):
        pygame.mixer.music.stop()
    def play_music(self,event=None):
        pygame.mixer.music.load(self.theme_man.themedict["Music"])
        pygame.mixer.music.play(-1)
        """
        scene_man is the primary manager, it controls what is shown on screen
          as well as keybinds and events. continuously loops
        score_man loads/saves scores of levels. these actions called by events
          inside scenes
        set_man loads/saves settings. called in its own scene mostly.
        theme_man controls lots of things, scenes often pull information from
          it's themedict to determine what colour to make things etc
        music is controlled from the top level, as it cannot be reloaded each scene,
          without loading the sound file over and over again. (horrible perfomance)
          stop and play music allow for this control to come from scene events.
        clock controls the framerate (very important for timing)
        """
    def load_scene (self, scene):
        self.scene_man.current_scene = scene

    def loop (self):
        while self.running:
            if self.scene_man.process_events() == False:
                # returns false if we should be quitting
                return

            # see if running state has changed after an event
            if not self.running:
                break
            
            self.scene_man.render()
            pygame.display.update()
            self.clock.tick(60) # 60 fps
            
    def switch_fullscreen (self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            print "[game] switching to fullscreen..."
            self.screen = pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        else:
            print "[game] switching to window..."
            self.screen = pygame.display.set_mode(self.resolution)
        self.set_man.setdict["Fullscreen"] = self.fullscreen
        self.set_man.save_settings()
        
        
    def quit (self,event=None):
        #event=None allows us to call this from keybinds,
        #which always pass two args to the target function
        self.running = False
        pygame.quit()

if __name__ == "__main__":
    g = Game (480, 580)
    g.load_scene (Menu(g))
    g.loop()
    #quit() will only occur when loop() ends
    g.quit()
    
    print "Soy un ladron, y estoy aqui para robar tu corazon."
