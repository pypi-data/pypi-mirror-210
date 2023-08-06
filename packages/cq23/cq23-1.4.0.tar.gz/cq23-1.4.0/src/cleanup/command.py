import shutil

import docker
from docker.errors import NotFound


def cleanup(*args):
    # Create a Docker client
    client = docker.from_env()

    # Get all containers
    containers = client.containers.list(all=True)

    # Delete containers with names starting with 'cq-'
    for container in containers:
        if container.name.startswith("cq_"):
            print("> Deleting container", container.name)
            container.remove(force=True)

    # Get all images
    images = client.images.list(all=True)

    # Delete images with names starting with 'cq_'
    for image in images:
        for tag in image.tags:
            if tag.startswith("cq_"):
                print("> Deleting image", tag)
                client.images.remove(image.id, force=True)
                break

    # Get the volume
    try:
        volume = client.volumes.get("cq-game-replay")

        # Delete the volume
        print("> Deleting volume cq-game-replay")
        volume.remove()
    except NotFound:
        pass

    print("All CodeQuest containers, images and volumes deleted.")

    try:
        print("Deleting game files...", end=" ", flush=True)
        shutil.rmtree(".game_files")
        print("deleted.")
    except FileNotFoundError:
        print("already deleted.")
