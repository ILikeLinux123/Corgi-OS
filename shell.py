# shell.py

from simple_input import LineEditor


class Shell:

    def __init__(self, kernel, user):

        self.kernel = kernel
        self.user = user
        self.running = True

        self.editor = LineEditor(history_file="data/.corgi_history")
        self.editor.set_completer(self.complete)

    # ==========================
    # Tab completion
    # ==========================

    def complete(self, word, line, word_start):

        if word_start == 0:
            return self._complete_command(word)

        return self._complete_path(word)

    def _complete_command(self, word):

        commands = self.kernel.fs["root"]["SYSTEM"]["commands"]

        names = [
            name[:-3]
            for name in commands
            if name.endswith(".py")
        ]

        return [name for name in names if name.startswith(word)]

    def _complete_path(self, word):

        folder = self.kernel.get_current_dir()

        return [name for name in folder if name.startswith(word)]

    # ==========================
    # Prompt / main loop
    # ==========================

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

        print("Corgi Shell started!")
        print("Type 'help' for commands.")
        print()

        while self.running and self.kernel.running:

            try:

                command = self.editor.input_line(self.prompt())

                if command.strip():
                    self.kernel.execute(command)

                if not self.kernel.running:
                    self.running = False

            except KeyboardInterrupt:

                print()
                print("Use exit to quit")

            except EOFError:

                print()
                self.running = False

        self.editor.save_history()