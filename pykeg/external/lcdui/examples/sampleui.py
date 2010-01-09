from lcdui.devices import Generic, CrystalFontz
from lcdui.ui import frame
from lcdui.ui import ui
from lcdui.ui import widget

#device = Generic.MockCharacterDisplay(rows=4, cols=40)
device = CrystalFontz.CFA635Display(port='/dev/ttyUSB1')

device.ClearScreen()
device.BacklightEnable(True)

ui = ui.LcdUi(device)

f = ui.FrameFactory(frame.Frame)

line1 = widget.LineWidget(contents="Hello, world!")
f.AddWidget("line1", line1, row=0, col=0)
line2 = widget.LineWidget(contents="cutoffXXXX")
f.AddWidget("line2", line2, row=3, col=10, span=6)

ui.PushFrame(f)
ui.Repaint()
