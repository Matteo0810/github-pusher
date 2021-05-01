import requests
from github_config import AUTH_TOKEN, REPOSITORY_NAME, REPOSITORY_DIR, OWNER_REPOSITORY
from base64 import b64encode
from webhook import sendWebhook
from github_directory import get_directory_content
from progress_bar import progress

# base url

BASE_URL = "https://api.github.com"

# verifications

if AUTH_TOKEN == '' or REPOSITORY_DIR == '' or OWNER_REPOSITORY == '' or REPOSITORY_NAME == '':
    raise Exception('Something wrong with the config, please check the config.')

# headers authorization

headers = {
    "Authorization": f'token {AUTH_TOKEN}',
    "Accept": 'application/vnd.github.v3+json'
}

# get the last commit 

def get_last_commit():
    progress('Getting last commit')
    data = requests.get(f'{BASE_URL}/repos/{OWNER_REPOSITORY}/{REPOSITORY_NAME}/branches/main', headers=headers).json()

    if 'message' in data:
        raise Exception(data['message'])

    return data['commit']['sha']

# convert file to base64 

def toBase64(filename):
    return str(b64encode(open(filename, "rb").read()), "utf-8")

# create blob url of file 

def create_blob(filename):
    data = {
        'content': toBase64(filename),
        'encoding': 'base64'
    }
    response = requests.post(
        f'{BASE_URL}/repos/{OWNER_REPOSITORY}/{REPOSITORY_NAME}/git/blobs', json=data,  headers=headers).json()

    return response['sha']

# create list of files

def create_file_list():
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
    progress('Creating tree')
    data = {
        'base_tree': last_commit,
        'tree': tree_list
    }
    response = requests.post(
        f'{BASE_URL}/repos/{OWNER_REPOSITORY}/{REPOSITORY_NAME}/git/trees', json=data, headers=headers).json()

    return response['sha']

# create commit 

def create_commit(message, tree, last_commit):
    progress('Create commit')
    data = {
        'message': message,
        'parents': [
            last_commit
        ],
        'tree': tree
    }
    response = requests.post(
        f'{BASE_URL}/repos/{OWNER_REPOSITORY}/{REPOSITORY_NAME}/git/commits', json=data, headers=headers).json()

    return (response['sha'], response['committer']['name'])

# update the head branch

def update_head(new_commit_sha):
    progress('Updating head...')
    data = {
        "ref": 'refs/heads/main',
        "sha": new_commit_sha
    }
    requests.post(
        f'{BASE_URL}/repos/{OWNER_REPOSITORY}/{REPOSITORY_NAME}/git/refs/heads/main', json=data, headers=headers)

# push on github

def push(message):
    print(f'Pushing on {REPOSITORY_NAME}...')
    last_commit = get_last_commit()
    tree = create_tree(create_file_list(), last_commit)
    new_commit_sha, pusher_name = create_commit(message, tree, last_commit)
    update_head(new_commit_sha)
    sendWebhook(pusher_name, REPOSITORY_NAME,  message)
    print(f'Files updated on {REPOSITORY_NAME} !')


#####################
### INPUT SECTION ###
#####################

message = input('Enter the commit message: (ex: initial commit): ')

if message != '':
    push(message)
else:
    raise Exception('Message cannot be empty, please fill it.')
