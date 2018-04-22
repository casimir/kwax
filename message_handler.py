import wx
from wx import stc


class StyleCache(object):

    def __init__(self, default_face):
        self._faces = {}
        self.defaults = default_face
        self.register(default_face)

    def _hash_face(self, face):
        return f"{face['fg']}{face['bg']}{set(face['attributes'])}"

    def register(self, face, hash=True):
        key = self._hash_face(face) if hash else face
        self._faces[key] = len(self._faces)
        assert len(self._faces) <= 32

    def get_id(self, face):
        key = self._hash_face(face)
        if key not in self._faces:
            self.register(key, hash=False)
        return self._faces[key]

    def patch_defaults(self, face):
        if face['fg'] == "default":
            face['fg'] = self.defaults['fg']
        if face['bg'] == "default":
            face['bg'] = self.defaults['bg']


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
        for line in lines:
            ctrl.Clear()
            default_style = face_to_style(default_face, self.default_style)
            ctrl.SetBackgroundColour(default_style.BackgroundColour)
            ctrl.SetDefaultStyle(default_style)
            for atom in line:
                style = face_to_style(atom['face'], default_style)
                ctrl.SetDefaultStyle(style)
                ctrl.AppendText(atom['contents'])

    def do_draw(self, message):
        lines, default_face, padding_face = message.params
        self.default_style = face_to_style(default_face)
        styles = StyleCache(default_face)

        bv = self.window.buffer_view
        bv.SetEditable(True)
        bv.ClearAll()
        bv.StyleClearAll()
        bv.StyleSetForeground(stc.STC_STYLE_DEFAULT, default_face['fg'])
        bv.StyleSetBackground(stc.STC_STYLE_DEFAULT, default_face['bg'])

        for line in lines:
            for atom in line:
                text = atom['contents']
                face = atom['face']
                attributes = face['attributes']
                if 'reverse' in attributes:
                    face['fg'], face['bg'] = face['bg'], face['fg']

                style_id = styles.get_id(face)
                styles.patch_defaults(face)
                bv.StyleSetSpec(style_id, "")
                bv.StyleSetFont(style_id, bv.Font)
                bv.StyleSetForeground(style_id, face['fg'])
                bv.StyleSetBackground(style_id, face['bg'])
                bv.StyleSetBold(style_id, 'bold' in attributes)
                bv.StyleSetItalic(style_id, 'italic' in attributes)
                bv.StyleSetUnderline(style_id, 'underline' in attributes)
                # TODO exclusive, blink, dim

                bv.StartStyling(bv.Length, 0x1f)
                bv.AddText(text)
                bv.SetStyling(len(text.encode('utf-8')), style_id)
            bv.NewLine()
        bv.SetEditable(False)

    def do_draw_status(self, message):
        status_line, mode_line, default_face = message.params
        self._write_to_ctrl(self.window.status_line, [status_line], default_face)
        self.window.SetTitle("".join([x['contents'] for x in mode_line]))
        self.window.SetStatusText("".join([x['contents'] for x in mode_line]))

    def do_refresh(self, message):
        pass

    def do_set_cursor(self, message):
        pass
