#this is where we create instances of the scene classes in libscene,
#and populate them with objects as per required for the game.
#it gets a bit tricky passing information between the scenes,
#but i'm pro.

import scenebarebones as scenebb

###########
#MAIN MENU#
###########

class Menu(scenebb.Scene):
    def load_scene(self):
        #layout of main menu
        self.add_escape_keybind()
        self.add_background(self.game.theme_man.themedict["Background"])
        self.objects["background"].scale_self((480,580))
        """
        calling background from theme and scaling allows it to be set once
        by theme_man and also always fit the window, regardless of image size
        that said, resizing images is a surefire way to reduce quality,
        so try use ones that are already 480x580
        """
        self.add_label("welcome",(10,10),"Curvature",self.titlecolor)
        self.add_label("starttut",(50,100),"Start Tutorial",self.textcolor,
            event=lambda x: self.load_next_scene(TutSelect(self.game)))
        self.add_label("startgame",(50,200),"Start Game",self.textcolor,
            event=lambda x: self.load_next_scene(LevelSelect(self.game)))
        self.add_label("themesel",(50,300),"Settings",self.textcolor,
            event=lambda x: self.load_next_scene(Settings(self.game)))
        self.add_label("quit",(10,500),"Quit Game",self.titlecolor,
            event=self.game.quit)

            
##############
#SETTING MENU#
##############

class Settings(scenebb.Scene):
    """
     scene that gives access to the name change scene,
     the theme select scene, and fullscreen toggle.
     all settings saved in resource/saved/settings.txt by set_man
    """
    def load_scene(self):
        self.fullscreen = self.game.set_man.setdict["Fullscreen"]
        self.add_background(self.game.theme_man.themedict["Background"])
        self.objects["background"].scale_self((480,580))
        self.add_prevscene_keybind()
        self.add_label("title",(10,10),"Settings",self.titlecolor)
        self.add_label("themes",(50,100),"Select Theme",self.textcolor,
            event=lambda x: self.load_next_scene(Themes(self.game)))
        self.add_label("name",(50,200),"Change Name",self.textcolor,
            event=lambda x: self.load_next_scene(Name(self.game)))
        self.add_label("fullscr",(50,300),"Fullscreen: "+str(self.fullscreen),self.textcolor,
            event=self.toggle_fullscreen)
            
        self.add_label("music",(50,400),"Music: HERP",self.textcolor,
            event=self.toggle_music)
        if self.game.theme_man.themedict["Music"] == None:
            self.objects["music"].obj.update_text("Music: None")
            self.objects["music"].events["click"] = self.no_music
        elif self.game.set_man.setdict["AutoPlayMusic"] == True:
            self.objects["music"].obj.update_text("Music: On")
        else:
            self.objects["music"].obj.update_text("Music: Off")
            
        self.add_label("menu",(10,500),"Main Menu",self.titlecolor,
            event=lambda x: self.load_next_scene(Menu(self.game)))
                
    def toggle_music(self,event=None):
        self.game.set_man.setdict["AutoPlayMusic"] = not self.game.set_man.setdict["AutoPlayMusic"]
        if self.game.set_man.setdict["AutoPlayMusic"] == True:
            self.objects["music"].obj.update_text("Music: On")
            self.game.play_music(-1)
        else:
            self.objects["music"].obj.update_text("Music: Off")
            self.game.stop_music()
        self.game.set_man.save_settings()
    
    def toggle_fullscreen(self,event=None):
        self.game.switch_fullscreen()
        self.fullscreen = self.game.set_man.setdict["Fullscreen"]
        self.objects["fullscr"].obj.update_text("Fullscreen: "+str(self.fullscreen))
        
    def no_music(self,event=None):
        print "No music for this theme, try changing."
        
###############
#NAME CHANGING#
###############       
        
class Name(scenebb.Scene):
    #scene for changing the name under which scores are saved.
    def load_scene(self):
        self.add_prevscene_keybind()
        self.add_background(self.game.theme_man.themedict["Background"])
        self.objects["background"].scale_self((480,580))
        self.name = self.game.set_man.setdict["Name"]
        self.add_label("name",(10,10),"Name Entry",self.titlecolor)
        self.add_object("nameentry","textbox",(50,100),{"fontfile":"resource/expressway.ttf",
                                                         "fontsize":40,
                                                         "color":self.textcolor,
                                                         "text":self.name})
        self.add_label("save",(50,200),"Save",self.textcolor,
            event=self.save_name)
        self.add_label("menu",(10,500),"Back to Settings",self.titlecolor,
            event=lambda x:self.load_prev_scene(self.game))
    def save_name(self,event=None):
        self.game.set_man.setdict["Name"] = self.objects["nameentry"].obj.text
        self.game.set_man.save_settings()

##############
#THEME SELECT#
##############
        
