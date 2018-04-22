import wx


def face_to_style(face, default=None):
    if not default:
        return wx.TextAttr(face['fg'], face['bg'])
    attr = wx.TextAttr(default)
    if face['fg'] != "default":
        attr.TextColour = face['fg']
    if face['bg'] != "default":
        attr.BackgroundColour = face['bg']
    return attr


class MessageHandler(object):

    def __init__(self, window):
        self.window = window
        self.default_style = None

    def handle(self, message):
        if message is None:
            return
        do_fn = getattr(self, f"do_{message.method}", self.do_undefined)
        do_fn(message)

    def do_undefined(self, message):
        print(f"? {message}")

    def _write_to_ctrl(self, ctrl, lines, default_face):
        ctrl.Clear()
        for line in lines:
            default_style = face_to_style(default_face, self.default_style)
            ctrl.SetBackgroundColour(default_style.BackgroundColour)
            ctrl.SetDefaultStyle(default_style)
            for atom in line:
                style = face_to_style(atom['face'], default_style)
                ctrl.SetDefaultStyle(style)
                ctrl.AppendText(atom['contents'])

    def do_draw(self, message):
        lines, default_face, padding_face = message.params
        self.window.buffer_view.set_content(lines, default_face, padding_face)
        self.default_style = face_to_style(default_face)

    def do_draw_status(self, message):
        status_line, mode_line, default_face = message.params
        self._write_to_ctrl(self.window.status_line, [status_line], default_face)
        self.window.SetTitle("".join([x['contents'] for x in mode_line]))
        self.window.SetStatusText("".join([x['contents'] for x in mode_line]))

    def do_refresh(self, message):
        pass

    def do_set_cursor(self, message):
        pass
