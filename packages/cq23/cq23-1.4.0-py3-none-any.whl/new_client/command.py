import os
import shutil
import subprocess


def clone_repository(repo_url, repo_directory):
    subprocess_args = ["git", "clone", repo_url, repo_directory]
    try:
        subprocess.run(subprocess_args, check=True)
        print("\nTemplate cloned.")
    except subprocess.CalledProcessError:
        print("Failed.")
        exit(128)


def delete_git_folder(repo_directory):
    current_directory = os.getcwd()
    repo_path = os.path.join(current_directory, repo_directory)
    git_folder = os.path.join(repo_path, ".git")

    shutil.rmtree(git_folder)


def new_client(*args):
    if not args:
        print("You must specify the language for the client: cq23 new python my_bot")
        return

    language_map = {
        "raw": "https://github.com/CALED-Team/codequest23-raw-submission.git",
        "python": "https://github.com/CALED-Team/codequest23-python-submission.git",
    }
    language = args[0]

    if language not in language_map.keys():
        return print(
            "Invalid language selected for the new bot. Language should be one of:",
            "[" + " - ".join(language_map.keys()) + "]",
        )

    if len(args) < 2:
        print(
            "You should specify a name for the new bot. A new folder with this name will be created so make sure"
            " there are no other folders with this name in the current directory. Example: cq23 new python my_bot"
        )
        return
    if len(args) > 2:
        print(
            "Unrecognised arguments were passed. Maybe you chose a name for your client that included spaces? If that"
            ' is the case make sure you wrap the name with double quotes. Example: cq23 new python "my bot"'
        )
        return

    repo_directory = args[1]

    clone_repository(language_map[language], repo_directory)
    delete_git_folder(repo_directory)
    print(
        f"New {language} client created in {repo_directory}. You can now go in the folder and run the game:"
    )
    print(f'> cd "{repo_directory}"')
    print("> cq23 run")
