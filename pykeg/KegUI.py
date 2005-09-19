import lcdui

class KegUI(lcdui.lcdui):
   def __init__(self, device):
      lcdui.lcdui.__init__(self, device)
      self.plate_main = plate_kegbot_main(self)
      self.plate_pour = plate_kegbot_pour(self)

class plate_kegbot_main(lcdui.plate_multi):
   def __init__(self, owner):
      lcdui.plate_multi.__init__(self,owner)
      self.owner = owner

      self.maininfo    = lcdui.plate_std(owner)
      self.tempinfo    = lcdui.plate_std(owner)
      self.freezerinfo = lcdui.plate_std(owner)
      self.lastinfo    = lcdui.plate_std(owner)
      self.drinker     = lcdui.plate_std(owner)

      self.main_menu = lcdui.plate_select_menu(owner,header="kegbot menu")
      self.main_menu.insert(("show history",None,()))
      self.main_menu.insert(("add user",None,()))
      self.main_menu.insert(("squelch user",None,()))
      self.main_menu.insert(("lock kegbot",None,()))
      #self.main_menu.insert(("exit",owner.setCurrentPlate,(self,)))

      self.cmd_dict = {'right': (self.owner.setCurrentPlate,(self.main_menu,)) }

      line1 = lcdui.widget_line_std(" ================== ",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("      kegbot!!      ",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("  have good beer!!  ",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std(" ================== ",row=3,col=0,scroll=0)

      self.maininfo.updateObject('line1',line1)
      self.maininfo.updateObject('line2',line2)
      self.maininfo.updateObject('line3',line3)
      self.maininfo.updateObject('line4',line4)

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| current temp:    |",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("| unknown          |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.tempinfo.updateObject('line1',line1)
      self.tempinfo.updateObject('line2',line2)
      self.tempinfo.updateObject('line3',line3)
      self.tempinfo.updateObject('line4',line4)

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| freezer status:  |",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("| [off]            |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.freezerinfo.updateObject('line1',line1)
      self.freezerinfo.updateObject('line2',line2)
      self.freezerinfo.updateObject('line3',line3)
      self.freezerinfo.updateObject('line4',line4)

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| last pour:       |",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("| 0.0 oz           |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.lastinfo.updateObject('line1',line1)
      self.lastinfo.updateObject('line2',line2)
      self.lastinfo.updateObject('line3',line3)
      self.lastinfo.updateObject('line4',line4)

      line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      line2 = lcdui.widget_line_std("| last drinker:    |",row=1,col=0,scroll=0)
      line3 = lcdui.widget_line_std("| unknown          |",row=2,col=0,scroll=0)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.drinker.updateObject('line1',line1)
      self.drinker.updateObject('line2',line2)
      self.drinker.updateObject('line3',line3)
      self.drinker.updateObject('line4',line4)

      self.addPlate("main",self.maininfo)
      self.addPlate("temp",self.tempinfo)
      self.addPlate("freezer",self.freezerinfo)
      self.addPlate("last",self.lastinfo)
      self.addPlate("drinker",self.drinker)

      # starts the rotation
      self.rotate_time = 5.0

   def setTemperature(self,tempc):
      inside = "%.1fc/%.1ff" % (tempc,toF(tempc))
      line3 = lcdui.widget_line_std("%s"%inside,row=2,col=0,prefix="| ", postfix= " |", scroll=0)
      self.tempinfo.updateObject('line3',line3)

   def setFreezer(self,status):
      inside = "[%s]" % status
      line3 = lcdui.widget_line_std("%s"%inside,row=2,col=0,prefix="| ", postfix= " |", scroll=0)
      self.freezerinfo.updateObject('line3',line3)

   def setLastDrink(self,user,ounces):
      line3 = lcdui.widget_line_std("%s oz"%ounces,row=2,col=0,prefix ="| ",postfix=" |",scroll=0)
      self.lastinfo.updateObject('line3',line3)
      line3 = lcdui.widget_line_std("%s"%user,row=2,col=0,prefix ="| ",postfix=" |",scroll=0)
      self.drinker.updateObject('line3',line3)

   def gotKey(self,key):
      lcdui.plate_multi.gotKey(self,key)

class plate_kegbot_pour(lcdui.plate_std):
   def __init__(self, owner):
      lcdui.plate_std.__init__(self,owner)
      self.owner = owner

      line1 = lcdui.widget_line_std("*------------------*", row=0, col=0, scroll=0)
      self.line2 = lcdui.widget_line_std("", row=1, col=0, scroll=0, prefix='| ', postfix=' |')
      line3 = lcdui.widget_progbar(row = 2, col = 2, prefix ='[', postfix=']', proglen = 9)
      line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      pipe1 = lcdui.widget_line_std("|", row=2,col=0,scroll=0,fat=0)
      pipe2 = lcdui.widget_line_std("|", row=2,col=19,scroll=0,fat=0)
      ounces = lcdui.widget_line_std("", row=2,col=12,scroll=0,fat=0)

      self.updateObject('line1',line1)
      self.updateObject('line2',self.line2)
      self.updateObject('line3',line3)
      self.updateObject('line4',line4)
      self.updateObject('pipe1',pipe1)
      self.updateObject('pipe2',pipe2)
      self.updateObject('ounces',ounces)

   def setDrinker(self, name):
      self.line2.setData('hello, ' + name)

