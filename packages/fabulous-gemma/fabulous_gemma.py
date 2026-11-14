#!/usr/bin/env python3
"""fabulous-gemma: the Gemma assistant of Fabulous OS.

Runs Google's Gemma 4 on this computer with llama.cpp's server. Nothing is sent
anywhere: the server is started inside its own empty network namespace (it has no
network card at all, not even the firewall's view of one) and is spoken to through
a private socket file. If that isolation cannot be set up, Gemma does not start.

  fabulous-gemma                 open the chat window
  fabulous-gemma --ask "..."     answer one question on the terminal (used by tests)
       [--picture FILE] [--recording FILE]   ... about a picture or a sound recording
  fabulous-gemma --isolation     show what network the assistant can see (tests)
"""
import argparse
import base64
import glob
import http.client
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time

PREFIX = os.environ.get("FABULOUS_GEMMA_PREFIX", "/opt/fabulous-gemma")
MODEL_DIR = os.environ.get("FABULOUS_GEMMA_MODELS", "/usr/share/fabulous/models")
RULES_DIR = os.environ.get("FABULOUS_RULES_DIR", "/usr/local/share/fabulous")

CONTEXT_TOKENS = 8192
# Roughly 3 characters per token; leave room for the answer.
HISTORY_CHAR_BUDGET = 15000
# Google's recommended sampling settings for Gemma.
SAMPLING = {"temperature": 1.0, "top_k": 64, "top_p": 0.95}
# With a picture or recording in the conversation the task is to report what is
# there, so Gemma is made less inventive. (At the normal setting it misheard a
# time of day in 5 of 9 tries in one test; at this one, 0 of 9.)
SAMPLING_SENSES = {"temperature": 0.2, "top_k": 64, "top_p": 0.95}
SYSTEM_PROMPT = (
    "You are Gemma, an AI assistant that runs entirely on the user's own computer as "
    "part of Fabulous OS. You have no internet access and cannot look anything up, so "
    "say so if asked about recent events or live information. If you are not sure of "
    "something, say that you are not sure. Keep answers short and clear unless asked "
    "for detail."
)
SYSTEM_PROMPT_SENSES = (
    " You can look at pictures and listen to sound recordings that the user attaches. "
    "Describe only what is really there, and say so if something is unclear."
)
# Roughly what an attachment costs of the model's working memory, in characters.
ATTACHMENT_CHAR_COST = 1200
PICTURE_TYPES = ("png", "jpg", "jpeg", "bmp", "gif", "webp")
RECORDING_TYPES = ("wav", "mp3", "flac")
MAX_RECORDING_BYTES = 30 * 1024 * 1024
ISOLATE = ["unshare", "--map-current-user", "--net", "--"]


class GemmaError(Exception):
    """A problem to show the person in plain words."""


# ---------------------------------------------------------------- hardware

def read_memory_gb(path="/proc/meminfo"):
    with open(path) as f:
        for line in f:
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) / 1024 / 1024
    return 0.0


def read_cpu(path="/proc/cpuinfo"):
    """Return (physical core count, set of feature flags)."""
    cores, flags, phys, core = set(), set(), None, None
    logical = 0
    with open(path) as f:
        for line in f:
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            if key == "processor":
                logical += 1
            elif key == "physical id":
                phys = value
            elif key == "core id":
                core = value
            elif key == "flags" and not flags:
                flags = set(value.split())
            elif not key and phys is not None and core is not None:
                cores.add((phys, core))
                phys = core = None
    if phys is not None and core is not None:
        cores.add((phys, core))
    return (len(cores) or logical or 1), flags


