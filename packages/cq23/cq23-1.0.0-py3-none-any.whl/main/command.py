import sys

from run_game.command import run_game

from .utils import restore_cwd


def help_message():
    print("Help me")


@restore_cwd
def route_command():
    command_args = sys.argv[1:]

    if not command_args:
        help_message()
    elif command_args[0].lower() == "run":
        run_game(*command_args[1:])
