import argparse
import sys

import wx

from client_frame import Client
from kakoune import Kakoune


class SessionChooser(wx.SingleChoiceDialog):

    def __init__(self, kak_bin=None):
        self.sessions = Kakoune(kak_bin).list_sessions()
        super(SessionChooser, self).__init__(
            None, "Choose a session or create a new one.", "Session chooser", self.sessions
        )

    def ShowModal(self):
        if len(self.sessions) == 0:
            return wx.CANCEL
        return super(SessionChooser, self).ShowModal()


class Launcher(wx.App):

    def __init__(self, args, from_app):
        self.args = args
        self.from_app = from_app
        self.client = None
        super(Launcher, self).__init__(redirect=args.debug, useBestVisual=True)

    def ensure_session(self, opts, ask):
        session = opts.get('session')
        if session or not ask:
            return
        session_chooser = SessionChooser(opts.get('bin'))
        if session_chooser.ShowModal() == wx.ID_OK:
            opts['session'] = session_chooser.StringSelection

    def OnInit(self):
        opts = {
            'bin': self.args.binary,
            'session': self.args.connect,
            'files': self.args.files[::-1],
        }
        self.ensure_session(opts, self.args.ask_session)
        self.client = Client(opts)
        self.client.Show()
        return True

    def MacOpenFiles(self, fileNames):
        if not self.from_app:
            return 
        for fname in fileNames:
            self.client.kakoune.send_command(f"edit '{fname}'")


def start(from_app):
    parser = argparse.ArgumentParser()
    parser.add_argument("files", metavar="FILE", nargs='*', help="open the given files on startup")
    parser.add_argument("-c", "--connect", metavar="SESSION", help="connect to given session")
    parser.add_argument(
        "-C", "--ask-session", action="store_true", help="ask for a session to connect to"
    )
    parser.add_argument("--debug", action='store_true', help="show a debug window while running")
    parser.add_argument("--binary", help="path to kakoune executable")
    args = parser.parse_args()

    print(f"wxPython: {wx.version()}")
    print(f"from app: {from_app}")
    print(f"args:     {args}")

    launcher = Launcher(args, from_app)
    launcher.MainLoop()


if __name__ == '__main__':
    start(False)
