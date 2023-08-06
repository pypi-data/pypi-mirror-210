import json
import os
import subprocess
import sys

from . import docker_tools

MATCH_TIMEOUT_SECONDS = 12 * 60  # This should ideally match the one in game worker


def run_gcs(gcs_folder_name, game_map=None):
    gcs_src_dir = os.path.join(gcs_folder_name, "src")
    clients_file_content = [
        {
            "id": "1",
            "name": "Your Code - 1",
            "image": docker_tools.get_client_image_tag(),
        },
        {
            "id": "2",
            "name": "Your Code - 2",
            "image": docker_tools.get_client_image_tag(),
        },
    ]
    clients_file_address = "clients.json"

    with open(os.path.join(gcs_src_dir, clients_file_address), "w") as f:
        f.write(json.dumps(clients_file_content))

    subprocess_args = [
        sys.executable,
        "controller.py",
        docker_tools.get_server_image_tag(),
        clients_file_address,
    ]

    if game_map:
        subprocess_args.append("--server-arg")
        subprocess_args.append("-m " + str(game_map))

    print("Starting the game...")
    subprocess.run(subprocess_args, timeout=MATCH_TIMEOUT_SECONDS, cwd=gcs_src_dir)
    print("Game finished.")

    os.remove(os.path.join(gcs_src_dir, clients_file_address))
