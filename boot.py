# boot.py
"""
Corgi OS Bootloader

Handles startup checks and loading the system.
"""

import time

import terminal
import corgi


BOOT_VERSION = "0.1.0"



def boot_step(name):

    try:

        print(
            f"[ OK ] {name}..."
        )

        time.sleep(0.3)

        return True


    except Exception:

        terminal.error(
            f"{name} failed"
        )

        return False



def boot():

    print("=" * 40)

    print(
        "        CORGI OS BOOTLOADER"
    )

    print("=" * 40)

    print()


    print(
        f"Corgi Bootloader v{BOOT_VERSION}"
    )

    print()


    steps = [

        "Checking filesystem",

        "Loading kernel",

        "Loading users",

        "Starting services",

        "Starting terminal"

    ]


    for step in steps:

        if not boot_step(step):

            print()

            corgi.panic()

            return False



    print()


    corgi.show(
        corgi.NORMAL
    )


    print()


    print(
        "Welcome to Corgi OS"
    )

    print()


    return True