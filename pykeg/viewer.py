import xmlrpclib
import socket
import thread
import time
import wx

class MainNB(wx.Notebook):
   def __init__(self, parent, id):
      wx.Notebook.__init__(self, parent, -1)
      self.parent = parent

      # set up page 1: the prefs/connection page
      win_rmt = wx.Panel(self, -1)
      self.AddPage(win_rmt, "Status")

      # set up page 2: the control (shutdown, etc) page
      #win_control = wx.Panel(self, -1)
      #self.AddPage(win_control, "Control")

      #b = wxButton(win_rmt,10,"Quit Kegbot ",wxPoint(0,0),wxSize(120,40))

      #EVT_BUTTON(self, 10, self.parent.quitJooky)
      #b.SetToolTipString("Shut down the jooky host")
      #b.SetDefault()
      wx.StaticText(win_rmt,-1,"current temperature:",(20,10))
      self.tempbox= wx.StaticText(win_rmt,-1,"none",(180,10))

      self.BUTTON_play = wx.NewId()
      self.BUTTON_stop = wx.NewId()
      self.BUTTON_prev = wx.NewId()
      self.BUTTON_next = wx.NewId()
      #box = wxBoxSizer(wxHORIZONTAL)
      #box.Add(wxButton(win_control,self.BUTTON_prev, "prev"), 0, wxALIGN_TOP)
      #box.Add(wxButton(win_control,self.BUTTON_play, "play/pause"), 0, wxALIGN_TOP)
      #box.Add(wxButton(win_control,self.BUTTON_stop, "stop"), 0, wxALIGN_TOP)
      #box.Add(wxButton(win_control,self.BUTTON_next, "next"), 0, wxALIGN_TOP)
      #win_rmt.sizer = box
      #win_rmt.SetSizer(box)
      #win_rmt.SetAutoLayout(1)
      #win_rmt.sizer.Fit(self)

      # set up periodic temperature polling
      ID_temps_timer = wx.NewId()
      self.temps_timer = wx.Timer(self, ID_temps_timer)
      wx.EVT_TIMER(self, ID_temps_timer, self.updateTemps)
      self.temps_timer.Start(1000)

   def updateTemps(self,e):
      try:
         server = self.parent.server
         temp,logtime = server.getCurrentTemps()
         temp = 4.4
         tempf = (1.8*temp)+32
         self.tempbox.SetLabel("%.2f° C | %.2f° F" % (temp,tempf))
      except:
         pass

   def updatePlaying(self,e):
      try:
         t = server.getCurrentTrack()
         self.playing_trackname.SetLabel(t)
      except:
         pass


class BrowserFrame(wx.Frame):
   def __init__(self, parent, ID, title):
      wx.Frame.__init__(self, parent, ID, title, wx.DefaultPosition, wx.Size(300, 300))

      self.host = "localhost"
      self.port = 7667
      self.parent = parent

      #self.server = xmlrpclib.ServerProxy("http://%s:%s" % (self.host,self.port))
      self.server = None
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

      thread.start_new_thread(self.updateStatus,())

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
