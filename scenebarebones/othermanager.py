"""
this contains the code for the secondary managers.
these look after all the persistent information, such as themes, scores and settings.
they are all minor derivatives of the base manager.
"""

import os.path as path

class BaseManager():    
    def __init__(self,filename=None):
        if filename is not None:
            self.filename = filename
            self.load(self.filename)
    """
    we open a file, and look at each line.
    each line should hold one key=value pair.
    eval() is a great builtin catchall that converts ints, tuples, etc
    everything else is just a string
    """
    def load(self,filename):
        f = open(filename,'r')
        dict = {}
        for line in f:
            line = line.strip()
            if line:
                if "COMMENT" not in line:
                    key,value = line.split('=')
                    key = key.strip()
                    value = value.strip()
                    #print value,'from',filename
                    value = eval(value)
                    dict[key] = value
        f.close()
        print '[Manager] loaded',filename
        return dict
    #writes the dict back to the file in the same format it was read.
    def save(self,dict,filename):        
        f = open(filename,'w')
        for key in dict:
            if type(dict[key]) == str:
                writeline=str(key)+'="'+str(dict[key])+'"\n'
            else:
                writeline = str(key) + '=' + str(dict[key]) + '\n'
            f.write(writeline)
        f.close()
        print '[Manager] saved',filename
        
#basic derivatives       
class SettingManager(BaseManager):
    def load_settings(self,filename="resource/saved/settings.txt"):
        self.setdict = self.load(filename)
        if path.exists("resource/saved/"+str(self.setdict["Name"])+"_progress.txt"):
            self.progdict = self.load("resource/saved/"+str(self.setdict["Name"])+"_progress.txt")
        else:
            #this creates a new file for us to write to, and sets it with default vals
            filestr = "resource/saved/"+str(self.setdict["Name"])+"_progress.txt"
            f = open(filestr,"w")
            f.write("Tut=1\n")
            f.write("Game=1\n")
            f.close()
            print "[Manager] created new "+str(self.setdict["Name"])+"_progress.txt"
        
    def save_settings(self,filename="resource/saved/settings.txt"):
        self.save(self.setdict,filename)
        self.save(self.progdict,filename="resource/saved/"+str(self.setdict["Name"])+"_progress.txt")
        
class ScoreManager(BaseManager):
    def load_scores(self,filename):
        self.scoredict = self.load(filename)
        
    def save_scores(self,filename):
        self.save(self.scoredict,filename)
"""
complex derivative!
there are "dominant" settings. This means that if the sub-settings are not set,
they will automatically take on the value of the "dominant" settings.
this means that we won't have to "if x is not None" when using these.
"""        
class ThemeManager(BaseManager):
    def load_theme(self,filename):
        self.themedict = self.load(filename)
        #print self.themedict
        if self.themedict["TitleColor"] == None:
            self.themedict["TitleColor"] = self.themedict["TextColor"]
        if self.themedict["GameMusic"] == None:
            self.themedict["GameMusic"] = self.themedict["Music"]
        if self.themedict["GameBackground"] == None:
            self.themedict["GameBackground"] = self.themedict["Background"]
            
    def save_theme(self,filename):
        self.save(self.themedict,filename)