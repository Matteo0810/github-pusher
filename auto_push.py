import requests, os, re
from base64 import b64encode

from github_config import PROFILE_NAME, TOKEN

REPOSITORY_NAME, REPOSITORY_DIR = '', ''
BASE_URL = "https://api.github.com"

# config verifications

if PROFILE_NAME == '' or TOKEN == '':
    raise Exception('Something wrong with the config, please check the config.')

# headers authorization

headers = {
    "Authorization": f'token {TOKEN}',
    "Accept": 'application/vnd.github.v3+json'
}

# get content of the path directory

def get_directory_content(path):
    path = path.replace('\\', '/')
    directories = []

    for path, _, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(path, filename)
            if file_path and not re.search(r'\.git|\.idea|__pycache__', file_path):
                directories.append(file_path.replace('\\', '/'))
    return directories

# get the last commit 

def get_last_commit():
    data = requests.get(f'{BASE_URL}/repos/{PROFILE_NAME}/{REPOSITORY_NAME}/branches/main', headers=headers).json()

    if 'message' in data:
        raise Exception(data['message'])

    return data['commit']['sha']

# convert file to base64 

def to_base64(filename):
    return str(b64encode(open(filename, "rb").read()), "utf-8")

# create blob url of file 

def create_blob(filename):
    global REPOSITORY_NAME 

    data = {
        'content': to_base64(filename),
        'encoding': 'base64'
    }
    response = requests.post(
        f'{BASE_URL}/repos/{PROFILE_NAME}/{REPOSITORY_NAME}/git/blobs', json=data,  headers=headers).json()

    return response['sha']

# create list of files

def create_file_list():
    global REPOSITORY_DIR 

    list = []
    directory = get_directory_content(REPOSITORY_DIR)
    for file in directory:
        list.append({
            "path": file.replace(REPOSITORY_DIR, ''),
            'mode': "100644",
            "type": "blob",
            "sha": create_blob(file)
        })
    return list

# create tree

def create_tree(tree_list, last_commit):
    global REPOSITORY_NAME

    data = {
        'base_tree': last_commit,
        'tree': tree_list
    }
    response = requests.post(
        f'{BASE_URL}/repos/{PROFILE_NAME}/{REPOSITORY_NAME}/git/trees', json=data, headers=headers).json()

    return response['sha']

# create commit 

def create_commit(message, tree, last_commit):
    global REPOSITORY_NAME

    data = {
        'message': message,
        'parents': [
            last_commit
        ],
        'tree': tree
    }
    response = requests.post(
        f'{BASE_URL}/repos/{PROFILE_NAME}/{REPOSITORY_NAME}/git/commits', json=data, headers=headers).json()

    return (response['sha'], response['committer']['name'])

# update the head branch

def update_head(new_commit_sha):
    global REPOSITORY_NAME

    data = {
        "ref": 'refs/heads/main',
        "sha": new_commit_sha
    }
    requests.post(
        f'{BASE_URL}/repos/{PROFILE_NAME}/{REPOSITORY_NAME}/git/refs/heads/main', json=data, headers=headers)

# push on github

def push(message):
    global REPOSITORY_NAME

    print(f'Pushing on {REPOSITORY_NAME}...')

    last_commit = get_last_commit()
    tree = create_tree(create_file_list(), last_commit)
    new_commit_sha = create_commit(message, tree, last_commit)
    update_head(new_commit_sha)

    print(f'Files updated on {REPOSITORY_NAME} !')


# main programm

repository_name = input('Enter the name of the repository: ')
repository_directory = input('Enter the path of the repository directory: ')
commit_message = input('Enter the commit message: (ex: initial commit): ')

if repository_name == '' or repository_directory == '' or commit_message == '':
    raise Exception('Something is wrong, please restart the program.')
    
push(commit_message)