def advice(memory_gb=None, flags=None):
    """What the project's rules say about Gemma on this computer.
    Returns (model or "none", [notes])."""
    if memory_gb is None:
        memory_gb = read_memory_gb()
    if flags is None:
        flags = read_cpu()[1]
    profile = {"memory": {"total_gb": memory_gb}, "cpu": {"avx2": "avx2" in flags}}
    try:
        sys.path.insert(0, RULES_DIR)
        import fabulous_rules
        return fabulous_rules.choose_model(profile, fabulous_rules.load_rules())
    except Exception:
        # Rules not installed (for example when run from the source tree): the same
        # limits, written out.
        if memory_gb < 6:
            return "none", ["This computer has too little memory for the Gemma assistant."]
        if "avx2" not in flags:
            return "e2b", ["This processor lacks features that speed up AI, so Gemma will answer slowly."]
        return "e2b", []
    finally:
        if sys.path and sys.path[0] == RULES_DIR:
            sys.path.pop(0)


def unavailable_text(memory_gb=None, flags=None):
    """Why Gemma will not run here, in the assistant's own words (the rules' wording
    is written for the installer)."""
    if memory_gb is None:
        memory_gb = read_memory_gb()
    if flags is None:
        flags = read_cpu()[1]
    text = f"Gemma cannot run on this computer. It has {memory_gb:.0f} GB of memory"
    if "avx2" in flags:
        return text + ", and Gemma needs at least 6 GB."
    return text + (" and a processor without the AVX2 feature that speeds up AI. "
                   "On such a processor Gemma needs at least 12 GB of memory.")


def find_model(model_dir=None):
    explicit = os.environ.get("FABULOUS_GEMMA_MODEL")
    if explicit:
        return explicit
    files = sorted(f for f in glob.glob(os.path.join(model_dir or MODEL_DIR, "*.gguf"))
                   if "mmproj" not in os.path.basename(f))
    if not files:
        raise GemmaError("The Gemma model file is missing from this computer.")
    return files[0]


def find_senses(model_dir=None):
    """Google's add-on file that lets Gemma look at pictures and listen to
    recordings, or None if this image was built without it."""
    explicit = os.environ.get("FABULOUS_GEMMA_MMPROJ")
    if explicit:
        return explicit if os.path.exists(explicit) else None
    files = sorted(glob.glob(os.path.join(model_dir or MODEL_DIR, "*mmproj*.gguf")))
    return files[0] if files else None


def attachment(kind, path, data=None):
    """A picture or recording to send with a question. `data` is the file's bytes
    (the window passes pictures already converted to PNG); otherwise the file is read."""
    if kind not in ("picture", "recording"):
        raise GemmaError("Only pictures and sound recordings can be attached.")
    if data is None:
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError as e:
            raise GemmaError(f"Could not open {os.path.basename(path)}: {e.strerror}")
    if kind == "recording" and len(data) > MAX_RECORDING_BYTES:
        raise GemmaError("That recording is too long for Gemma. Try a shorter one.")
    return {"kind": kind, "name": os.path.basename(path), "b64": base64.b64encode(data).decode("ascii")}


def to_wire(message):
    """One message of the conversation in the form the server expects."""
    attached = message.get("attachments") or []
    if not attached:
        return {"role": message["role"], "content": message["content"]}
    # The question goes first: asked the other way round, Gemma sometimes replied
    # that it could not listen to recordings (seen in testing, 14 November 2026).
    parts = [{"type": "text", "text": message["content"]}]
    for a in attached:
        if a["kind"] == "picture":
            parts.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + a["b64"]}})
        else:
            parts.append({"type": "input_audio", "input_audio": {"data": a["b64"], "format": "wav"}})
    return {"role": message["role"], "content": parts}


def find_server():
    path = os.environ.get("FABULOUS_GEMMA_SERVER") or os.path.join(PREFIX, "bin", "llama-server")
    if not os.access(path, os.X_OK):
        raise GemmaError("The program that runs Gemma is missing from this computer.")
    return path


def isolation_report():
    """What network the assistant can see from inside its isolation. On a correct
    system: only the 'lo' loopback device, and it is down."""
    out = subprocess.run(ISOLATE + ["cat", "/proc/net/dev"], capture_output=True, text=True)
    if out.returncode != 0:
        raise GemmaError("Network isolation could not be set up: " + out.stderr.strip())
    devices = [line.split(":")[0].strip() for line in out.stdout.splitlines()[2:] if ":" in line]
    return devices


