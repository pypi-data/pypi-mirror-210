import os
import shutil

import docker
from docker.errors import APIError, NotFound

AWS_REGION = "ap-southeast-2"
ECR_REGISTRY = "public.ecr.aws/z3i0q5x8"
GAME_SERVER_ECR_REPO = "cq-game-server"

DOCKER_CLIENT = docker.from_env()


def get_server_image_tag():
    return f"{ECR_REGISTRY}/{GAME_SERVER_ECR_REPO}:latest"


def get_client_image_tag():
    return "cq-local-dev-client:latest"


def pull_latest_game_server():
    print("Pulling the game server...", end=" ")
    game_server_image = get_server_image_tag()
    try:
        DOCKER_CLIENT.images.pull(game_server_image)
        print("Done!")
    except APIError:
        print("Failed to pull the game server!")
        return False
    return True


def check_dockerfile_exists():
    current_dir = os.getcwd()
    dockerfile_path = os.path.join(current_dir, "Dockerfile")

    if os.path.isfile(dockerfile_path):
        print("Dockerfile found.")
    else:
        raise Exception(
            "Dockerfile not found! Make sure you run `cq23_run` from the directory that contains your bot's"
            "Dockerfile."
        )


def build_and_tag_image(image_tag):
    print("Building the image...")
    client = docker.from_env()
    current_dir = os.getcwd()
    dockerfile_path = os.path.join(current_dir, "Dockerfile")

    # Build the Docker image
    image, _ = client.images.build(
        path=current_dir, dockerfile=dockerfile_path, tag=image_tag
    )

    # Print the ID of the built image
    print("Docker image built with ID:", image.id)


def copy_replay_files(game_files_abs_path):
    volume_name = "cq-game-replay"
    local_dir = "replay_files"

    # Ensure the local directory exists and is empty
    os.makedirs(local_dir, exist_ok=True)
    for root, dirs, files in os.walk(local_dir):
        # Delete all files in the current directory
        for file in files:
            os.remove(os.path.join(root, file))
        # Delete all subfolders and their contents
        for dir in dirs:
            shutil.rmtree(os.path.join(root, dir))

    # Get the Docker volume and its associated container
    try:
        DOCKER_CLIENT.volumes.get(volume_name)
    except NotFound:
        print("Volume does not exist! Something has failed.")
        return False

    cmd = ["/bin/sh", "-c", f"cp -r /data/* /{local_dir}"]
    replay_files_dir = os.path.join(game_files_abs_path, local_dir)
    DOCKER_CLIENT.containers.run(
        "busybox",
        cmd,
        detach=True,
        remove=True,
        volumes={
            volume_name: {"bind": "/data", "mode": "ro"},
            replay_files_dir: {"bind": f"/{local_dir}", "mode": "rw"},
        },
    )

    return True
