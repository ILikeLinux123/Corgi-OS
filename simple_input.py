# simple_input.py
"""
Corgi OS — readline-free line editor.

A drop-in alternative to pyreadline3 / GNU readline that gives you:
  - up/down arrow command history
  - left/right arrow cursor movement
  - Tab completion (press Tab repeatedly to cycle matches)
  - Backspace / Delete / Home / End

It works by reading raw keypresses itself (no dependency on the host
terminal's readline setup), which is why it behaves consistently in
VS Code's integrated terminal, where pyreadline3/readline is flaky.

Falls back to a plain input() automatically when stdin isn't an
interactive terminal (e.g. piped input), so it's still safe to use
in scripts/tests.
"""

import sys
import os
import contextlib

IS_WINDOWS = os.name == "nt"

if IS_WINDOWS:
    import msvcrt
else:
    import termios
    import tty


class LineEditor:

    def __init__(self, history_file="data/.corgi_history", max_history=500):

        self.history_file = history_file
        self.max_history = max_history
        self.history = self._load_history()
        self.completer = None  # function(word, full_line, word_start) -> list[str]

    def set_completer(self, fn):
        self.completer = fn

    # ------------------------------------------------------------
    # History persistence
    # ------------------------------------------------------------

    def _load_history(self):

        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return [line.rstrip("\n") for line in f if line.strip()]
        except OSError:
            return []

    def save_history(self):

        folder = os.path.dirname(self.history_file) or "."
        os.makedirs(folder, exist_ok=True)

        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                f.write("\n".join(self.history[-self.max_history:]))
        except OSError:
            pass

    def _add_history(self, line):

        if line and (not self.history or self.history[-1] != line):
            self.history.append(line)

    # ------------------------------------------------------------
    # Raw key reading
    # ------------------------------------------------------------

    def _read_key(self):

        if IS_WINDOWS:

            ch = msvcrt.getwch()

            if ch in ("\x00", "\xe0"):

                ch2 = msvcrt.getwch()

                return {
                    "H": "UP",
                    "P": "DOWN",
                    "K": "LEFT",
                    "M": "RIGHT",
                    "S": "DELETE",
                    "G": "HOME",
                    "O": "END",
                }.get(ch2, "")

            return ch

        ch = sys.stdin.read(1)

        if ch == "\x1b":

            ch2 = sys.stdin.read(1)

            if ch2 == "[":

                ch3 = sys.stdin.read(1)

                return {
                    "A": "UP",
                    "B": "DOWN",
                    "C": "RIGHT",
                    "D": "LEFT",
                    "H": "HOME",
                    "F": "END",
                    "3": "DELETE",  # some terminals send ESC [ 3 ~
                }.get(ch3, "")

            return ""

        return ch

    def _raw_mode(self):

        if IS_WINDOWS:
            return contextlib.nullcontext()

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        @contextlib.contextmanager
        def ctx():
            try:
                tty.setcbreak(fd)
                yield
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ctx()

    # ------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------

    def input_line(self, prompt=""):

        # Non-interactive stdin (piped input, tests, etc) — just use input()
        if not sys.stdin.isatty():
            return input(prompt)

        buf = list("")
        cursor = 0
        hist_index = len(self.history)
        stash = ""

        tab_word = None
        tab_matches = []
        tab_pos = 0

        sys.stdout.write(prompt)
        sys.stdout.flush()

        def redraw():
            sys.stdout.write("\r\x1b[K")
            sys.stdout.write(prompt + "".join(buf))
            move_back = len(buf) - cursor
            if move_back > 0:
                sys.stdout.write(f"\x1b[{move_back}D")
            sys.stdout.flush()

        with self._raw_mode():

            while True:

                key = self._read_key()

                if key in ("\r", "\n"):
                    sys.stdout.write("\n")
                    line = "".join(buf)
                    self._add_history(line)
                    return line

                elif key == "\x03":  # Ctrl+C
                    sys.stdout.write("\n")
                    raise KeyboardInterrupt

                elif key == "\x04":  # Ctrl+D on empty line = EOF
                    if not buf:
                        sys.stdout.write("\n")
                        raise EOFError
                    continue

                elif key in ("\x7f", "\x08"):  # Backspace
                    if cursor > 0:
                        del buf[cursor - 1]
                        cursor -= 1
                    redraw()

                elif key == "DELETE":
                    if cursor < len(buf):
                        del buf[cursor]
                    redraw()

                elif key == "LEFT":
                    cursor = max(0, cursor - 1)
                    redraw()

                elif key == "RIGHT":
                    cursor = min(len(buf), cursor + 1)
                    redraw()

                elif key == "HOME":
                    cursor = 0
                    redraw()

                elif key == "END":
                    cursor = len(buf)
                    redraw()

                elif key == "UP":
                    if hist_index > 0:
                        if hist_index == len(self.history):
                            stash = "".join(buf)
                        hist_index -= 1
                        buf = list(self.history[hist_index])
                        cursor = len(buf)
                    redraw()

                elif key == "DOWN":
                    if hist_index < len(self.history):
                        hist_index += 1
                        if hist_index == len(self.history):
                            buf = list(stash)
                        else:
                            buf = list(self.history[hist_index])
                        cursor = len(buf)
                    redraw()

                elif key == "\t":
                    if self.completer:
                        line = "".join(buf[:cursor])
                        word_start = line.rfind(" ") + 1
                        word = line[word_start:]

                        if tab_word != word:
                            tab_matches = sorted(
                                self.completer(word, "".join(buf), word_start)
                            )
                            tab_word = word
                            tab_pos = 0
                        else:
                            tab_pos += 1

                        if tab_matches:
                            match = tab_matches[tab_pos % len(tab_matches)]
                            new_prefix = list("".join(buf)[:word_start] + match)
                            rest = buf[cursor:]
                            buf = new_prefix + rest
                            cursor = len(new_prefix)
                    redraw()

                elif key and key.isprintable():
                    buf.insert(cursor, key)
                    cursor += 1
                    tab_word = None
                    redraw()

                # anything else (unrecognized control sequence) is ignored