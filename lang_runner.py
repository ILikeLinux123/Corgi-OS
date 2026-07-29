import subprocess
import os
import sys
import tempfile
from corgi import SAD


def fail(message, details=""):
    print(SAD)
    print("Corgi could not complete the task.")
    print()
    print("Reason:")
    print(message)

    if details:
        print()
        print("Details:")
        print(details)

def print_info(*args, **kwargs):
    print("Corgi Language Runner")
    print("=====================")
    print("Usage:")
    print("  c <file.c>")
    print("  cpp <file.cpp>")
    print("  rust <file.rs>")
    print("  python <file.py>")
def run_process(command, cwd=None):

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            fail(
                "The program returned an error code.",
                result.stderr or result.stdout
            )
            return False

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr)

        return True


    except FileNotFoundError:
        fail(
            f"Command not found: {command[0]}",
            "The required compiler or program is not installed."
        )
        return False


    except Exception as e:
        fail(
            "Unexpected error.",
            str(e)
        )
        return False



def run_language(language, filename, args):

    if not os.path.exists(filename):
        fail(
            "File does not exist.",
            filename
        )
        return


    if language == "c":

        output = "program"

        if sys.platform == "win32":
            output += ".exe"

        if run_process([
            "gcc",
            filename,
            "-o",
            output
        ]):
            run_process(
                ["./" + output] + args
            )


    elif language == "cpp":

        output = "program"

        if sys.platform == "win32":
            output += ".exe"

        if run_process([
            "g++",
            filename,
            "-o",
            output
        ]):
            run_process(
                ["./" + output] + args
            )


    elif language == "rust":

        output = "program"

        if sys.platform == "win32":
            output += ".exe"

        if run_process([
            "rustc",
            filename,
            "-o",
            output
        ]):
            run_process(
                ["./" + output] + args
            )


    elif language == "python":

        run_process(
            ["python3", filename] + args
        )


    else:

        fail(
            "Unknown language.",
            language
        )
def run_file(language, content, filename, args=None):

    if args is None:
        args = []

    temp_dir = tempfile.mkdtemp()

    ext = {
        "c": ".c",
        "cpp": ".cpp",
        "rust": ".rs",
        "csharp": ".cs"
    }.get(language)

    if ext is None:
        print("Unknown language")
        return


    source = os.path.join(
        temp_dir,
        filename
    )

    with open(source, "w", encoding="utf-8") as f:
        f.write(content)


    output = os.path.join(
        temp_dir,
        "program"
    )


    try:

        if language == "c":
            compile_cmd = [
                "gcc",
                source,
                "-o",
                output
            ]

        elif language == "cpp":
            compile_cmd = [
                "g++",
                source,
                "-o",
                output
            ]

        elif language == "rust":
            compile_cmd = [
                "rustc",
                source,
                "-o",
                output
            ]


        result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True
        )


        if result.returncode != 0:
            print(SAD)
            print("Compilation failed:")
            print(result.stderr)
            return


        run = subprocess.run(
            [output] + args,
            capture_output=True,
            text=True
        )


        if run.returncode != 0:
            print(SAD)
            print("Program crashed:")
            print(run.stderr)
            return


        print(run.stdout)


    except FileNotFoundError as e:
        print(SAD)
        print("Missing compiler:")
        print(e)