# ---------------------------------------------------------------- engine

class _UnixConnection(http.client.HTTPConnection):
    def __init__(self, path, timeout=None):
        super().__init__("localhost", timeout=timeout)
        self._path = path

    def connect(self):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect(self._path)
        self.sock = s


def trim_history(messages, budget=HISTORY_CHAR_BUDGET):
    """Keep the newest messages that fit the model's working memory. Always keeps
    the last message. Drops whole messages, oldest first."""
    kept, used = [], 0
    for m in reversed(messages):
        n = len(m["content"]) + ATTACHMENT_CHAR_COST * len(m.get("attachments") or [])
        if kept and used + n > budget:
            break
        kept.append(m)
        used += n
    kept.reverse()
    # A conversation sent to the model should start with the user's turn.
    while len(kept) > 1 and kept[0]["role"] != "user":
        kept.pop(0)
    return kept


def parse_stream_line(line):
    """One line of the server's event stream -> (text piece or None, timings or None, done)."""
    line = line.strip()
    if not line.startswith("data:"):
        return None, None, False
    data = line[5:].strip()
    if data == "[DONE]":
        return None, None, True
    try:
        obj = json.loads(data)
    except ValueError:
        return None, None, False
    if "error" in obj:
        err = obj["error"]
        raise GemmaError(str(err.get("message", err) if isinstance(err, dict) else err))
    piece = None
    choices = obj.get("choices") or []
    if choices:
        piece = (choices[0].get("delta") or {}).get("content")
    return piece, obj.get("timings"), False


class Engine:
    """Starts and talks to the model on this computer."""

    def __init__(self, threads=None, log_path=None):
        self.proc = None
        self.dir = None
        self.sock = None
        self.threads = threads
        self.log_path = log_path
        self._conn = None
        self.last_timings = None
        self.senses = False  # can it look at pictures and listen to recordings?

    def start(self):
        server, model = find_server(), find_model()
        mmproj = find_senses()
        self.senses = mmproj is not None
        if shutil.which("unshare") is None:
            raise GemmaError("Network isolation is not available, so Gemma was not started.")
        isolation_report()  # raises if the isolation cannot be set up
        base = os.environ.get("XDG_RUNTIME_DIR")
        self.dir = tempfile.mkdtemp(prefix="fabulous-gemma-", dir=base if base and os.path.isdir(base) else None)
        self.sock = os.path.join(self.dir, "gemma.sock")
        threads = self.threads or read_cpu()[0]
        cmd = ISOLATE + [
            server, "--model", model, "--host", self.sock,
            "--ctx-size", str(CONTEXT_TOKENS), "--threads", str(threads),
            "--parallel", "1", "--reasoning", "off", "--no-ui", "--offline",
            "--cache-ram", "256", "--no-slots",
        ]
        if mmproj:
            cmd += ["--mmproj", mmproj]
        env = dict(os.environ, LD_LIBRARY_PATH=os.path.join(PREFIX, "bin"))
        self.log_path = self.log_path or os.path.join(self.dir, "server.log")
        self._log = open(self.log_path, "wb")
        self.proc = subprocess.Popen(cmd, stdout=self._log, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, env=env)
        return self

    def log_tail(self, lines=15):
        try:
            with open(self.log_path, "rb") as f:
                return b"\n".join(f.read().splitlines()[-lines:]).decode("utf-8", "replace")
        except OSError:
            return ""

    def is_ready(self):
        """True once the model is loaded. Raises if the program has stopped."""
        if self.proc.poll() is not None:
            raise GemmaError("Gemma stopped unexpectedly while starting.\n\n" + self.log_tail())
        if not os.path.exists(self.sock):
            return False
        try:
            c = _UnixConnection(self.sock, timeout=5)
            c.request("GET", "/health")
            ok = c.getresponse().status == 200
            c.close()
            return ok
        except OSError:
            return False

    def wait_ready(self, timeout=900):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if self.is_ready():
                return
            time.sleep(0.5)
        raise GemmaError("Gemma took too long to load.")

    def chat(self, messages, max_tokens=None):
        """Yield the answer piece by piece. `messages` is the conversation so far."""
        system = SYSTEM_PROMPT + (SYSTEM_PROMPT_SENSES if self.senses else "")
        kept = trim_history(messages)
        sampling = SAMPLING_SENSES if any(m.get("attachments") for m in kept) else SAMPLING
        body = dict(sampling, stream=True, messages=[{"role": "system", "content": system}]
                    + [to_wire(m) for m in kept])
        if max_tokens:
            body["max_tokens"] = max_tokens
        self.last_timings = None
        conn = self._conn = _UnixConnection(self.sock, timeout=1800)
        try:
            conn.request("POST", "/v1/chat/completions", json.dumps(body),
                         {"Content-Type": "application/json"})
            resp = conn.getresponse()
            if resp.status != 200:
                text = resp.read().decode("utf-8", "replace")
                try:
                    text = json.loads(text)["error"]["message"]
                except Exception:
                    pass
                raise GemmaError("Gemma could not answer: " + text[:500])
            for raw in resp:
                piece, timings, done = parse_stream_line(raw.decode("utf-8", "replace"))
                if timings:
                    self.last_timings = timings
                if piece:
                    yield piece
                if done:
                    break
        finally:
            self._conn = None
            conn.close()

    def cancel(self):
        """Stop the answer being written (closing the connection tells the server)."""
        conn = self._conn
        if conn is not None and conn.sock is not None:
            try:
                conn.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if self.dir:
            shutil.rmtree(self.dir, ignore_errors=True)
        self.proc = None


