from .rhello import rgreet


def greet():
    """
    A thin wrapper around the rust-greet function

    prints a nice greeting
    """
    rgreet()
