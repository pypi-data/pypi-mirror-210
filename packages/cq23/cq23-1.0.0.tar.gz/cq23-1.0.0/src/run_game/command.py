import os
import shutil
import subprocess

from . import docker_tools
from .gcs import run_gcs


def clone_or_pull_repository(repository_url, folder_path):
    if not os.path.exists(folder_path):
        # Clone the repository if the folder doesn't exist
        subprocess.run(["git", "clone", repository_url, folder_path])
    else:
        # Pull the latest changes if the folder already exists
        current_dir = os.getcwd()
        os.chdir(folder_path)
        subprocess.run(["git", "pull"])
        os.chdir(current_dir)
    print("GCS cloned successfully.")


def extract_map_from_command_args(args):
    map_arg = list(filter(lambda x: str(x).startswith("map="), args))
    if not map_arg:
        return None
    if len(map_arg) > 1:
        raise Exception("Multiple `map` arguments provided.")

    # We can also validate the map name here if we want...

    return map_arg[0][4:]


def copy_container_logs(game_files_abs_path, gcs_folder_name):
    src_dir = os.path.join(os.path.join(gcs_folder_name, "src"), "container_logs")
    dst_dir = os.path.join(game_files_abs_path, "replay_files")
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dst_file = os.path.join(dst_dir, filename)
        # Copy the file to the destination directory
        shutil.copy2(src_file, dst_file)


def run_game(*args):
    game_files_dir = ".game_files"
    gcs_folder_name = "gcs"
    gcs_repo = "https://github.com/CALED-Team/game-communication-system.git"

    docker_tools.check_dockerfile_exists()
    docker_tools.build_and_tag_image(docker_tools.get_client_image_tag())

    if not os.path.exists(game_files_dir):
        os.makedirs(game_files_dir)
    os.chdir(game_files_dir)
    game_files_abs_path = os.getcwd()

    clone_or_pull_repository(gcs_repo, gcs_folder_name)
    docker_tools.pull_latest_game_server()
    run_gcs(gcs_folder_name, extract_map_from_command_args(args))
    docker_tools.copy_replay_files(game_files_abs_path)
    copy_container_logs(game_files_abs_path, gcs_folder_name)

    # Go back to the same directory as we were (one up)
    os.chdir(os.path.dirname(os.getcwd()))
