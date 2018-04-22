import collections
import queue
import shutil
import subprocess
from threading import Thread

import jsonrpc


class Kakoune(object):
    _rpc_next_id = 1

    def __init__(self, bin=None, session=None, files=None):
        self.bin = bin or shutil.which("kak") or "/usr/local/bin/kak"
        self.session = session
        self.files = files
        self.proc = None
        self.messages = queue.Queue()
        self.history = collections.deque(maxlen=1000)
        self._old_size = (-1, -1)

    def list_sessions(self, include_dead=False):
        cmd_output = subprocess.check_output([self.bin, "-l"])
        sessions = cmd_output.decode().splitlines()
        if not include_dead:
            return [x for x in sessions if not x.endswith(" (dead)")]
        return sessions

    def get_connection_command(self):
        parts = [self.bin, "-ui", "json"]
        if self.session:
            parts += ["-c", self.session]
        if self.files:
            cmd = ";".join(f"edit '{x}'" for x in self.files)
            parts += ["-e", cmd]
        return parts

    def _read_messages(self):
        while self.proc.returncode is None:
            line = self.proc.stdout.readline()
            if len(line) == 0:
                break
            message = jsonrpc.Response.parse(line)
            self.messages.put(message)
            self.history.append((">", message))
        self.proc.wait()
        print(f"server disconnected: status {self.proc.returncode}")

    def start(self):
        cmd = self.get_connection_command()
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        message_reader = Thread(target=self._read_messages, name=" ".join(cmd))
        message_reader.start()

    def is_running(self):
        return self.proc and self.proc.returncode is None

    def get_next_message(self):
        try:
            return self.messages.get_nowait()
        except queue.Empty:
            return None

    def _request(self, method, params):
        message = jsonrpc.Request(self._rpc_next_id, method=method, params=params)
        self._rpc_next_id += 1
        self.proc.stdin.write(f"{message}\n".encode())
        self.proc.stdin.flush()
        self.history.append(("<", message))

    def send_keys(self, keys):
        literal_keys = []
        acc = ""
        for c in keys:
            if c == ">":
                literal_keys.append(acc + c)
                acc = ""
                continue
            if c == "<" or len(acc) > 0:
                acc += c
            else:
                literal_keys.append(c)
        self._request('keys', literal_keys)

    def send_command(self, cmd, force=False):
        cmdline = f":{cmd}<ret>"
        if force:
            cmdline = "<esc>" + cmdline
        self.send_keys(cmdline)

    def send_resize(self, rows, columns):
        if self._old_size != (rows, columns):
            self._request('resize', [rows, columns])
            self._old_size = (rows, columns)

    def stop(self):
        if self.is_running():
            self.send_command("quit!", force=True)