# ---------------------------------------------------------------- terminal

def ask(question, max_tokens=None, out=sys.stdout, picture=None, recording=None):
    model, notes = advice()
    if model == "none":
        raise GemmaError(unavailable_text())
    cores, flags = read_cpu()
    print(f"model file: {os.path.basename(find_model())}", file=out)
    senses = find_senses()
    print(f"pictures and recordings: {os.path.basename(senses) if senses else 'not in this image'}", file=out)
    attached = []
    if picture:
        attached.append(attachment("picture", picture))
    if recording:
        attached.append(attachment("recording", recording))
    if attached and not senses:
        raise GemmaError("This copy of Gemma cannot look at pictures or listen to recordings.")
    print(f"processor: {cores} cores, AVX2 {'yes' if 'avx2' in flags else 'no'}, "
          f"AVX {'yes' if 'avx' in flags else 'no'}; memory {read_memory_gb():.1f} GB", file=out)
    print(f"network devices visible to the assistant: {isolation_report()}", file=out)
    engine = Engine()
    t0 = time.monotonic()
    engine.start()
    try:
        engine.wait_ready()
        print(f"loaded in {time.monotonic() - t0:.0f} s", file=out)
        print(f"question: {question}" + "".join(f" [{a['kind']}: {a['name']}]" for a in attached), file=out)
        out.write("answer: ")
        t1 = time.monotonic()
        first = None
        for piece in engine.chat([{"role": "user", "content": question, "attachments": attached}],
                                 max_tokens=max_tokens):
            if first is None:
                first = time.monotonic() - t1
            out.write(piece)
            out.flush()
        t = engine.last_timings or {}
        print(f"\nanswer began after {first or 0:.0f} s; answered in {time.monotonic() - t1:.0f} s; "
              f"{t.get('predicted_n', '?')} tokens at {t.get('predicted_per_second', 0):.1f} tokens per second "
              f"(reading the question: {t.get('prompt_per_second', 0):.1f} per second)", file=out)
    finally:
        engine.stop()


# ---------------------------------------------------------------- window

