import wx


class DrawContext(object):

    def __init__(self, lines=None, default_face=None, padding_face=None):
        self.lines = lines
        self.default_face = default_face
        self.padding_face = padding_face

    def _defaulted_value(self, face, key):
        if not face or face[key] == 'default':
            return self.default_face[key]
        return face[key]

    def fg(self, face=None):
        return self._defaulted_value(face, 'fg')

    def bg(self, face=None):
        return self._defaulted_value(face, 'bg')


class FacedStaticText(wx.Window):

    def __init__(self, parent, style=0, **kwargs):
        style |= wx.WANTS_CHARS
        super(FacedStaticText, self).__init__(parent, style=style, **kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.is_drawing = False
        self.is_dirty = False
        self.drawing_context = DrawContext()

        font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.change_font(font)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetFocus()

    def change_font(self, font):
        self.font = font
        dc = wx.ClientDC(self)
        dc.Font = self.font
        self.font_w = dc.CharWidth
        self.font_h = dc.CharHeight

    def compute_dimensions(self):
        bw, bh = self.ClientSize
        w, h = int(bw / self.font_w), int(bh / self.font_h)
        return w, h

    def set_content(self, lines, default_face, padding_face):
        self.drawing_context = DrawContext(lines, default_face, padding_face)
        self.is_dirty = True
        self.Parent.Refresh()

    def set_face(self, dc, face):
        dc.TextForeground = self.drawing_context.fg(face)
        dc.TextBackground = self.drawing_context.bg(face)

    def draw_line(self, line_idx, line, dc):
        cursor = 0
        for atom in line:
            text = atom['contents']
            self.set_face(dc, atom['face'])
            dc.DrawText(text, cursor * self.font_w, line_idx * self.font_h)
            cursor += len(text)

    def draw_padding(self, dc):
        _, h = self.compute_dimensions()
        self.set_face(dc, self.drawing_context.padding_face)
        for i in range(len(self.drawing_context.lines), h):
            dc.DrawText("~", 0, i * self.font_h)

    def draw(self):
        dc = wx.BufferedPaintDC(self)
        if not dc.IsOk():
            return
        dc.Font = self.font
        dc.BackgroundMode = wx.SOLID
        dc.Background = wx.Brush(self.drawing_context.bg())
        self.set_face(dc, None)
        dc.Clear()
        for (i, line) in enumerate(self.drawing_context.lines):
            self.draw_line(i, line, dc)
        self.draw_padding(dc)

    def OnPaint(self, event):
        if not self.is_dirty or self.is_drawing:
            return
        dc = wx.PaintDC(self)
        if not dc.IsOk():
            return
        dc = wx.PaintDC(self)
        if not dc.IsOk():
            return
        self.is_drawing = True
        self.draw()
        self.is_drawing = False
        self.is_dirty = False

    def OnSize(self, event):
        self.SetFocus()
