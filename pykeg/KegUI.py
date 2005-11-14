import Backend
import re

import lcdui

class KegUI(lcdui.lcdui):
   def __init__(self, device, kb):
      self.kb = kb
      lcdui.lcdui.__init__(self, device)
      self.plate_standby = plate_kegbot_standby(self)
      self.plate_input = plate_kegbot_input(self)
      self.plate_main = plate_kegbot_main(self)
      self.plate_pour = plate_kegbot_pour(self)

   def startPour(self, user):
      self.kb.handleDrinker(user.username)

   def updatePourAmount(self, ounces):
      oz = '%.1foz' % round(ounces, 1)
      progress = (ounces % 8.0)/8.0
      self.plate_pour.write_dict['progline'].setProgress(progress)
      self.plate_pour.write_dict['ounces'].setData(oz)

   def setFreezer(self, status):
      self.plate_main.setFreezer(status)

   def setDrinker(self, name):
      self.plate_pour.setDrinker(name)

   def setLastDrink(self, name, amt):
      self.plate_main.setLastDrink(name, amt)

   def flowEnded(self):
      self.plate_main.gotoPlate('last')

class plate_kegbot_main(lcdui.plate_multi):
   def __init__(self, owner):
      lcdui.plate_multi.__init__(self,owner)
      self.owner = owner

      self.maininfo    = lcdui.plate_std(owner)
      self.tempinfo    = lcdui.plate_std(owner)
      self.freezerinfo = lcdui.plate_std(owner)
      self.lastinfo    = lcdui.plate_std(owner)
      self.drinker     = lcdui.plate_std(owner)
      self.drinkers    = plate_kegbot_drinker_menu(owner, header = "select drinker", default_ptr = self.owner.startPour)

      self.main_menu = lcdui.plate_select_menu(owner,header="kegbot menu")
      self.main_menu.insert(("pour a drink",owner.setCurrentPlate,(self.drinkers,)))
      self.main_menu.insert(("display standby",owner.setCurrentPlate,(owner.plate_standby,)))
      self.main_menu.insert(("input",owner.setCurrentPlate,(owner.plate_input,)))
      self.main_menu.insert(("drink cancel",None,()))
      self.main_menu.insert(("add user",None,()))
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

      self.cmd_dict['enter'] = (self.owner.kb.stopFlow, ())
      self.cmd_dict['exit'] = (self.owner.kb.stopFlow, ())

      line1 = lcdui.widget_line_std("_now pouring________", row=0, col=0, scroll=0)
      self.userline = lcdui.widget_line_std("", row=1, col=0, scroll=0, prefix='', postfix='')
      self.progline = lcdui.widget_progbar(row = 2, col = 0, prefix ='|flow: [', postfix=']', proglen = 14)
      self.costline = lcdui.widget_line_std("",row=3,col=0,prefix='|cost: $0.00',scroll=0)

      ounces = lcdui.widget_line_std("", row=2,col=14,scroll=0,fat=0)

      self.updateObject('line1',line1)
      self.updateObject('userline',self.userline)
      self.updateObject('progline',self.progline)
      self.updateObject('costline',self.costline)
      self.updateObject('ounces',ounces)

   def setDrinker(self, name):
      self.userline.setData('|user: ' + name)

class plate_kegbot_drinker_menu(lcdui.plate_select_menu):
   def onSwitchIn(self):
      users = Backend.User.select()
      if self.cursor + self.offset >= users:
         self.reset()
      self.menu = []
      for u in users:
         self.menu.append((u.username, self.owner.startPour, (u,)))
      self.refreshMenu()

class plate_kegbot_input(lcdui.plate_std):
   def __init__(self, owner):
      lcdui.plate_std.__init__(self, owner)
      self.cmd_dict['up'] = self.goUp
      self.cmd_dict['down'] = self.goDown
      self.cmd_dict['left'] = self.goLeft
      self.cmd_dict['right'] = self.goRight
      self.cmd_dict['exit'] = self.owner.backToLastPlate
      self.cmd_dict['enter'] = self.submit

      self.chars = ' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
      self.data = ' '
      self.updateInput()

   def updateInput(self):
      real_data = re.sub('\s+$','',self.data)  # strip only trailing whitespace
      self.input_line = lcdui.widget_line_std(real_data+'_'*(self.owner.cols() - len(real_data)), row=1,col=0,scroll=0,fat=0)
      self.updateObject('input_line', self.input_line)
      self.cursor_line = lcdui.widget_line_std( (len(self.data) - 1)*' ' + '\x1a', row=2,col=0,scroll=0,fat=0)
      self.updateObject('cursor_line', self.cursor_line)

   def goUp(self):
      if len(self.data) == 0:
         curr_char = ' '
      else:
         curr_char = self.data[-1]
      new_char = self.chars[(self.chars.index(curr_char)-1) % len(self.chars)]
      self.data = self.data[:-1] + new_char
      self.updateInput()

   def goDown(self):
      if len(self.data) == 0:
         curr_char = ' '
      else:
         curr_char = self.data[-1]
      new_char = self.chars[(self.chars.index(curr_char)+1) % len(self.chars)]
      self.data = self.data[:-1] + new_char
      self.updateInput()

   def goLeft(self):
      self.data = self.data[:-1]
      self.updateInput()

   def goRight(self):
      self.data += ' '
      self.updateInput()

   def submit(self):
      print self.data

class plate_kegbot_standby(lcdui.plate_std):
   def __init__(self, owner):
      lcdui.plate_std.__init__(self, owner)
      self.cmd_dict['up'] = self.owner.backToLastPlate
      self.cmd_dict['down'] = self.owner.backToLastPlate
      self.cmd_dict['left'] = self.owner.backToLastPlate
      self.cmd_dict['right'] = self.owner.backToLastPlate
      self.cmd_dict['enter'] = self.owner.backToLastPlate
      self.cmd_dict['exit'] = self.owner.backToLastPlate

   def onSwitchIn(self):
      self.owner.lcdobj.DisableBacklight()

   def onSwitchOut(self):
      self.owner.lcdobj.EnableBacklight()
