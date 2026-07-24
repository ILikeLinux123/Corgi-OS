# main.py
import corgi
from boot import boot
from auth import login

from kernel import Kernel
from system import register_kernel
from shell import Shell



import sys
import traceback
def kernel_panic(error):

    corgi.panic()

    print()

    print("Python error:")
    traceback.print_exception(
        type(error),
        error,
        error.__traceback__
    )

    print()

    print("[ERROR] Corgi OS has halted.")

    sys.exit(1)


def main():

    try:

        kernel = Kernel()
    # Start boot sequence
        boot()


    # Login
        user = login()
        kernel.user = user
        kernel.run_user_startup()

        if user is None:

            return



    # Start kernel


        register_kernel(kernel)
        kernel.user = user
        username = user["username"]

        home = kernel.fs["root"]["home"]

        if username not in home:
            home[username] = {
                "Documents": {},
                "Downloads": {},
                "Desktop": {}
    }

        kernel.cwd = [
            "root",
            "home",
            username
]

        kernel.save_filesystem()

        kernel.info(
            "Kernel loaded"
    )


        kernel.success(
            "System ready"
    )



        print()

        print(
        f"Welcome {user['username']}!"
    )


        if user["admin"]:

            print(
            "Administrator account"
        )
    

        print()


    # Start Corgi Shell 

        shell = Shell(
            kernel,
            user
    )

        shell.start()
        kernel.run_startup()

    except Exception as error:

        kernel_panic(error)


if __name__ == "__main__":

    main()