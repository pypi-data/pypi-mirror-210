import os
import zipfile


def zip_current_directory():
    current_dir = os.getcwd()
    zip_filename = "submission.zip"
    excluded_files = [zip_filename, ".DS_Store", ".gitignore"]
    excluded_folders = [".game_files", ".idea", ".vscode", ".git"]

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(current_dir):

            # Remove bad files
            for excluded_file in excluded_files:
                if excluded_file in files:
                    files.remove(excluded_file)

            # Remove bad folders
            for excluded_folder in excluded_folders:
                if excluded_folder in dirs:
                    dirs.remove(excluded_folder)

            # Put all files in
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=os.path.relpath(file_path, current_dir))

            # Put all folders in
            for folder in dirs:
                folder_path = os.path.join(root, folder)
                arcname = os.path.relpath(folder_path, current_dir)
                zipf.write(folder_path, arcname=arcname)

    print(f"Submission file '{zip_filename}' created successfully!")


def zip(*args):
    zip_current_directory()
