import Backend
import re

import lcdui
import units
import util

class KegUI(lcdui.lcdui):
   def __init__(self, device, kb):
      self.kb = kb
      lcdui.lcdui.__init__(self, device)
      self.plate_standby = plate_kegbot_standby(self)
      self.plate_input = plate_kegbot_input(self)
      self.plate_main = plate_kegbot_main(self)
      self.plate_pour = plate_kegbot_pour(self)
      self.plate_alert = AlertPlate(self)
      self.plate_alert.line1 = lcdui.widget_line_std('*'*20, row = 0, col = 0, scroll = 0)
      self.plate_alert.line2 = lcdui.widget_line_std('ERROR'.center(18), row=1, col=0,
            scroll=0, prefix='*', postfix='*')
      self.plate_alert.line4 = lcdui.widget_line_std('*'*20, row = 3, col = 0, scroll = 0)

   def Alert(self, notice):
      self.plate_alert.line3 = lcdui.widget_line_std(notice.center(18), row=2, col=0, scroll=0,
            prefix='*', postfix='*')

      self.plate_alert.SetTimeout(2)
      self.setCurrentPlate(self.plate_alert)

   def setMain(self):
      self.setCurrentPlate(self.plate_main)

   def userPresent(self, user):
      """ Callback for menu UI (if enabled) to start flow for a user """
      self.kb.AuthUser(user.username)

   def setLastDrink(self, d):
      self.plate_main.setLastDrink(d)

   def pourStart(self, username):
      """ Called by kegbot at start of new flow """
      self.activity()
      self.setDrinker(username)
      self.setCurrentPlate(self.plate_pour, replace=1)

   def pourUpdate(self, ounces, cost):
      """ Called by kegbot periodically during a flow """
      self.activity()
      oz = '%.1foz' % round(ounces, 1)
      progress = (ounces % 8.0)/8.0
      self.plate_pour.progline.setProgress(progress)
      self.plate_pour.ounces.setData(oz.rjust(6))
      self.plate_pour.costline.setData('$%.2f' % cost)

   def pourEnd(self, username, amt):
      """ Called by kegbot at end of flow """
      self.plate_main.setLastDrink(username, amt)
      self.setCurrentPlate(self.plate_main, replace=1)

   def setFreezer(self, status):
      self.plate_main.setFreezer(status)

   def setDrinker(self, name):
      self.plate_pour.setDrinker(name)

   def flowEnded(self):
      self.plate_main.gotoPlate('last')


class AlertPlate(lcdui.TimeoutMixin, lcdui.plate_std):
   pass


