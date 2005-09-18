#!/usr/bin/python
# coding: iso-8859-1

import xmlrpclib
import socket
import thread
import time
import wx

from wx.lib.wxPlotCanvas import *
import wx.lib.wxPlotCanvas

class StatusPanel(wx.Panel):
   def __init__(self, parent):
      wx.Panel.__init__(self,parent,-1)
      self.SetAutoLayout(True)
      tempfont = wx.Font(20,wx.DEFAULT,wx.NORMAL,wx.BOLD)

      # the top left panel; it stores the celcius temperature text
      self.top_left_panel = wx.Window(self, -1, (10,10), (110,30))
      self.top_right_panel = wx.Window(self, -1, (150,10), (110,30))

      # anchor the top left panel to the top-left
      tc_lc = wx.LayoutConstraints()
      tc_lc.top.SameAs(self,wx.Top,10)
      tc_lc.left.SameAs(self,wx.Left,10)
      self.top_left_panel.SetConstraints(tc_lc)

      # place the temp box in it
      self.temp_c_box= wx.StaticText(self.top_left_panel,-1,"C",wx.DefaultPosition)
      self.temp_c_box.SetFont(tempfont)
      #self.temp_c_box.SetConstraints(tc_lc)

      # the top right panel; it stores the celcius temperature text
      #self.top_right_panel = wx.Window(self, -1, wx.DefaultPosition, (100,30))

      # anchor the top right panel to the top-left
      tf_lc = wx.LayoutConstraints()
      tf_lc.top.SameAs(self,wx.Top,10)
      tf_lc.right.SameAs(self,wx.Right,10)
      self.top_right_panel.SetConstraints(tf_lc)

      # place the temp box in it
      self.temp_f_box= wx.StaticText(self.top_right_panel,-1,"F",wx.DefaultPosition)
      self.temp_f_box.SetFont(tempfont)
      #self.temp_f_box.SetConstraints(tf_lc)


class MainNB(wx.Notebook):
   def __init__(self, parent, id):
      wx.Notebook.__init__(self, parent, -1)
      self.parent = parent

      #
      # set up page 1: the overview page
      # 
      #win_overview = wx.Panel(self, -1)
      self.win_overview = StatusPanel(self)
      self.AddPage(self.win_overview, "Status")

      # 
      # set up page 2: the temperature history page
      # 
      #win_temphist = wx.Panel(self, -1)
      #self.AddPage(win_temphist, "Histogram")
      #plot = PlotCanvas(self)
      #plot.draw(PlotGraphics(PolyLine()))

      #b = wxButton(win_overview,10,"Quit Kegbot ",wxPoint(0,0),wxSize(120,40))

      #EVT_BUTTON(self, 10, self.parent.quitJooky)
      #b.SetToolTipString("Shut down the jooky host")
      #b.SetDefault()
      #wx.StaticText(win_overview,-1,"current temperature:",(20,10))
      #box = wxBoxSizer(wxHORIZONTAL)
      #box.Add(wxButton(win_control,self.BUTTON_prev, "prev"), 0, wxALIGN_TOP)
      #box.Add(wxButton(win_control,self.BUTTON_play, "play/pause"), 0, wxALIGN_TOP)
      #box.Add(wxButton(win_control,self.BUTTON_stop, "stop"), 0, wxALIGN_TOP)
      #box.Add(wxButton(win_control,self.BUTTON_next, "next"), 0, wxALIGN_TOP)
      #win_overview.sizer = box
      #win_overview.SetSizer(box)
      #win_overview.SetAutoLayout(1)
      #win_overview.sizer.Fit(self)

      # set up periodic temperature polling
      ID_temps_timer = wx.NewId()
      self.temps_timer = wx.Timer(self, ID_temps_timer)
      wx.EVT_TIMER(self, ID_temps_timer, self.updateTemps)
      self.temps_timer.Start(5000)

   def updateTemps(self,e):
      try:
         server = self.parent.server
         temp,logtime = server.getTemps()
         #temp = 4.4
         tempf = (1.8*temp)+32
         self.win_overview.temp_c_box.SetLabel("%.2f°C" % (temp,))
         self.win_overview.temp_f_box.SetLabel("%.2f°F" % (tempf,))
      except:
         pass


class BrowserFrame(wx.Frame):
   def __init__(self, parent, ID, title):
      wx.Frame.__init__(self, parent, ID, title, wx.DefaultPosition, wx.Size(300, 300))

      self.host = "192.168.1.50" # alias for 192.168.0.110
      self.host = "localhost"
      self.port = 8337
      self.parent = parent

      self.server = xmlrpclib.ServerProxy("http://%s:%s" % (self.host,self.port))
      self.CenterOnScreen()
      self.CreateStatusBar()
      self.SetStatusText("Status: idle.")

      menuBar = wx.MenuBar()

      menu1 = wx.Menu()

      menu1.Append(101,"E&xit\tCtrl-X","Quit the browser")
      menuBar.Append(menu1,"&File")
      wx.EVT_MENU(self,101,self.onExit)

      self.SetMenuBar(menuBar)

      self.nb = MainNB(self, -1)

      #thread.start_new_thread(self.updateStatus,())

   def updateStatus(self):
      s = ''
      while 1:
         time.sleep(1.0)
         try:
            if self.server.status():
               news = "Status: kegbot active on %s:%s" % (self.host,self.port)
               if s != news:
                  self.SetStatusText(news)
            else:
               news = "Status: no kegbot found on %s:%s" % (self.host,self.port)
               if s != news:
                  self.SetStatusText(news)
         except:
            news = "Status: no kegbot found on %s:%s" % (self.host,self.port)
            if s != news:
               self.SetStatusText(news)
         s = news

   def quitJooky(self,event):
      try:
         if self.server.event("quit"):
            self.SetStatusText("Kegbot is shutting down.")
      except socket.error:
         self.SetStatusText("Error: unable to contact server; maybe it is gone?")
         return None

   def onExit(self,e):
      self.Close(True)

class KegbotViewer(wx.App):
   def OnInit(self):
      frame = BrowserFrame(wx.NULL, -1, "kegbot monitor")
      self.SetTopWindow(frame)
      frame.Show(True)
      return True

app = KegbotViewer(0)
app.MainLoop()
