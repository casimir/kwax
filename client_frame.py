import wx

from faced_text import FacedStaticText
from kakoune import Kakoune
from message_handler import MessageHandler

wx_to_kakoune_keys = {
    wx.WXK_RETURN: "<ret>",
    wx.WXK_SPACE: "<space>",
    wx.WXK_TAB: "<tab>",
    ord("<"): "<lt>",
    ord(">"): "<gt>",
    wx.WXK_BACK: "<backspace>",
    wx.WXK_ESCAPE: "<esc>",
    wx.WXK_UP: "<up>",
    wx.WXK_DOWN: "<down>",
    wx.WXK_LEFT: "<left>",
    wx.WXK_RIGHT: "<right>",
    wx.WXK_PAGEUP: "<pageup>",
    wx.WXK_PAGEDOWN: "<pagedown>",
    wx.WXK_HOME: "<home>",
    wx.WXK_END: "<end>",
    wx.WXK_DELETE: "<end>",
    ord("+"): "<plus>",
    ord("-"): "<minus>",
}


class Client(wx.Frame):

    def __init__(self, kakopts):
        super(Client, self).__init__(None)

        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.makeMenuBar()
        self.CreateStatusBar()

        self.status_line = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)

        self.buffer_view = FacedStaticText(self)
        self.buffer_view.Bind(wx.EVT_SIZE, self.OnBufferSize)
        self.buffer_view.Bind(wx.EVT_KEY_DOWN, self.OnBufferKeyPress)
        self.buffer_view.Bind(wx.EVT_CHAR, self.OnBufferChar)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.status_line, 0, wx.EXPAND)
        sizer.Add(self.buffer_view, 1, wx.EXPAND)
        sizer.SetSizeHints(self)
        self.SetSizerAndFit(sizer)

        self.kakoune = Kakoune(**kakopts)
        self.kakoune.start()
        self.message_handler = MessageHandler(self)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.kakoune_tick, self.timer)
        self.timer.Start(10)

    def kakoune_tick(self, event):
        if not self.kakoune.is_running():
            self.Close()
        else:
            self.message_handler.handle(self.kakoune.get_next_message())

    def makeMenuBar(self):
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(
            wx.ID_ANY, "&Hello...\tCtrl-H", "Help string shown in status bar for this menu item"
        )
        fileMenu.AppendSeparator()
        exitItem = fileMenu.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)

    def OnBufferSize(self, event):
        w, h = self.buffer_view.compute_dimensions()
        self.kakoune.send_resize(h, w)

    def OnBufferKeyPress(self, event):
        keys = wx_to_kakoune_keys.get(event.KeyCode)
        if keys:
            #print("KEY", keys)
            self.kakoune.send_keys(keys)
        else:
            event.Skip()

    def OnBufferChar(self, event):
        keycode = f"{event.UnicodeKey:c}"
        keys = wx_to_kakoune_keys.get(event.UnicodeKey, keycode)
        #print("CHAR", keycode, event.UnicodeKey, keys)
        self.kakoune.send_keys(keys)
        event.Skip()

    def OnExit(self, event):
        self.kakoune.stop()
        self.Destroy()

    def OnHello(self, event):
        wx.MessageBox("Hello again from wxPython")

    def OnAbout(self, event):
        wx.MessageBox("An experimental Kakoune GUI", "kwax", wx.OK | wx.ICON_INFORMATION)