class plate_kegbot_main(lcdui.plate_multi):
   def __init__(self, owner):
      lcdui.plate_multi.__init__(self,owner)
      self.owner = owner

      self.maininfo    = lcdui.plate_std(owner)
      self.tempinfo    = lcdui.plate_std(owner)
      self.freezerinfo = lcdui.plate_std(owner)
      self.lastinfo    = lcdui.plate_std(owner)
      self.drinker     = lcdui.plate_std(owner)
      self.drinkers    = plate_kegbot_drinker_menu(owner, header = "select drinker",
            default_ptr = self.owner.userPresent)

      self.main_menu = lcdui.plate_select_menu(owner,header="kegbot menu")
      self.main_menu.insert(("pour a drink",owner.setCurrentPlate,(self.drinkers,)))
      self.main_menu.insert(("display standby",owner.setCurrentPlate,(owner.plate_standby,)))
      self.main_menu.insert(("input",owner.setCurrentPlate,(owner.plate_input,)))
      self.main_menu.insert(("drink cancel",None,()))
      self.main_menu.insert(("add user",None,()))
      self.main_menu.insert(("lock kegbot",None,()))
      #self.main_menu.insert(("exit",owner.setCurrentPlate,(self,)))

      self.cmd_dict = {'right': (self.owner.setCurrentPlate,(self.main_menu,)) }

      self.maininfo.line1 = lcdui.widget_line_std(" ================== ",row=0,col=0,scroll=0)
      self.maininfo.line2 = lcdui.widget_line_std("      kegbot!!      ",row=1,col=0,scroll=0)
      self.maininfo.line3 = lcdui.widget_line_std("  have good beer!!  ",row=2,col=0,scroll=0)
      self.maininfo.line4 = lcdui.widget_line_std(" ================== ",row=3,col=0,scroll=0)

      self.tempinfo.line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      self.tempinfo.line2 = lcdui.widget_line_std("| current temp:    |",row=1,col=0,scroll=0)
      self.tempinfo.line3 = lcdui.widget_line_std("| unknown          |",row=2,col=0,scroll=0)
      self.tempinfo.line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.freezerinfo.line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      self.freezerinfo.line2 = lcdui.widget_line_std("| freezer status:  |",row=1,col=0,scroll=0)
      self.freezerinfo.line3 = lcdui.widget_line_std("| [off]            |",row=2,col=0,scroll=0)
      self.freezerinfo.line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.lastinfo.line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      self.lastinfo.line2 = lcdui.widget_line_std("| last pour:       |",row=1,col=0,scroll=0)
      self.lastinfo.line3 = lcdui.widget_line_std("| 0.0 oz           |",row=2,col=0,scroll=0)
      self.lastinfo.line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.drinker.line1 = lcdui.widget_line_std("*------------------*",row=0,col=0,scroll=0)
      self.drinker.line2 = lcdui.widget_line_std("| last drinker:    |",row=1,col=0,scroll=0)
      self.drinker.line3 = lcdui.widget_line_std("| unknown          |",row=2,col=0,scroll=0)
      self.drinker.line4 = lcdui.widget_line_std("*------------------*",row=3,col=0,scroll=0)

      self.addPlate("main",self.maininfo)
      self.addPlate("temp",self.tempinfo)
      self.addPlate("freezer",self.freezerinfo)
      self.addPlate("last",self.lastinfo)
      self.addPlate("drinker",self.drinker)

      # starts the rotation
      self.rotate_time = 5.0

   def setTemperature(self, tempc):
      inside = '%.1fc/%.1ff' % (tempc, util.toF(tempc))
      self.tempinfo.line3 = lcdui.widget_line_std(inside, row = 2, col = 0,
            prefix = '| ', postfix= ' |', scroll=0)

   def setFreezer(self, status):
      inside = '[%s]' % status
      self.freezerinfo.line3 = lcdui.widget_line_std(inside, row = 2, col = 0,
            prefix = '| ', postfix = ' |', scroll = 0)

   def setLastDrink(self, d):
      ounces = units.to_ounces(d.volume)
      self.lastinfo.line3 = lcdui.widget_line_std('%.1f oz' % ounces,
            row = 2, col = 0, prefix = '| ', postfix = ' |', scroll = 0)
      self.drinker.line3 = lcdui.widget_line_std(d.user.username,
            row = 2, col = 0, prefix = '| ', postfix = ' |', scroll = 0)


class plate_kegbot_pour(lcdui.plate_std):
   def __init__(self, owner):
      lcdui.plate_std.__init__(self,owner)
      self.owner = owner

      self.cmd_dict['enter'] = (self.owner.kb.StopFlow, ())
      self.cmd_dict['exit'] = (self.owner.kb.StopFlow, ())

      self.line1 = lcdui.widget_line_std("_now pouring________", row = 0, col = 0, scroll = 0)
      self.userline = lcdui.widget_line_std("", row = 1, col = 0, scroll = 0,
            prefix = '', postfix = '')
      self.progline = lcdui.widget_progbar("", row = 2, col = 0,
            prefix = '|flow: [', postfix =']', proglen = 14)
      self.ounces = lcdui.widget_line_std("", row = 2,col = 14,scroll = 0, pad = False)
      self.costline = lcdui.widget_line_std("$0.00", row = 3, col = 0,
            prefix = '|cost: ', scroll = 0)


   def setDrinker(self, name):
      self.userline.setData('|user: ' + name)


class plate_kegbot_drinker_menu(lcdui.plate_select_menu):
   def onSwitchIn(self):
      users = Backend.User.select()
      if self.cursor + self.offset >= users:
         self.reset()
      self.menu = []
      for u in users:
         self.menu.append((u.username, self.owner.userPresent, (u,)))
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

      self.__dict__['chars'] = ' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
      self.__dict__['data'] = ' '
      self.updateInput()

   def updateInput(self):
      real_data = re.sub('\s+$','',self.data)  # strip only trailing whitespace
      self.input_line = lcdui.widget_line_std(real_data+'_'*(self.owner.cols() - len(real_data)),
            row = 1, col = 0, scroll = 0)
      self.cursor_line = lcdui.widget_line_std( (len(self.data) - 1)*' ' + '\x1a',
            row = 2, col = 0, scroll = 0)

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

