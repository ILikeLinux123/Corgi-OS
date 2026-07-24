import time
import subprocess
import sys
import os


time.sleep(1)


subprocess.Popen(
    [
        sys.executable,
        os.path.join(
            os.getcwd(),
            "main.py"
        )
    ],
    creationflags=subprocess.CREATE_NEW_CONSOLE
)