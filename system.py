# system.py
"""
Corgi OS System API

This is the bridge between programs/commands
and the kernel.

Programs should use this instead of directly
importing terminal, logger, or corgi.
"""


_current_kernel = None



def register_kernel(kernel):

    global _current_kernel

    _current_kernel = kernel



def get_kernel():

    if _current_kernel is None:

        raise RuntimeError(
            "Corgi OS kernel is not running!"
        )

    return _current_kernel



def info(message):

    get_kernel().info(message)



def success(message):

    get_kernel().success(message)



def warning(message):

    get_kernel().warning(message)



def error(message):

    get_kernel().error(message)



def panic(message):

    get_kernel().panic(message)

def shutdown():

    global _current_kernel

    if _current_kernel:

        _current_kernel.running = False