import os, re

def get_directory_content(path):
    directories = []

    for path, dirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(path, filename)
            if file_path is not None and not re.search(r'\.git|\.idea|__pycache__', file_path):
                directories.append(file_path.replace('\\', '/'))
    return directories
