import sys

from check.command import check
from cleanup.command import cleanup
from new_client.command import new_client
from run_game.command import run_game
from zip.command import zip

from .utils import restore_cwd


def help_message():
    message = (
        "Available commands:\n\n"
        + "> cq23 new python my_bot\n"
        + "> cq23 run\n"
        + "> cq23 run map=<map name>\n"
        + "> cq23 zip\n"
        + "> cq23 check\n"
        + "> cq23 cleanup\n\n"
        + "If you need help with the competition, post a message in Discord or email us at info@codequest.club."
    )
    print(message)


@restore_cwd
def route_command():
    command_args = sys.argv[1:]

    first_arg_mapping = {
        "new": new_client,
        "run": run_game,
        "cleanup": cleanup,
        "zip": zip,
        "check": check,
    }

    if not command_args or command_args[0].lower() not in first_arg_mapping.keys():
        help_message()
    else:
        first_arg_mapping[command_args[0].lower()](*command_args[1:])
