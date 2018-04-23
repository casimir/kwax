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

    def refresh_buffer_dimensions(self):
        w, h = self.buffer_view.compute_dimensions()
        self.kakoune.send_resize(h, w)

    def register_menu_view(self, menu_bar):
        bindings = []
        menu = wx.Menu()
        item_zoom_in = menu.Append(
            wx.ID_ANY, "Zoom &in\tCtrl-+", "Zoom buffer in"
        )
        bindings.append((item_zoom_in, self.menu_view_zoom_in))
        item_zoom_out = menu.Append(
            wx.ID_ANY, "Zoom &out\tCtrl--", "Zoom buffer out"
        )
        bindings.append((item_zoom_out, self.menu_view_zoom_out))
        item_zoom_0 = menu.Append(
            wx.ID_ANY, "Zoom &reset\tCtrl-0", "Reset buffer zoom"
        )
        bindings.append((item_zoom_0, self.menu_view_zoom_0))
        menu.AppendSeparator()
        menu_bar.Append(menu, "&View")
        return bindings

    def menu_view_zoom_in(self, event):
        self.buffer_view.change_font_size('+')
        self.refresh_buffer_dimensions()

    def menu_view_zoom_out(self, event):
        self.buffer_view.change_font_size('-')
        self.refresh_buffer_dimensions()

    def menu_view_zoom_0(self, event):
        self.buffer_view.change_font_size('0')
        self.refresh_buffer_dimensions()

    def makeMenuBar(self):
        menu_file = wx.Menu()
        menu_file.AppendSeparator()
        exitItem = menu_file.Append(wx.ID_EXIT)

        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        menu_bindings = []
        menuBar = wx.MenuBar()
        menuBar.Append(menu_file, "&File")
        menu_bindings += self.register_menu_view(menuBar)
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        for item, handler in menu_bindings:
            self.Bind(wx.EVT_MENU, handler, item)

    def OnBufferSize(self, event):
        self.refresh_buffer_dimensions()

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

    def OnAbout(self, event):
        wx.MessageBox("An experimental Kakoune GUI", "kwax", wx.OK | wx.ICON_INFORMATION)
