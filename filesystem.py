# filesystem.py
"""
Corgi OS Virtual Filesystem
"""

import json
import os


SAVE_FILE = "corgi_filesystem.json"



class FileSystem:


    def __init__(self):

        self.fs = self.load()

        self.current = [
            "home",

        ]



    def default_fs(self):

        return {

            "home": {


            },


            "system": {

                "logs": {},

                "packages": {}

            },


            "programs": {}

        }



    def load(self):

        if os.path.exists(SAVE_FILE):

            try:

                with open(
                    SAVE_FILE,
                    "r"
                ) as f:

                    return json.load(f)


            except:

                pass


        return self.default_fs()



    def save(self):

        with open(
            SAVE_FILE,
            "w"
        ) as f:

            json.dump(
                self.fs,
                f,
                indent=4
            )



    def get_current(self):

        folder = self.fs


        for item in self.current:

            folder = folder[item]


        return folder



    def path(self):

        return "/" + "/".join(
            self.current
        )



    def ls(self):

        return list(
            self.get_current().keys()
        )



    def exists(self, name):

        return name in self.get_current()



    def mkdir(self, name):

        folder = self.get_current()

        if name not in folder:

            folder[name] = {}

            self.save()

            return True


        return False



    def touch(self, name):

        folder = self.get_current()

        if name not in folder:

            folder[name] = ""

            self.save()

            return True


        return False



    def write(self, name, text):

        folder = self.get_current()

        folder[name] = text

        self.save()



    def read(self, name):

        folder = self.get_current()

        if name in folder:

            if isinstance(
                folder[name],
                str
            ):

                return folder[name]


        return None



    def remove(self, name):

        folder = self.get_current()

        if name in folder:

            del folder[name]

            self.save()

            return True


        return False



    def cd(self, name):

        if name == "..":

            if len(self.current) > 2:

                self.current.pop()

                return True


            return False



        folder = self.get_current()


        if name in folder:

            if isinstance(
                folder[name],
                dict
            ):

                self.current.append(name)

                return True


        return False



    def tree(self, folder=None, indent=0):

        if folder is None:

            folder = self.fs


        for name, item in folder.items():

            print(
                " " * indent +
                "📁 " +
                name
            )


            if isinstance(
                item,
                dict
            ):

                self.tree(
                    item,
                    indent + 2
                )