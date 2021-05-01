import requests
from github_config import WEBHOOK_URL

def sendWebhook(username, repository, commit):
    data = {
        "content": None,
        "embeds": [
            {
                "title": f'Update sur le répertoire {repository} !',
                "description": f'Contenu du commit \n `{commit}`',
                "url": "https://github.com/Matteo0810/poke-strat",
                "color": 15748172,
                "author": {
                    "name": username
                }
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=data)
