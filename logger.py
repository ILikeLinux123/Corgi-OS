# logger.py

from datetime import datetime


class Logger:


    def __init__(self):

        self.logs = []



    def log(self, message, level="INFO"):

        self.logs.append({

            "time":
                datetime.now().strftime("%H:%M:%S"),

            "level":
                level,

            "message":
                message
        })



    def show(self):

        if not self.logs:

            print("No logs.")

            return


        for entry in self.logs:

            print(
                f"[{entry['time']}] "
                f"[{entry['level']}] "
                f"{entry['message']}"
            )



    def clear(self):

        self.logs.clear()