
import os
import sys
import time
import subprocess
import platform


def restart():
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "main.py"
    )

    python = sys.executable
    system = platform.system()

    if system == "Windows":
        # Open a new Windows console
        subprocess.Popen([
            python,
            script_path
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)

    elif system == "Linux":
        # Try common Linux terminal emulators
        terminals = [
            ["x-terminal-emulator", "-e"],
            ["gnome-terminal", "--"],
            ["konsole", "-e"],
            ["xfce4-terminal", "-e"],
            ["xterm", "-e"]
        ]

        for terminal in terminals:
            try:
                subprocess.Popen(
                    terminal + [python, script_path],
                    start_new_session=True
                )
                return
            except FileNotFoundError:
                continue

        print("Error: No supported terminal emulator was found.")

    elif system == "Darwin":
        # Open a new macOS Terminal window
        command = f"{python!r} {script_path!r}"
        apple_script = (
            'tell application "Terminal"\n'
            f"activate\n"
            f'do script "{command.replace(chr(34), chr(92) + chr(34))}"\n'
            "end tell"
        )

        subprocess.Popen(["osascript", "-e", apple_script])

    else:
        print(f"Unsupported operating system: {system}")


if __name__ == "__main__":
    time.sleep(1)
    restart()
