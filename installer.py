import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import requests
import os
import shutil
import threading
import sys


APP_NAME = "Corgi OS Installer"


# ---------------------------------
#  GitHub
# ---------------------------------

GITHUB_API = (
    "https://api.github.com/"
    "repos/ILikeLinux123/"
    "Corgi-OS/"
    "contents/"
)



# ---------------------------------
#  Files
# ---------------------------------

CORE_FILES = {
    "main.py",
    "kernel.py",
    "shell.py",
    "system.py",
    "boot.py",
    "auth.py",
    "logger.py",
    "terminal.py",
    "corgi.py",
    "simple_input.py"
}


ALLOWED_FILES = {
    *CORE_FILES,

    "README.md",
    "LICENSE"
}


ALLOWED_FOLDERS = {
    "commands",
    "apps",
    "SYSTEM"
}



# ---------------------------------
# Licenses
# ---------------------------------

EULA = """
Corgi OS End User License Agreement

By installing Corgi OS you agree:

1. Corgi OS is experimental software.
2. The software is provided as-is.
3. You use it at your own risk.
4. You agree to the MIT License.

🐶 Thank you for using Corgi OS!
"""


MIT = """
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files.

The software is provided "AS IS", without warranty of any kind.
"""



# ---------------------------------
# Local file checker
# ---------------------------------

def copy_local_files(destination):

    installer_folder = os.path.dirname(
        os.path.abspath(__file__)
    )


    missing = []


    for file in CORE_FILES:

        path = os.path.join(
            installer_folder,
            file
        )


        if not os.path.exists(path):

            missing.append(
                file
            )


    # All files exist beside installer

    if not missing:


        for file in CORE_FILES:

            shutil.copy2(

                os.path.join(
                    installer_folder,
                    file
                ),

                os.path.join(
                    destination,
                    file
                )
            )


        return True



    return False



# ---------------------------------
# GitHub downloader
# ---------------------------------

def download_folder(api_url, destination, progress):

    response = requests.get(
        api_url,
        timeout=30
    )


    response.raise_for_status()


    items = response.json()



    for item in items:


        name = item["name"]



        if item["type"] == "file":


            if name not in ALLOWED_FILES:

                continue



            output = os.path.join(
                destination,
                name
            )



            data = requests.get(

                item["download_url"],

                timeout=30
            )


            data.raise_for_status()



            with open(
                output,
                "wb"
            ) as file:

                file.write(
                    data.content
                )



            progress.step(5)




        elif item["type"] == "dir":



            if name not in ALLOWED_FOLDERS:

                continue



            folder = os.path.join(
                destination,
                name
            )


            os.makedirs(
                folder,
                exist_ok=True
            )



            download_folder(

                item["url"],

                folder,

                progress
            )



# ---------------------------------
# Create launcher
# ---------------------------------

def create_launcher(folder):

    launcher = os.path.join(
        folder,
        "run.py"
    )


    code = r'''
import os
import sys
import subprocess


HERE = os.path.dirname(
    os.path.abspath(__file__)
)


CORGI_FOLDER = os.path.join(
    HERE,
    "Corgi OS Kernel Code"
)


MAIN = os.path.join(
    CORGI_FOLDER,
    "main.py"
)



if not os.path.exists(MAIN):

    print(
        "Corgi OS main.py missing!"
    )

    sys.exit(1)



subprocess.run(

    [
        sys.executable,
        MAIN
    ],

    cwd=CORGI_FOLDER
)
'''


    with open(
        launcher,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            code
        )




# ---------------------------------
# Installer GUI
# ---------------------------------

class Installer:


    def __init__(self, root):

        self.root = root

        root.title(
            APP_NAME
        )

        root.geometry(
            "600x520"
        )

        root.resizable(
            False,
            False
        )


        self.path = tk.StringVar(
            value=os.path.expanduser(
                "~/Corgi OS"
            )
        )


        tk.Label(
            root,
            text="🐶 Corgi OS Installer",
            font=(
                "Arial",
                22,
                "bold"
            )
        ).pack(
            pady=20
        )



        location_frame = tk.Frame(
            root
        )

        location_frame.pack()



        tk.Entry(
            location_frame,
            textvariable=self.path,
            width=45
        ).pack(
            side="left"
        )



        tk.Button(
            location_frame,
            text="Browse",
            command=self.browse
        ).pack(
            side="left",
            padx=5
        )



        self.eula = tk.BooleanVar()

        self.mit = tk.BooleanVar()



        tk.Checkbutton(
            root,
            text="I agree to the Corgi OS EULA",
            variable=self.eula,
            command=self.check
        ).pack(
            pady=5
        )



        tk.Button(
            root,
            text="View EULA",
            command=lambda:
                self.show_text(
                    "EULA",
                    EULA
                )
        ).pack()



        tk.Checkbutton(
            root,
            text="I agree to the MIT License",
            variable=self.mit,
            command=self.check
        ).pack(
            pady=5
        )



        tk.Button(
            root,
            text="View MIT License",
            command=lambda:
                self.show_text(
                    "MIT License",
                    MIT
                )
        ).pack()



        self.status_label = tk.Label(
            root,
            text="Waiting..."
        )

        self.status_label.pack(
            pady=15
        )



        self.progress = ttk.Progressbar(
            root,
            length=400
        )

        self.progress.pack(
            pady=10
        )



        self.install_button = tk.Button(
            root,
            text="Install Corgi OS",
            state="disabled",
            command=self.start_install
        )

        self.install_button.pack(
            pady=10
        )




    # -----------------------------
    # UI Functions
    # -----------------------------


    def status(self, text):

        self.status_label.config(
            text=text
        )

        self.root.update()



    def browse(self):

        folder = filedialog.askdirectory()


        if folder:

            self.path.set(
                folder
            )




    def check(self):

        if (
            self.eula.get()
            and self.mit.get()
        ):

            self.install_button.config(
                state="normal"
            )

        else:

            self.install_button.config(
                state="disabled"
            )




    def show_text(self, title, text):

        window = tk.Toplevel(
            self.root
        )


        window.title(
            title
        )


        box = tk.Text(
            window,
            width=70,
            height=20
        )

        box.pack()


        box.insert(
            "1.0",
            text
        )


        box.config(
            state="disabled"
        )




    # -----------------------------
    # Install
    # -----------------------------


    def start_install(self):

        threading.Thread(
            target=self.install
        ).start()




    def install(self):

        try:


            base = self.path.get()



            kernel_folder = os.path.join(

                base,

                "Corgi OS Kernel Code"

            )



            self.status(
                "Creating folders..."
            )



            os.makedirs(
                kernel_folder,
                exist_ok=True
            )



            self.progress["value"] = 10




            self.status(
                "Checking local installer files..."
            )



            local = copy_local_files(
                kernel_folder
            )



            if local:


                self.status(
                    "Using included Corgi OS files..."
                )



            else:


                self.status(
                    "Missing files detected!"
                )


                self.status(
                    "Downloading from GitHub..."
                )


                download_folder(

                    GITHUB_API,

                    kernel_folder,

                    self.progress

                )




            self.progress["value"] = 80




            self.status(
                "Creating run.py launcher..."
            )



            create_launcher(
                base
            )



            self.progress["value"] = 100



            self.status(
                "Installation complete!"
            )



            messagebox.showinfo(

                "Finished",

                "🐶 Corgi OS installed successfully!"

            )



        except Exception as error:


            messagebox.showerror(

                "Install failed",

                str(error)

            )




# ---------------------------------
# Start program
# ---------------------------------

if __name__ == "__main__":


    root = tk.Tk()


    Installer(
        root
    )


    root.mainloop()
