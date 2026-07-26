"""
Corgi OS Kernel 0.1.4

The kernel handles:
- system messages
- filesystem
- command loading
- command execution
- panic
- default commands
"""

import time
import json
from datetime import datetime
import sys
import terminal
import corgi

from logger import Logger


# ==========================
# Development reset switch
# ==========================

FACTORY_RESET = False

SAVE_FILE = "corgi_fs.json"



class Kernel:
    username = ""
    VERSION = "0.1.4"


    def __init__(self):
        
        self.user = None
        self.logger = Logger()
        self.running = True
        self.start_time = time.time()
        self.boot_time = datetime.now()
        self.services = {}

        self.cwd = [
            "root",


        ]

        self.fs = self.load_filesystem()

        self.run_system_startup()
    def merge_filesystem(self, old, new):

        for name, new_item in new.items():

        # New folder
            if isinstance(new_item, dict):

                if name not in old:

                    old[name] = new_item

                else:

                    self.merge_filesystem(
                        old[name],
                        new_item
                    )


        # New or updated file
            else:

                old[name] = new_item


        return old

    def refresh_filesystem(self):

        self.info(
            "Refreshing system files..."
        )   


        old_fs = self.fs


        new_fs = self.default_filesystem()


        self.fs = self.merge_filesystem(
            old_fs,
            new_fs
    )


        self.save_filesystem()


        self.success(
            "Filesystem refreshed!"
    )
    # ==========================
    # Startup System
    # ==========================

    def run_system_startup(self):

        startup = (
            self.fs
            ["root"]
            ["SYSTEM"]
            .get("STARTUP", {})
        )

        if not startup:
            return


        self.info(
            "Starting system services..."
        )


        for filename, source in startup.items():

            if not filename.endswith(".py"):
                continue


            namespace = {}


            try:

                exec(
                    source,
                    namespace
                )


                if "run" in namespace:

                    namespace["run"](self)


                self.success(
                    f"{filename} started"
                )


            except Exception as e:

                self.error(
                    f"{filename} failed"
                )

                print(e)



    # ==========================
    # User Startup (.pystart)
    # ==========================

    def find_pystart(self, folder, path=""):

        found = []


        for name, item in folder.items():

            current = (
                path + "/" + name
            )


            if isinstance(item, dict):

                found.extend(
                    self.find_pystart(
                        item,
                        current
                    )
                )


            elif name.endswith(".pystart"):

                found.append(
                    (
                        current,
                        item
                    )
                )


        return found



    def run_user_startup(self):

        files = self.find_pystart(
            self.fs
        )


        if not files:
            return


        self.info(
            "Starting user programs..."
        )


        for path, source in files:

            namespace = {}


            try:

                exec(
                    source,
                    namespace
                )
                

                if "run" in namespace:

                    namespace["run"](self)


                self.success(
                    f"{path} started"
                )


            except Exception as e:

                self.error(
                    f"{path} failed"
                )

                print(e)



    # ==========================
    # Filesystem
    # ==========================

    def load_filesystem(self):

        if FACTORY_RESET:

            fs = self.default_filesystem()

            self.save_filesystem(fs)

            return fs



        try:

            with open(
                SAVE_FILE,
                "r"
            ) as file:

                return json.load(file)



        except:

            fs = self.default_filesystem()

            self.save_filesystem(fs)

            return fs



    def save_filesystem(self, fs=None):

        if fs is None:

            fs = self.fs


        with open(
            SAVE_FILE,
            "w"
        ) as file:

            json.dump(
                fs,
                file,
                indent=4
            )



    def default_filesystem(self):

        return {

        "root": {


            "SYSTEM": {
                "UPDATES": {
                  "updates.txt": """
                  
                  """
                },
                "STARTUP": {

            },

                "commands": {


                    "help.py": """
def run(corgi,args):

    commands = corgi.fs["root"]["SYSTEM"]["commands"]

    print("🐶 Corgi OS Commands")
    print("-------------------")

    for command in sorted(commands):

        print(command.replace(".py",""))

""",


                    "pwd.py": """
def run(corgi,args):

    print(corgi.path())

""",

                    "refresh.py": """
def run(corgi,args):

    corgi.refresh_filesystem()

""",

"ls.py": """
def resolve_path(corgi, path):

    if path == "/":

        return ["root"]


    if path.startswith("/"):

        parts = path.strip("/").split("/")


        if parts[0] == "root":

            parts.pop(0)


        return ["root"] + parts


    return corgi.cwd + path.split("/")



def run(corgi,args):

    target = args.strip()


    if target:

        path = resolve_path(
            corgi,
            target
        )

        folder = corgi.fs


        try:

            for part in path:

                folder = folder[part]


        except KeyError:

            print(
                "ls: folder not found"
            )

            return


    else:

        folder = corgi.get_current_dir()



    if not folder:

        print("(empty)")

        return



    for item in folder:

        print(item)

""",


"cd.py": """
def resolve_path(corgi, path):

    # Home shortcut
    if path == "~":

        return [
            "root",
            "home",
            corgi.user["username"]
        ]


    # Root directory
    if path == "/":

        return [
            "root"
        ]


    # Absolute paths
    if path.startswith("/"):

        parts = path.strip("/").split("/")


        if parts[0] == "root":

            parts.pop(0)


        return [
            "root"
        ] + parts



    # Relative paths
    return corgi.cwd + path.split("/")



def run(corgi, args):

    target = args.strip()


    if not target:

        print(
            corgi.path()
        )

        return



    if target == "..":

        if len(corgi.cwd) > 1:

            corgi.cwd.pop()

        return



    new_path = resolve_path(
        corgi,
        target
    )


    folder = corgi.fs


    try:

        for part in new_path:

            folder = folder[part]


        if isinstance(folder, dict):

            corgi.cwd = new_path

        else:

            print(
                "cd: not a directory"
            )


    except KeyError:

        print(
            "cd: folder not found"
        )
""",
                    "git.py": """




import urllib.request
import zipfile
import io
import os


def run(corgi, args):

    parts = args.split()


    if len(parts) < 2 or parts[0] != "clone":

        print(
            " Usage: git clone <github url>"
        )

        return


    url = parts[1]

    clone(corgi, url)



def clone(corgi, url):

    try:

        print()
        print("🐶 Corgi Git")
        print()

        print("[ OK ] Connecting to GitHub...")


        parts = url.rstrip("/").split("/")

        owner = parts[-2]

        repo = parts[-1]


        zip_url = (
            f"https://github.com/"
            f"{owner}/{repo}"
            f"/archive/refs/heads/main.zip"
        )


        print("[ OK ] Downloading repository...")


        data = urllib.request.urlopen(
            zip_url
        ).read()



        archive = zipfile.ZipFile(
            io.BytesIO(data)
        )


        print("[ OK ] Importing files...")


        folder = repo


        fs = corgi.get_current_dir()


        if folder not in fs:

            fs[folder] = {}



        for file in archive.namelist():

            if file.endswith("/"):

                continue


            name = file.split(
                "/",
                1
            )[1]


            content = archive.read(
                file
            ).decode(
                errors="ignore"
            )


            add_file(
                fs[folder],
                name,
                content
            )



        print()
        print(
            " Clone complete!"
        )



    except Exception as e:

        print(
            "[ERROR] Clone failed:"
        )

        print(e)




def add_file(folder, path, content):

    parts = path.split("/")


    current = folder


    for part in parts[:-1]:

        if part not in current:

            current[part] = {}


        current = current[part]



    current[parts[-1]] = content
""",
"exit.py": """
import sys
def run(corgi,args):

    print("🐶 Corgi is going to sleep...")
    sys.exit()
    corgi.running = False

""",


                    "pip.py": """
def run(corgi,args):

    import subprocess
    import sys


    if not args.strip():

        print("usage: pip <command>")

        return


    try:

        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip"
            ]
            +
            args.split()
        )


    except Exception as e:

        print("Pip error:")
        print(e)

""",


                    "paw.py": """
def run(corgi,args):

    packages = {

    "paw indev"

    }


    parts=args.split()



    if not parts:

        print(
'''
🐾 Corgi Paw Package Manager

Commands:

paw list
paw install <package>
paw remove <package>
'''
        )

        return



    command=parts[0]



    if command=="list":

        print("Available packages:")

        for package in packages:

            print(
                "-",
                package
            )



    elif command=="install":

        if len(parts)<2:

            print(
                "paw No workin"
            )

            return


       # name=parts[1]


        #if name not in packages:

         #   print(
          #      "Package not found "
           # )

            #return


        #print(
         #   f"Installing {name}..."
        #)

        #print(
         #   "[ OK ] Installed"
        #)



    #elif command=="remove":

     #   if len(parts)<2:

      #      print(
       #         "paw remove <package>"
        #    )

         #   return


        #print(
         #   f"Removed {parts[1]}"
        #)


    else:

        print(
            "Paw doesnt work right now"
        )

""",
"autologin.py": """
def run(corgi, args):

    import json
    import os


    USER_FILE = "data/users.json"


    username = corgi.user["username"]


    option = args.strip().lower()


    if option not in ["on", "off"]:

        print(
            "Usage: autologin on/off"
        )

        return



    if not os.path.exists(USER_FILE):

        print(
            "[ERROR] Users database not found."
        )

        return



    with open(USER_FILE, "r") as file:

        users = json.load(file)



    if username not in users:

        print(
            "[ERROR] User not found."
        )

        return



    users[username]["autologin"] = (
        option == "on"
    )



    with open(USER_FILE, "w") as file:

        json.dump(
            users,
            file,
            indent=4
        )



    if option == "on":

        print(
            " Automatic login enabled."
        )

    else:

        print(
            " Automatic login disabled."
        )
""",
"neofetch.py": """
def run(corgi,args):

    import platform
    import time
    import os
    import shutil


    print(r'''
      / \\_/\\
 ____/ •ᴥ• )
/         O
\\   (_____/
 /_____/   U
''')


    print("Corgi OS")
    print("=" * 30)


    # OS
    print(
        "OS:",
        platform.system(),
        platform.release()
    )


    # Kernel
    print(
        "Kernel:",
        corgi.VERSION
    )


    # User
    print(
        "User:",
        corgi.cwd[-1]
    )


    # Path
    print(
        "Path:",
        corgi.path()
    )


    # CPU
    print(
        "CPU:",
        platform.processor()
        or "Unknown"
    )


    # Architecture
    print(
        "Architecture:",
        platform.machine()
    )


    # Python
    print(
        "Python:",
        platform.python_version()
    )


    # RAM
    try:

        import psutil

        ram = psutil.virtual_memory()

        print(
            "RAM:",
            f"{ram.used/1024**3:.2f}GB / {ram.total/1024**3:.2f}GB"
        )

    except:

        print(
            "RAM: Install psutil for details"
        )


    # Storage
    try:

        disk = shutil.disk_usage(".")


        print(
            "Storage:",
            f"{disk.used/1024**3:.2f}GB / {disk.total/1024**3:.2f}GB"
        )

    except:

        print(
            "Storage: Unknown"
        )


    # GPU
    gpu="Unknown"


    try:

        import subprocess


        result=subprocess.check_output(
            "wmic path win32_VideoController get name",
            shell=True,
            text=True
        )


        lines=result.splitlines()


        if len(lines)>1:

            gpu=lines[1].strip()


    except:

        pass


    print(
        "GPU:",
        gpu
    )


    # Commands
    print(
        "Commands:",
        len(
            corgi.fs["root"]["SYSTEM"]["commands"]
        )
    )


    print(
        "Uptime:",
        corgi.uptime()
    )


    print("=" * 30)


    print(
        "🐶 Corgi status: Happy and ready"
    )

""",
"reboot.py": """
def run(corgi,args=None):

    import subprocess
    import sys


    print()

    print(
        "🐶 Corgi is rebooting..."
    )


    subprocess.Popen(
        [
            sys.executable,
            "rebooter.py"
        ]
    )


    raise SystemExit

""",
"sudo.py": """
def run(corgi,args):

    import getpass

    try:
        from auth import hash_password

    except ImportError:

        print(
            "sudo: password system unavailable"
        )

        return



    if not args.strip():

        print(
            "usage: sudo <command>"
        )

        return



    if corgi.user is None:

        print(
            "sudo: no user logged in"
        )

        return



    if not corgi.user.get(
        "admin",
        False
    ):

        print(
            "🐶 Corgi says: you are not an administrator."
        )

        return



    password = getpass.getpass(
        "Password: "
    )



    hashed_password = hash_password(
        password
    )



    if hashed_password != corgi.user.get(
        "password"
    ):

        print(
            "Incorrect password."
        )

        return



    print(
        "[sudo] Running as administrator..."
    )


    corgi.execute(
        args
    )

""",


                    "mkdir.py": """
def run(corgi,args):

    name=args.strip()


    if not name:

        print("usage: mkdir <name>")
        return


    folder=corgi.get_current_dir()


    if name in folder:

        print("Already exists")
        return


    folder[name]={}

    print("Directory created ")

""",


                    "touch.py": """
def run(corgi,args):

    name=args.strip()


    if not name:

        print("usage: touch <file>")
        return


    folder=corgi.get_current_dir()

    folder[name]=""

    print("File created")

""",


                    "dog.py": """
def run(corgi,args):

    name=args.strip()

    folder=corgi.get_current_dir()


    if name not in folder:

        print("File not found")
        return


    if isinstance(folder[name],dict):

        print("dog: directory")

        return


    print(folder[name])

""",


                    "echo.py": """
def run(corgi,args):

    print(args)

""",


                    "rm.py": """
def run(corgi,args):

    name=args.strip()

    folder=corgi.get_current_dir()


    if name not in folder:

        print("Not found")

        return


    del folder[name]

    print("Deleted 🗑️")

""",


                    "clear.py": """
def run(corgi,args):

    import os

    os.system(
        "cls" if os.name=="nt" else "clear"
    )

""",


                    "corgi.py": """
import random


def run(corgi,args):

    messages = [

        "Corgi is watching the keyboard 🐶",

        "Corgi has checked the code. Corgi approves.",

        "Corgi is currently doing important Corgi things.",

        "Corgi found a bug. Corgi politely ignored it.",

        "Corgi says: boop.",

    ]


    print(
        random.choice(messages)
    )

""",


                    "nano.py": r"""


import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font as tkfont
import re
import keyword


# ----------------------------------------------------------------------
# Simple Python syntax highlighter (lightweight, regex based)
# ----------------------------------------------------------------------
PY_KEYWORDS = set(keyword.kwlist)

TOKEN_PATTERNS = [
    ("comment", r"#.*"),
    ("string", r"(\"\"\".*?\"\"\"|'''.*?'''|\"[^\"\\n]*\"|'[^'\\n]*')"),
    ("number", r"\b\d+(\.\d+)?\b"),
    ("keyword", r"\b(" + "|".join(re.escape(k) for k in PY_KEYWORDS) + r")\b"),
    ("function", r"\bdef\s+(\w+)"),
]


class LineNumbers(tk.Canvas):


    def __init__(self, master, text_widget, **kwargs):
        super().__init__(master, width=48, highlightthickness=0, **kwargs)
        self.text_widget = text_widget

    def redraw(self, *args):
        self.delete("all")
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(
                40, y, anchor="ne", text=linenum,
                font=self.text_widget.cget("font"),
                fill=self.text_widget.linenum_color if hasattr(self.text_widget, "linenum_color") else "#888888",
            )
            i = self.text_widget.index(f"{i}+1line")


class NanoEditor(tk.Toplevel):
    THEMES = {
        "light": dict(bg="#ffffff", fg="#1e1e1e", insert="#000000",
                      linebg="#f0f0f0", linefg="#888888", cur_line="#eef4ff",
                      select="#cce5ff", status_bg="#e8e8e8", menu_bg="#f5f5f5"),
        "dark": dict(bg="#1e1e1e", fg="#d4d4d4", insert="#ffffff",
                     linebg="#252526", linefg="#7a7a7a", cur_line="#2a2d2e",
                     select="#264f78", status_bg="#007acc", menu_bg="#252526"),
    }

    SYNTAX_COLORS_DARK = dict(keyword="#569cd6", string="#ce9178",
                               comment="#6a9955", number="#b5cea8", function="#dcdcaa")
    SYNTAX_COLORS_LIGHT = dict(keyword="#0000ff", string="#a31515",
                                comment="#008000", number="#098658", function="#795e26")

    def __init__(self, master, filename, initial_content, on_save):
        super().__init__(master)
        self.filename = filename
        self.on_save = on_save
        self.modified = False
        self.theme = "dark"
        self.wrap = "none"
        self.syntax_on = filename.endswith(".py")
        self.font_size = 13

        self.title(f"Corgi Nano — {filename}")
        self.geometry("900x650")
        self.minsize(500, 350)

        self._build_menu()
        self._build_editor()
        self._build_statusbar()
        self._bind_shortcuts()

        # Load initial content
        self.text.insert("1.0", initial_content)
        self.text.edit_reset()  # clear undo history of the initial load
        self.modified = False
        self._update_title()

        self.apply_theme()
        self._on_change()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.text.focus_set()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_menu(self):
        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save            Ctrl+S", command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label="Exit             Ctrl+Q", command=self._on_close)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo            Ctrl+Z", command=lambda: self.text.edit_undo())
        editmenu.add_command(label="Redo            Ctrl+Y", command=lambda: self.text.edit_redo())
        editmenu.add_separator()
        editmenu.add_command(label="Find            Ctrl+F", command=self.open_find)
        editmenu.add_command(label="Replace         Ctrl+H", command=self.open_replace)
        editmenu.add_command(label="Go to Line      Ctrl+G", command=self.goto_line)
        menubar.add_cascade(label="Edit", menu=editmenu)

        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Toggle Theme    Ctrl+T", command=self.toggle_theme)
        viewmenu.add_command(label="Toggle Word Wrap", command=self.toggle_wrap)
        viewmenu.add_command(label="Toggle Syntax Highlight", command=self.toggle_syntax)
        viewmenu.add_command(label="Zoom In         Ctrl+=", command=lambda: self.zoom(1))
        viewmenu.add_command(label="Zoom Out        Ctrl+-", command=lambda: self.zoom(-1))
        menubar.add_cascade(label="View", menu=viewmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Shortcuts / About", command=self.show_help)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)

    def _build_editor(self):
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.editor_font = tkfont.Font(family="Consolas", size=self.font_size)

        self.text = tk.Text(
            container, wrap=self.wrap, undo=True, maxundo=-1,
            font=self.editor_font, borderwidth=0, highlightthickness=0,
            tabs=self._tab_stops(), padx=8, pady=6,
        )
        self.text.linenum_color = "#888888"

        self.linenumbers = LineNumbers(container, self.text)
        self.linenumbers.pack(side="left", fill="y")

        vsb = ttk.Scrollbar(container, orient="vertical", command=self._on_scroll)
        self.text.configure(yscrollcommand=self._on_textscroll)
        vsb.pack(side="right", fill="y")
        self.vsb = vsb

        self.text.pack(side="left", fill="both", expand=True)

        # Tags
        self.text.tag_configure("current_line")
        self.text.tag_configure("found", background="#ffd54f", foreground="#000000")
        self.text.tag_configure("bracket_match", background="#808080")

        for tag, color in self.SYNTAX_COLORS_DARK.items():
            self.text.tag_configure(f"syn_{tag}", foreground=color)

        self.text.bind("<<Modified>>", self._on_modified_flag)
        self.text.bind("<KeyRelease>", self._on_change)
        self.text.bind("<ButtonRelease-1>", self._on_change)
        self.text.bind("<MouseWheel>", self._on_mousewheel)  # windows/mac
        self.text.bind("<Button-4>", self._on_mousewheel)    # linux scroll up
        self.text.bind("<Button-5>", self._on_mousewheel)    # linux scroll down
        self.text.bind("<Configure>", lambda e: self.linenumbers.redraw())
        self.text.bind("<Return>", self._auto_indent)
        self.text.bind("<Tab>", self._insert_spaces)

        self._build_context_menu()

    def _build_context_menu(self):
        self.ctx_menu = tk.Menu(self.text, tearoff=0)
        self.ctx_menu.add_command(label="Cut", command=lambda: self.text.event_generate("<<Cut>>"))
        self.ctx_menu.add_command(label="Copy", command=lambda: self.text.event_generate("<<Copy>>"))
        self.ctx_menu.add_command(label="Paste", command=lambda: self.text.event_generate("<<Paste>>"))
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="Select All", command=lambda: self.text.tag_add("sel", "1.0", "end"))
        self.text.bind("<Button-3>", lambda e: self.ctx_menu.tk_popup(e.x_root, e.y_root))

    def _build_statusbar(self):
        self.status = tk.Frame(self, height=26)
        self.status.pack(fill="x", side="bottom")

        self.pos_label = tk.Label(self.status, text="Ln 1, Col 1", anchor="w", padx=10)
        self.pos_label.pack(side="left")

        self.stats_label = tk.Label(self.status, text="", anchor="w", padx=10)
        self.stats_label.pack(side="left")

        self.msg_label = tk.Label(self.status, text="", anchor="e", padx=10, fg="#4caf50")
        self.msg_label.pack(side="right")

    def _bind_shortcuts(self):
        self.bind("<Control-s>", lambda e: self.save())
        self.bind("<Control-q>", lambda e: self._on_close())
        self.bind("<Control-f>", lambda e: self.open_find())
        self.bind("<Control-h>", lambda e: self.open_replace())
        self.bind("<Control-g>", lambda e: self.goto_line())
        self.bind("<Control-t>", lambda e: self.toggle_theme())
        self.bind("<Control-equal>", lambda e: self.zoom(1))
        self.bind("<Control-plus>", lambda e: self.zoom(1))
        self.bind("<Control-minus>", lambda e: self.zoom(-1))

    # ------------------------------------------------------------------
    # Scrolling / line numbers
    # ------------------------------------------------------------------
    def _on_scroll(self, *args):
        self.text.yview(*args)
        self.linenumbers.redraw()

    def _on_textscroll(self, *args):
        self.vsb.set(*args)
        self.linenumbers.redraw()

    def _on_mousewheel(self, event):
        # Ctrl+Scroll -> zoom, otherwise let default scroll happen
        if event.state & 0x4:  # Control key held
            direction = 1 if getattr(event, "delta", 0) > 0 or event.num == 4 else -1
            self.zoom(direction)
            return "break"
        self.after_idle(self.linenumbers.redraw)

    # ------------------------------------------------------------------
    # Editing helpers
    # ------------------------------------------------------------------
    def _tab_stops(self):
        return ()

    def _insert_spaces(self, event):
        self.text.insert("insert", "    ")
        return "break"

    def _auto_indent(self, event):
        line = self.text.get("insert linestart", "insert")
        indent = re.match(r"[ \t]*", line).group()
        extra = "    " if line.rstrip().endswith(":") else ""
        self.text.insert("insert", "\n" + indent + extra)
        return "break"

    def _on_modified_flag(self, event=None):
        if self.text.edit_modified():
            self.modified = True
            self._update_title()
            self.text.edit_modified(False)

    def _update_title(self):
        star = "*" if self.modified else ""
        self.title(f"Corgi Nano — {self.filename}{star}")

    def _on_change(self, event=None):
        self.linenumbers.redraw()
        self._highlight_current_line()
        self._update_status()
        self._highlight_brackets()
        if self.syntax_on:
            self._highlight_syntax()

    def _highlight_current_line(self):
        self.text.tag_remove("current_line", "1.0", "end")
        self.text.tag_add("current_line", "insert linestart", "insert lineend+1c")

    def _update_status(self):
        row, col = self.text.index("insert").split(".")
        content = self.text.get("1.0", "end-1c")
        lines = content.count("\n") + 1
        words = len(content.split())
        chars = len(content)
        self.pos_label.config(text=f"Ln {row}, Col {int(col)+1}")
        self.stats_label.config(text=f"{lines} lines · {words} words · {chars} chars")

    def _flash(self, msg, color="#4caf50"):
        self.msg_label.config(text=msg, fg=color)
        self.after(2000, lambda: self.msg_label.config(text=""))

    # ------------------------------------------------------------------
    # Bracket matching
    # ------------------------------------------------------------------
    PAIRS = {"(": ")", "[": "]", "{": "}"}

    def _highlight_brackets(self):
        self.text.tag_remove("bracket_match", "1.0", "end")
        idx = self.text.index("insert")
        for offset in (0, -1):
            try:
                ch = self.text.get(f"{idx}{'+' if offset==0 else ''}{'' if offset==0 else offset}c")
            except tk.TclError:
                continue
        # simple check just before cursor
        before = self.text.get("insert-1c", "insert")
        after = self.text.get("insert", "insert+1c")
        for open_b, close_b in self.PAIRS.items():
            if before == open_b or after == open_b:
                pos = "insert-1c" if before == open_b else "insert"
                match = self._find_match(pos, open_b, close_b, forward=True)
                if match:
                    self.text.tag_add("bracket_match", pos, f"{pos}+1c")
                    self.text.tag_add("bracket_match", match, f"{match}+1c")
            if before == close_b or after == close_b:
                pos = "insert-1c" if before == close_b else "insert"
                match = self._find_match(pos, close_b, open_b, forward=False)
                if match:
                    self.text.tag_add("bracket_match", pos, f"{pos}+1c")
                    self.text.tag_add("bracket_match", match, f"{match}+1c")

    def _find_match(self, pos, this_b, other_b, forward=True):
        depth = 0
        idx = pos
        step = "+1c" if forward else "-1c"
        limit = 20000
        while limit > 0:
            limit -= 1
            char = self.text.get(idx)
            if char == this_b:
                depth += 1
            elif char == other_b:
                depth -= 1
                if depth == 0:
                    return idx
            try:
                idx = self.text.index(f"{idx}{step}")
            except tk.TclError:
                break
            if forward and self.text.compare(idx, ">=", "end"):
                break
            if not forward and self.text.compare(idx, "<=", "1.0"):
                break
        return None

    # ------------------------------------------------------------------
    # Syntax highlighting
    # ------------------------------------------------------------------
    def _highlight_syntax(self):
        for tag in ("syn_keyword", "syn_string", "syn_comment", "syn_number", "syn_function"):
            self.text.tag_remove(tag, "1.0", "end")

        content = self.text.get("1.0", "end-1c")
        for name, pattern in TOKEN_PATTERNS:
            tagname = "syn_function" if name == "function" else f"syn_{name}"
            for m in re.finditer(pattern, content, re.DOTALL):
                start = self._offset_to_index(m.start(1) if name == "function" and m.lastindex else m.start())
                end = self._offset_to_index(m.end(1) if name == "function" and m.lastindex else m.end())
                self.text.tag_add(tagname, start, end)
        # keep these tags visually above current_line highlight
        for tag in ("syn_keyword", "syn_string", "syn_comment", "syn_number", "syn_function"):
            self.text.tag_raise(tag, "current_line")

    def _offset_to_index(self, offset):
        return self.text.index(f"1.0+{offset}c")

    def toggle_syntax(self):
        self.syntax_on = not self.syntax_on
        if not self.syntax_on:
            for tag in ("syn_keyword", "syn_string", "syn_comment", "syn_number", "syn_function"):
                self.text.tag_remove(tag, "1.0", "end")
        else:
            self._highlight_syntax()
        self._flash(f"Syntax highlight: {'on' if self.syntax_on else 'off'}")

    # ------------------------------------------------------------------
    # Find / Replace / Goto
    # ------------------------------------------------------------------
    def open_find(self):
        self._search_dialog(replace=False)

    def open_replace(self):
        self._search_dialog(replace=True)

    def _search_dialog(self, replace):
        win = tk.Toplevel(self)
        win.title("Replace" if replace else "Find")
        win.transient(self)
        win.resizable(False, False)

        tk.Label(win, text="Find:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        find_entry = tk.Entry(win, width=30)
        find_entry.grid(row=0, column=1, padx=6, pady=6)
        find_entry.focus_set()

        repl_entry = None
        if replace:
            tk.Label(win, text="Replace:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
            repl_entry = tk.Entry(win, width=30)
            repl_entry.grid(row=1, column=1, padx=6, pady=6)

        def do_find(direction=1):
            self.text.tag_remove("found", "1.0", "end")
            query = find_entry.get()
            if not query:
                return
            start = self.text.index("insert")
            idx = self.text.search(query, start if direction == 1 else "1.0",
                                    stopindex="end" if direction == 1 else start,
                                    forwards=(direction == 1))
            if not idx:
                idx = self.text.search(query, "1.0", stopindex="end")
            if idx:
                end = f"{idx}+{len(query)}c"
                self.text.tag_add("found", idx, end)
                self.text.mark_set("insert", end)
                self.text.see(idx)
            else:
                self._flash("Not found", color="#e57373")
            # highlight all
            count_idx = "1.0"
            while True:
                pos = self.text.search(query, count_idx, stopindex="end")
                if not pos:
                    break
                end = f"{pos}+{len(query)}c"
                self.text.tag_add("found", pos, end)
                count_idx = end

        def do_replace_one():
            query = find_entry.get()
            repl = repl_entry.get()
            sel = self.text.tag_ranges("found")
            if sel:
                self.text.delete(sel[0], sel[1])
                self.text.insert(sel[0], repl)
            do_find()

        def do_replace_all():
            query = find_entry.get()
            repl = repl_entry.get()
            if not query:
                return
            content = self.text.get("1.0", "end-1c")
            new_content = content.replace(query, repl)
            count = content.count(query)
            self.text.delete("1.0", "end")
            self.text.insert("1.0", new_content)
            self._flash(f"Replaced {count} occurrence(s)")
            self._on_change()

        btns = tk.Frame(win)
        btns.grid(row=2, column=0, columnspan=2, pady=8)
        tk.Button(btns, text="Find Next", command=lambda: do_find(1)).pack(side="left", padx=4)
        if replace:
            tk.Button(btns, text="Replace", command=do_replace_one).pack(side="left", padx=4)
            tk.Button(btns, text="Replace All", command=do_replace_all).pack(side="left", padx=4)
        tk.Button(btns, text="Close", command=win.destroy).pack(side="left", padx=4)

        find_entry.bind("<Return>", lambda e: do_find(1))

    def goto_line(self):
        line = simpledialog.askinteger("Go to Line", "Line number:", parent=self)
        if line:
            total = int(self.text.index("end-1c").split(".")[0])
            line = max(1, min(line, total))
            self.text.mark_set("insert", f"{line}.0")
            self.text.see(f"{line}.0")
            self._on_change()

    # ------------------------------------------------------------------
    # Theme / zoom / wrap
    # ------------------------------------------------------------------
    def apply_theme(self):
        t = self.THEMES[self.theme]
        self.text.configure(bg=t["bg"], fg=t["fg"], insertbackground=t["insert"],
                             selectbackground=t["select"])
        self.text.tag_configure("current_line", background=t["cur_line"])
        self.linenumbers.configure(bg=t["linebg"])
        self.text.linenum_color = t["linefg"]
        self.status.configure(bg=t["status_bg"])
        for lbl in (self.pos_label, self.stats_label):
            lbl.configure(bg=t["status_bg"], fg=t["fg"] if self.theme == "light" else "#ffffff")

        colors = self.SYNTAX_COLORS_DARK if self.theme == "dark" else self.SYNTAX_COLORS_LIGHT
        for tag, color in colors.items():
            self.text.tag_configure(f"syn_{tag}", foreground=color)

        self.linenumbers.redraw()

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self._flash(f"Theme: {self.theme}")

    def toggle_wrap(self):
        self.wrap = "word" if self.wrap == "none" else "none"
        self.text.configure(wrap=self.wrap)
        self._flash(f"Word wrap: {'on' if self.wrap == 'word' else 'off'}")

    def zoom(self, direction):
        self.font_size = max(6, min(48, self.font_size + direction))
        self.editor_font.configure(size=self.font_size)
        self.linenumbers.redraw()

    # ------------------------------------------------------------------
    # Save / close
    # ------------------------------------------------------------------
    def save(self):
        content = self.text.get("1.0", "end-1c")
        self.on_save(self.filename, content)
        self.modified = False
        self._update_title()
        self._flash("Saved 🐶")

    def _on_close(self):
        if self.modified:
            answer = messagebox.askyesnocancel(
                "Unsaved changes",
                f"'{self.filename}' has unsaved changes. Save before closing?"
            )
            if answer is None:
                return  # cancel close
            if answer:
                self.save()
        self.destroy()

    def show_help(self):
        messagebox.showinfo(
            "Corgi Nano — Shortcuts",
            "Ctrl+S       Save\n"
            "Ctrl+Q       Exit\n"
            "Ctrl+Z/Y     Undo / Redo\n"
            "Ctrl+F       Find\n"
            "Ctrl+H       Find & Replace\n"
            "Ctrl+G       Go to line\n"
            "Ctrl+T       Toggle dark/light theme\n"
            "Ctrl+=/-     Zoom in/out (or Ctrl+Scroll)\n"
            "Tab          Insert 4 spaces\n"
            "Right-click  Cut/Copy/Paste/Select All\n"
        )


# ----------------------------------------------------------------------
# Public API — matches your original nano.py's run(corgi, args) signature
# ----------------------------------------------------------------------
def run(corgi, args):
    name = args.strip()

    if not name:
        print("usage: nano <file>")
        return

    folder = corgi.get_current_dir()

    # Create the file if it doesn't exist yet
    if name not in folder:
        folder[name] = ""

    if isinstance(folder[name], dict):
        print("Cannot edit directory")
        return

    existing_content = folder[name]  # load existing contents (bugfix vs original)

    def on_save(filename, content):
        folder[filename] = content

    print(f"Opening '{name}' in Corgi Nano (GUI)...")

    root = tk._default_root
    owns_root = False
    if root is None:
        root = tk.Tk()
        root.withdraw()
        owns_root = True

    editor = NanoEditor(root, name, existing_content, on_save)
    editor.grab_set()
    editor.wait_window()

    if owns_root:
        root.destroy()

    print("Closed Corgi Nano 🐶")


# ----------------------------------------------------------------------
# Standalone test harness (lets you run `python nano_gui.py` directly)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    class FakeCorgi:
        def __init__(self):
            self.fs = {"hello.py": "def hello():\n    print('hi')\n", "notes.txt": ""}

        def get_current_dir(self):
            return self.fs

    corgi = FakeCorgi()
    run(corgi, "hello.py")
    print(corgi.fs["hello.py"])
"""

                }

            },


            "home": {



            }

        }

    }



    def save_filesystem(self, fs=None):


        if fs is None:

            fs = self.fs


        with open(
            SAVE_FILE,
            "w"
        ) as file:

            json.dump(
                fs,
                file,
                indent=4
            )



    # ==========================
    # Directory helpers
    # ==========================


    def get_current_dir(self):

        folder = self.fs


        for part in self.cwd:

            folder = folder[part]


        return folder



    def path(self):

        return "/" + "/".join(
            self.cwd
        )



    # ==========================
    # Command system
    # ==========================


    def execute(self, command):


        parts = command.split(
            " ",
            1
        )


        name = parts[0]

        args = ""


        if len(parts) > 1:

            args = parts[1]



        commands = (
            self.fs
            ["root"]
            ["SYSTEM"]
            ["commands"]
        )


        filename = name + ".py"



        if filename not in commands:

            self.error(
                f"{name}: command not found"
            )

            return
        


        source = commands[filename]

        

        try:


            program = {}


            exec(
                source,
                program
            )


            program["run"](
                self,
                args
            )


        except Exception as error:


            self.error(
                f"{name} crashed:"
            )


            print(error)



        self.save_filesystem()



    # ==========================
    # Messages
    # ==========================


    def info(self,message):

        terminal.info(message)

        self.logger.log(
            message,
            "INFO"
        )



    def success(self,message):

        terminal.success(message)

        self.logger.log(
            message,
            "SUCCESS"
        )



    def warning(self,message):

        terminal.warning(message)

        self.logger.log(
            message,
            "WARNING"
        )



    def error(self,message):

        terminal.error(message)

        self.logger.log(
            message,
            "ERROR"
        )



    # ==========================
    # Kernel info
    # ==========================


    def uptime(self):

        return (
            f"{int(time.time()-self.start_time)}s"
        )



    def about(self):

        print()

        print(
            "Corgi OS"
        )

        print(
            f"Kernel: {self.VERSION}"
        )

        print(
            f"Uptime: {self.uptime()}"
        )

        print()



    # ==========================
    # Panic
    # ==========================


    def panic(self, reason):

        self.running = False

        if getattr(self.kernel, "reboot", False):

            print()

            print(
                "Restart requested..."
    )

    # later this will return to bootloader
            print()

        print(
            "="*45
        )

        print(
            " CORGI OS KERNEL PANIC"
        )

        print(
            "="*45
        )


        corgi.panic()


        print()

        print(
            "Reason:"
        )

        print(reason)


        self.logger.log(
            reason,
            "PANIC"
        )


        print()

        print(
            "System halted."
        )

        
