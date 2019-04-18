import requests
from requests.exceptions import ConnectionError

host = "localhost:8000"
session = requests.Session()


# DO NOT USE ADMIN ACCOUNT FOR TESTING
def login(username, password):
    server = "http://%s/auth/" % host
    kwargs = {
        'username': username,
        'password': password,
    }
    try:
        response = session.post(server, data=kwargs)
        return str(response.text)
    except ConnectionError:
        return ""


if __name__ == '__main__':
    print(login('sam', 'serious.2019'))
