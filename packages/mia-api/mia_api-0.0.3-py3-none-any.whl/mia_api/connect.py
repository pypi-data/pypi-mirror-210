import requests
import json
import os

from mia_api.config_file import APIPATH
from mia_api.utils import response_return


def connect():
    # Retrieve credentials
    username = os.environ.get("MIA_API_USERNAME")
    password = os.environ.get("MIA_API_PASSWORD")
    if username is None or password is None:
        if os.path.exists(os.path.expanduser("~/.mia_api")):
            with open(os.path.expanduser("~/.mia_api")) as f:
                for line in f.readlines():
                    if ":" in line:
                        k, v = line.strip().split(":", 1)
                        if k == "username":
                            username = v.strip()
                        elif k == "password":
                            password = v.strip()
        else:
            error_message = 'No username and/or password provided. ' \
                            'In case of first login please refer to the ' \
                            'procedures described in README'
            raise Exception(error_message)
    tokenpath = APIPATH + '/token'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': '',
        'username': username,
        'password': password,
        'scope': '',
        'client_id': '',
        'client_secret': ''
    }
    try:
        response = requests.request(
            "POST",
            tokenpath,
            headers=headers,
            data=data
        )
    except:
        raise Exception("Mia API not responding. Please contact an admin")
    response_return(response)
    os.environ['MIA_API_TOKEN'] = response.json()["access_token"]
    print(f"{username} successfully connected to MIA API")
