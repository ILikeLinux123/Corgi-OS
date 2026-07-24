# shell.py

class Shell:

    def complete(self, text, state):

        folder = self.kernel.get_current_dir()

        options = []


        for name in folder:

            if name.startswith(text):

                options.append(name)


        if state < len(options):

            return options[state]


        return None

    def __init__(self, kernel, user):

        self.kernel = kernel

        self.user = user

        self.running = True



    def prompt(self):

        path = "/" + "/".join(
            self.kernel.cwd[1:]
    )

        return (
            f"{self.user['username']}"
            "@corgios:"
            f"{path}$ "
    )



    def start(self):

        print(
            "Corgi Shell started!"
        )

        print(
            "Type 'help' for commands."
    )

        print()


        while self.running and self.kernel.running:

            try:

                command = input(
                    self.prompt()
            )


                if command.strip():

                    self.kernel.execute(
                        command
                )


            # Check if a command requested shutdown/reboot
                if not self.kernel.running:

                    self.running = False


            except KeyboardInterrupt:

                print()

                print(
                    "Use exit to quit"
            )