#!/usr/bin/env python3
"""vmctl: drive a QEMU test machine through its QMP socket.

  vmctl.py SOCKET shot FILE.png
  vmctl.py SOCKET key alt-n          (qcodes joined by "-")
  vmctl.py SOCKET type "some text"
  vmctl.py SOCKET click X Y          (pixels; needs -device usb-tablet)
  vmctl.py SOCKET dclick X Y
  vmctl.py SOCKET quit

Several commands can be given, separated by "--". "sleep N" waits.
"""
import json
import socket
import sys
import time

W, H = 1280, 800

KEYMAP = {" ": "spc", "-": "minus", "=": "equal", ".": "dot", ",": "comma", "/": "slash",
          ";": "semicolon", "'": "apostrophe", "\n": "ret", "\t": "tab"}
SHIFTED = {"_": "minus", "+": "equal", ":": "semicolon", "?": "slash", "!": "1", "$": "4", "%": "5"}


class VM:
    def __init__(self, path):
        self.s = socket.socket(socket.AF_UNIX)
        self.s.connect(path)
        self.f = self.s.makefile("rw")
        self.f.readline()
        self.cmd("qmp_capabilities")

    def cmd(self, execute, **arguments):
        msg = {"execute": execute}
        if arguments:
            msg["arguments"] = arguments
        self.f.write(json.dumps(msg) + "\n")
        self.f.flush()
        while True:
            line = self.f.readline()
            if not line:
                raise SystemExit("test machine closed the connection")
            r = json.loads(line)
            if "return" in r:
                return r["return"]
            if "error" in r:
                raise SystemExit(f"{execute}: {r['error']}")

    def key(self, combo):
        keys = [{"type": "qcode", "data": k} for k in combo.split("-")]
        self.cmd("send-key", keys=keys)
        time.sleep(0.15)

    def type(self, text):
        for ch in text:
            if ch in SHIFTED:
                self.key("shift-" + SHIFTED[ch])
            elif ch.isupper():
                self.key("shift-" + ch.lower())
            else:
                self.key(KEYMAP.get(ch, ch))

    def move(self, x, y):
        ev = [{"type": "abs", "data": {"axis": "x", "value": int(x * 32767 / W)}},
              {"type": "abs", "data": {"axis": "y", "value": int(y * 32767 / H)}}]
        self.cmd("input-send-event", events=ev)
        time.sleep(0.2)

    def press(self):
        for down in (True, False):
            self.cmd("input-send-event", events=[{"type": "btn", "data": {"down": down, "button": "left"}}])
            time.sleep(0.08)

    def click(self, x, y, times=1):
        self.move(x, y)
        for _ in range(times):
            self.press()
        time.sleep(0.3)

    def shot(self, filename):
        self.cmd("screendump", filename=filename, format="png")


def run(vm, words):
    op, args = words[0], words[1:]
    if op == "shot":
        vm.shot(args[0])
    elif op == "key":
        for k in args:
            vm.key(k)
    elif op == "type":
        vm.type(" ".join(args))
    elif op == "click":
        vm.click(int(args[0]), int(args[1]))
    elif op == "dclick":
        vm.click(int(args[0]), int(args[1]), times=2)
    elif op == "move":
        vm.move(int(args[0]), int(args[1]))
    elif op == "sleep":
        time.sleep(float(args[0]))
    elif op == "quit":
        try:
            vm.cmd("quit")
        except SystemExit:
            pass
    else:
        raise SystemExit(f"unknown command: {op}")


if __name__ == "__main__":
    vm = VM(sys.argv[1])
    group = []
    for w in sys.argv[2:] + ["--"]:
        if w == "--":
            if group:
                run(vm, group)
            group = []
        else:
            group.append(w)