class Themes(scenebb.Scene):  ## currently where we select themes
    def load_scene(self):
        self.add_background(self.game.theme_man.themedict["Background"])
        self.objects["background"].scale_self((480,580))
        self.add_label("title",(10,10),"Select Theme",self.titlecolor)
        self.add_label("quit",(10,500),"Back to Settings",self.titlecolor,
            event=lambda x: self.load_next_scene(Settings(self.game)))
        # this where we pull the list of themes, and generate a menu for selecting them
        self.themelist = []
        self.themefiles = {}
        self.namelist = []
        f = open("resource/themes/theme_list.txt")
        for line in f:
            line=line.strip()
            if line:
                themename,line = line.split('=')
                fileline = eval(line)
                line = line[16:-10] # strips the _theme.txt
                self.themefiles[line] = fileline # allows easy access to the files
                self.themelist.append(line)
                self.namelist.append(themename)
        f.close()
        labelheight = 40 #make first 80
        for theme in self.themelist:
            labelheight+= 50
            self.add_label(str(theme)+"label",(50,labelheight),str(self.namelist[self.themelist.index(theme)]),self.textcolor,
                  event=lambda x:self.load_theme(x.target.theme))
            self.objects[str(theme)+"label"].theme = theme
        
    def load_theme(self,theme): #just a little less cluttered in the add_label this way
        self.game.theme_man.load_theme(self.themefiles[theme])
        self.themesave = self.themefiles[theme]
        self.save_and_apply()
        
    def save_and_apply(self,event=None):
        self.game.set_man.setdict["Theme"] = self.themesave
        self.game.set_man.save_settings()
        self.game.stop_music() #stops music from previous theme
        self.load_next_scene(Themes(self.game)) #reloading the scene shows the user the new theme

#################
#LEVEL SELECTION#
#################

class LevelSelect(scenebb.Scene):
    def load_scene(self):
        self.add_background(self.game.theme_man.themedict["Background"])
        self.objects["background"].scale_self((480,580))
        self.add_label("title",(10,10),"Select Level",self.titlecolor)
        #this allows us to select levels, and simply pass the filename
        #to the game scene.
        self.leveldict = {1:"resource/levels/leveltwo.txt",2:"resource/levels/levelone.txt",
                          3:"resource/levels/levelthreenotfive.txt",4:"resource/levels/levelthreeforreal.txt"}
        self.scoredirdict = {}
        for key,value in self.leveldict.items():
            # everything except "resource/levels/" and the ".txt"
            value = "resource/saved/" + value[16:-4] + "scores.txt"
            self.scoredirdict[key] = value
        """
        this counts through the items in the level dictionary
        and adds a label for each one, attaches to that label the appropriate event
        and breaks if the user hasn't progressed to that point
        """
        labelheight=40
        count=0
        progress = self.game.set_man.progdict["Game"]
        for level,dir in self.leveldict.items():
            count+=1
            last = False
            if level == len(self.leveldict):
                last = True
            labelheight+=50
            self.add_label(str(level)+"label",(50,labelheight),str(level),self.textcolor,
                event=lambda x:self.load_next_scene(Game(self.game,x.target.leveldets)))
            self.objects[str(level)+"label"].leveldets = (level,False,self.leveldict[level],self.scoredirdict[level],last)
            if count == progress:
                break
        
        self.add_label("menu",(10,400),"Main Menu",self.titlecolor,
            event=lambda x:self.load_next_scene(Menu(self.game)))

class TutSelect(scenebb.Scene):
    def load_scene(self):
        self.add_background(self.game.theme_man.themedict["Background"])
        self.objects["background"].scale_self((480,580))
        self.add_label("title",(10,10),"Select Tutorial",self.titlecolor)
        self.tutdict = {1:"resource/levels/tutorialone.txt",2:"resource/levels/tutorialtwo.txt",
                        3:"resource/levels/tutorialthree.txt",4:"resource/levels/tutorialfour.txt",
                        5:"resource/levels/tutorialfive.txt"}
        labelheight=40
        count=0
        progress = self.game.set_man.progdict["Tut"]                
        for level,dir in self.tutdict.items():
            count+=1
            last = False
            if level == len(self.tutdict):
                last = True
            labelheight+=50
            self.add_label(str(level)+"label",(50,labelheight),str(level),self.textcolor,
                event=lambda x:self.load_next_scene(Game(self.game,x.target.leveldets)))
            self.objects[str(level)+"label"].leveldets = (level,True,self.tutdict[level],None,last)
            if count == progress:
                break
        self.add_label("menu",(10,500),"Main Menu",self.titlecolor,
            event=lambda x:self.load_next_scene(Menu(self.game)))

################
#THE GAME SCENE#
################
            
