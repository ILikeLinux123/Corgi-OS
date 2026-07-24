# terminal.py
"""
Corgi OS Terminal Colors
"""


class Colors:

    RESET = "\033[0m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"



def error(message):

    print(
        f"{Colors.RED}[ERROR]{Colors.RESET} {message}"
    )



def warning(message):

    print(
        f"{Colors.YELLOW}[WARNING]{Colors.RESET} {message}"
    )



def success(message):

    print(
        f"{Colors.GREEN}[ OK ]{Colors.RESET} {message}"
    )



def info(message):

    print(
        f"{Colors.CYAN}[INFO]{Colors.RESET} {message}"
    )