def run_window(demo=None, screenshot=None, demo_picture=None, demo_recording=None):
    """Open the chat window. `demo` and `screenshot` are for tests: ask one question
    by itself, save a picture of the window when it is answered, and close."""
    import fcntl
    from PyQt6.QtCore import QBuffer, QIODevice, Qt, QThread, QTimer, pyqtSignal
    from PyQt6.QtGui import QIcon, QImage, QTextCursor
    from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMainWindow,
                                 QMessageBox, QPlainTextEdit, QPushButton, QTextBrowser,
                                 QVBoxLayout, QWidget)

    def load_picture(path):
        """Read a picture of any kind Qt knows, shrink a large photo, and hand it
        over as PNG. A phone photo is far bigger than Gemma can take in."""
        img = QImage(path)
        if img.isNull():
            raise GemmaError(f"{os.path.basename(path)} could not be opened as a picture.")
        if max(img.width(), img.height()) > 1600:
            img = img.scaled(1600, 1600, Qt.AspectRatioMode.KeepAspectRatio,
                             Qt.TransformationMode.SmoothTransformation)
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        img.save(buf, "PNG")
        return attachment("picture", path, bytes(buf.data()))

    app = QApplication(sys.argv)
    app.setApplicationName("Gemma")
    app.setDesktopFileName("fabulous-gemma")
    app.setWindowIcon(QIcon.fromTheme("fabulous-gemma", QIcon.fromTheme("dialog-messages")))

    # One Gemma at a time: two would each load the whole model into memory.
    lock_dir = os.environ.get("XDG_RUNTIME_DIR") or tempfile.gettempdir()
    lock = open(os.path.join(lock_dir, "fabulous-gemma.lock"), "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        QMessageBox.information(None, "Gemma", "Gemma is already open.")
        return 0

    model, notes = advice()
    if model == "none":
        QMessageBox.information(None, "Gemma", unavailable_text())
        return 0

    class Loader(QThread):
        ready = pyqtSignal()
        failed = pyqtSignal(str)

        def __init__(self, engine):
            super().__init__()
            self.engine = engine

        def run(self):
            try:
                self.engine.start()
                self.engine.wait_ready()
                self.ready.emit()
            except GemmaError as e:
                self.failed.emit(str(e))
            except Exception as e:  # shown, never hidden
                self.failed.emit(f"Unexpected problem: {e}")

    class Answer(QThread):
        piece = pyqtSignal(str)
        finished_ok = pyqtSignal()
        failed = pyqtSignal(str)

        def __init__(self, engine, messages):
            super().__init__()
            self.engine, self.messages, self.cancelled = engine, messages, False

        def run(self):
            try:
                for p in self.engine.chat(self.messages):
                    self.piece.emit(p)
                self.finished_ok.emit()
            except GemmaError as e:
                self.failed.emit(str(e))
            except Exception as e:
                if self.cancelled:
                    self.finished_ok.emit()
                else:
                    self.failed.emit(f"Unexpected problem: {e}")

    class Input(QPlainTextEdit):
        send = pyqtSignal()

        def keyPressEvent(self, e):
            if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (
                    e.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.send.emit()
            else:
                super().keyPressEvent(e)

    class Window(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Gemma")
            self.resize(760, 640)
            self.engine = Engine()
            self.messages = []   # the conversation: [{"role", "content", "attachments"}]
            self.pending = []    # pictures and recordings waiting to go with the next question
            self.partial = None  # the answer being written
            self.answer = None
            self.started = 0.0

            self.view = QTextBrowser()
            self.view.setOpenLinks(False)  # nothing in an answer can open a web page
            self.input = Input()
            self.input.setPlaceholderText("Type your question here. Enter sends it; Shift+Enter starts a new line.")
            self.input.setFixedHeight(84)
            self.input.send.connect(self.on_send)
            self.send_btn = QPushButton("Send")
            self.send_btn.clicked.connect(self.on_send)
            self.stop_btn = QPushButton("Stop")
            self.stop_btn.clicked.connect(self.on_stop)
            self.new_btn = QPushButton("New chat")
            self.new_btn.clicked.connect(self.on_new)
            self.pic_btn = QPushButton("Add a picture…")
            self.pic_btn.clicked.connect(self.on_add_picture)
            self.rec_btn = QPushButton("Add a recording…")
            self.rec_btn.clicked.connect(self.on_add_recording)
            self.clear_btn = QPushButton("Remove")
            self.clear_btn.clicked.connect(self.on_clear_pending)
            self.pending_label = QLabel()
            self.pending_label.setWordWrap(True)
            self.status = QLabel()
            self.status.setWordWrap(True)
            about = QLabel("Gemma runs on this computer only. Nothing you type is sent anywhere. "
                           "Gemma can be wrong: check anything important."
                           + ("".join("\n" + n for n in notes)))
            about.setWordWrap(True)

            buttons = QVBoxLayout()
            for b in (self.send_btn, self.stop_btn, self.new_btn):
                buttons.addWidget(b)
            row = QHBoxLayout()
            row.addWidget(self.input, 1)
            row.addLayout(buttons)
            self.attach_row = QWidget()
            attach = QHBoxLayout(self.attach_row)
            attach.setContentsMargins(0, 0, 0, 0)
            attach.addWidget(self.pic_btn)
            attach.addWidget(self.rec_btn)
            attach.addWidget(self.pending_label, 1)
            attach.addWidget(self.clear_btn)
            self.attach_row.hide()  # shown once Gemma has loaded with eyes and ears
            col = QVBoxLayout()
            col.addWidget(about)
            col.addWidget(self.view, 1)
            col.addWidget(self.attach_row)
            col.addLayout(row)
            col.addWidget(self.status)
            w = QWidget()
            w.setLayout(col)
            self.setCentralWidget(w)

            self.refresh = QTimer(self)
            self.refresh.setInterval(200)
            self.refresh.timeout.connect(self.render)
            self.set_busy(True, "Gemma is loading. This can take a minute or two…")
            self.loader = Loader(self.engine)
            self.loader.ready.connect(self.on_ready)
            self.loader.failed.connect(self.on_load_failed)
            self.loader.start()

        def show_pending(self):
            names = ", ".join(a["name"] for a in self.pending)
            self.pending_label.setText(("Attached: " + names) if names else "")
            self.clear_btn.setVisible(bool(self.pending))

        def add_pending(self, make):
            try:
                self.pending.append(make())
            except GemmaError as e:
                QMessageBox.warning(self, "Gemma", str(e))
            self.show_pending()

        def on_add_picture(self):
            pattern = "Pictures (" + " ".join("*." + t for t in PICTURE_TYPES) + ")"
            path, _ = QFileDialog.getOpenFileName(self, "Choose a picture", os.path.expanduser("~"), pattern)
            if path:
                self.add_pending(lambda: load_picture(path))

        def on_add_recording(self):
            pattern = "Sound recordings (" + " ".join("*." + t for t in RECORDING_TYPES) + ")"
            path, _ = QFileDialog.getOpenFileName(self, "Choose a recording", os.path.expanduser("~"), pattern)
            if path:
                self.add_pending(lambda: attachment("recording", path))

        def on_clear_pending(self):
            self.pending = []
            self.show_pending()

        def set_busy(self, busy, text=None, answering=False):
            self.send_btn.setEnabled(not busy)
            self.new_btn.setEnabled(not busy)
            self.pic_btn.setEnabled(not busy)
            self.rec_btn.setEnabled(not busy)
            self.stop_btn.setEnabled(answering)
            if text is not None:
                self.status.setText(text)

        def on_ready(self):
            self.set_busy(False, "Ready.")
            self.attach_row.setVisible(self.engine.senses)
            self.show_pending()
            self.input.setFocus()
            if demo is not None:
                if demo_picture:
                    self.add_pending(lambda: load_picture(demo_picture))
                if demo_recording:
                    self.add_pending(lambda: attachment("recording", demo_recording))
                self.input.setPlainText(demo)
                self.on_send()

        def on_load_failed(self, text):
            self.set_busy(True, "Gemma could not start.")
            if demo is not None:
                print("Gemma: " + text, file=sys.stderr)
                QTimer.singleShot(0, self.close)
                return
            QMessageBox.warning(self, "Gemma", text)

        def render(self):
            parts = []
            shown = self.messages + ([{"role": "assistant", "content": self.partial + " ▌"}]
                                     if self.partial is not None else [])
            for m in shown:
                who = "You" if m["role"] == "user" else "Gemma"
                files = "".join(f"\n\n*[{a['kind'].capitalize()}: {a['name']}]*"
                                for a in m.get("attachments") or [])
                parts.append(f"**{who}**{files}\n\n{m['content']}")
            self.view.setMarkdown("\n\n---\n\n".join(parts))
            self.view.moveCursor(QTextCursor.MoveOperation.End)

        def on_send(self):
            text = self.input.toPlainText().strip()
            if not self.send_btn.isEnabled():
                return
            if not text and self.pending:
                kinds = {a["kind"] for a in self.pending}
                text = "Describe this picture." if kinds == {"picture"} else "What is said in this recording?"
            if not text:
                return
            self.input.clear()
            attached, self.pending = self.pending, []
            self.show_pending()
            self.messages.append({"role": "user", "content": text, "attachments": attached})
            self.partial = ""
            self.started = time.monotonic()
            waiting = "Gemma is thinking…"
            if any(a["kind"] == "picture" for a in attached):
                waiting = "Gemma is looking at the picture. This can take several minutes…"
            elif attached:
                waiting = "Gemma is listening to the recording…"
            self.set_busy(True, waiting, answering=True)
            self.answer = Answer(self.engine, list(self.messages))
            self.answer.piece.connect(self.on_piece)
            self.answer.finished_ok.connect(self.on_done)
            self.answer.failed.connect(self.on_failed)
            self.answer.start()
            self.refresh.start()
            self.render()

        def on_piece(self, p):
            if not self.partial:
                self.status.setText("Gemma is answering…")
            self.partial += p

        def finish(self):
            self.refresh.stop()
            if self.partial:
                self.messages.append({"role": "assistant", "content": self.partial})
            elif self.messages and self.messages[-1]["role"] == "user":
                self.messages.pop()  # nothing was answered; do not leave a dangling question
            self.partial = None
            self.render()

        def on_done(self):
            stopped = bool(self.answer and self.answer.cancelled)
            self.finish()
            secs = time.monotonic() - self.started
            self.set_busy(False, "Stopped." if stopped else f"Answered in {secs:.0f} seconds.")
            self.input.setFocus()
            if demo is not None:
                if screenshot:
                    self.grab().save(screenshot)
                QTimer.singleShot(200, self.close)

        def on_failed(self, text):
            self.finish()
            self.set_busy(False, text)

        def on_stop(self):
            if self.answer:
                self.answer.cancelled = True
            self.engine.cancel()

        def on_new(self):
            self.messages = []
            self.on_clear_pending()
            self.render()
            self.status.setText("Ready.")

        def closeEvent(self, e):
            self.on_stop()
            for t in (self.answer, self.loader):
                if t is not None:
                    t.wait(3000)
            self.engine.stop()
            super().closeEvent(e)

    win = Window()
    win.show()
    return app.exec()


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gemma, the assistant that runs on this computer.")
    ap.add_argument("--ask", metavar="QUESTION", help="answer one question on the terminal")
    ap.add_argument("--max-tokens", type=int, default=None)
    ap.add_argument("--isolation", action="store_true",
                    help="list the network devices the assistant can see")
    ap.add_argument("--picture", metavar="FILE", help="with --ask: a picture to ask about")
    ap.add_argument("--recording", metavar="FILE", help="with --ask: a sound recording to ask about")
    ap.add_argument("--demo", metavar="QUESTION", help=argparse.SUPPRESS)
    ap.add_argument("--screenshot", metavar="FILE", help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    try:
        if a.isolation:
            print("network devices visible to the assistant:", isolation_report())
            return 0
        if a.ask:
            ask(a.ask, a.max_tokens, picture=a.picture, recording=a.recording)
            return 0
        return run_window(a.demo, a.screenshot, a.picture, a.recording)
    except GemmaError as e:
        print(f"Gemma: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