class Game(scenebb.GameScene):
    #instance of gamescene, all fun stuff here.
    def __init__(self,game,leveldetails):
        self.level = leveldetails[0]
        self.tut = leveldetails[1]
        self.levelmap = leveldetails[2]
        self.scoredir = leveldetails[3]
        self.last = leveldetails[4]
        """
        leveldetails functions essentially the same as state
        but carries slightly different information,
        and carries TO the level instead of FROM it.
        """
        scenebb.GameScene.__init__(self,game,self.levelmap)
        self.load_scene(self.levelmap)

    def load_scene(self,level):
        self.add_background(self.game.theme_man.themedict["GameBackground"])
        self.objects["background"].scale_self((480,580))
        self.time = 0
        if self.tut == False:  # don't want to pressure people doing the tut
            self.add_object("timer","label",(300,50),
                  {"fontfile":"resource/expressway.ttf",
                  "fontsize":35,
                  "color":self.textcolor,
                  "text":"Time:"+str(self.time/60)},
                  events={"render":self.tick_timer})
        self.load_level(self.levelmap)

    def load_menu(self,event=None): #called from inside gamescene.py, allows us to
        self.load_next_scene(Menu(self.game)) #exit straight to menu without importing menu to libscene
                                                    #which would be VERY bad.

    def end_level(self,time): #as above.
        #print 'end_level in Game'
        self.name = self.game.set_man.setdict["Name"]
        """
        these determine what should be displayed in the WIN scene, 
        ie whether the next level should be displayed or not
        """
        self.time = time       
        if self.tut:
            self.game.set_man.progdict["Tut"]+=1
            self.state = (self.level,self.tut,self.last,self.time,
                          None,self.name)
        else:
            self.game.set_man.progdict["Game"]+=1
            self.game.score_man.load_scores(self.scoredir) #load our scores
            #print self.name,'got',self.time/60
            if self.game.score_man.scoredict.has_key(self.name):
                if self.time/60 < self.game.score_man.scoredict[self.name]: #check new against old, if good
                    self.game.score_man.scoredict[self.name] = self.time/60 #then set new to score
            else:
                self.game.score_man.scoredict[self.name] = self.time/60
            
            self.state = (self.level,self.tut,self.last,self.time,
                          self.scoredir,self.name)
        
        self.load_next_scene(Win(self.game,self.state))
        
#################
#THE GRATS SCENE#
#################

class Win(scenebb.Scene):
    """
     this is a GRATS scene when you finish level,
     offers options to continue (if applicable) and return to menu
     should soon display time for level completion, and highscores?
    """
    def __init__ (self,game,state):
            self.game = game
            scenebb.Scene.__init__(self,self.game,setup=False)
            self.add_background(self.game.theme_man.themedict["GameBackground"])
            self.objects["background"].scale_self((480,580))
            self.load_scene(game,state)

    def load_scene(self,game,state):
            """
             the state tuple is a handy way of transferring 
             all the required data about the gamescene we just left
             to the grats scene that we just entered. Saves making a billion args
            """
            self.level = state[0]
            self.tut = state[1]
            self.last = state[2]
            self.time = state[3]
            self.scoredir = state[4] #will be none if self.tut = False. (no scores on tuts)
            self.name = state[5]
            """            
            these add_labels are conditioned because they mean that we can have different messages
            depending on the outcome of the level and the mode in which the user is playing.
            saves us having an unnecessary scene.
            """
            self.add_label("grats",(10,50),"Congratulations.",self.titlecolor)
            if self.tut == False:
                score = self.time/60
                self.game.score_man.save_scores(self.scoredir)
                self.game.score_man.scoredict[self.name] = score
                self.add_label("score",(35,200),
                                "Your time was "+ str(score) +" seconds.",self.textcolor,fontsize=40)
                self.add_label("high",(35,260),
                                "The top 5 times for this level are:",self.textcolor,fontsize=25)
                scoresheight = 280
                count=0
                for name,score in sorted(self.game.score_man.scoredict.items(),key=lambda scor:scor[1]):
                    scoresheight+= 25 #generates high score table based on scores in file, ranked by time
                    self.add_label(str(name)+'score',(35,scoresheight),
                                str(name)+" : "+str(score),self.textcolor,fontsize=20)
                    count+=1
                    if count == 5:
                        break # having more than five scores looks horrible, Top 5 only.

            else:
                self.add_label("note",(35,200),"Note: Tutorials are not timed.",self.titlecolor,fontsize=38)
            if self.last:
                self.level = 1
                self.add_label("men",(10,500),"Quit",self.titlecolor,
                        event = lambda x: self.load_next_scene(Menu(self.game)))
            else:
                self.level+=1
                if self.tut == False:
                    self.add_label("cont",(10,450),"Save and Continue",self.titlecolor,
                        event=lambda x: self.load_next_scene (LevelSelect(self.game)))
                else:
                    self.add_label("conttut",(10,450),"Save and Continue",self.titlecolor,
                        event=lambda x: self.load_next_scene (TutSelect(self.game)))
                        
                self.add_label("men",(10,500),"Save and Quit",self.textcolor,fontsize=20,
                    event=lambda x: self.load_next_scene (Menu(self.game)))
