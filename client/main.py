import wx
from views import MainFrameView

if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrameView(None)
    frame.Show()
    app.MainLoop()
