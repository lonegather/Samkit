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


def update(table, **fields):
    server = "http://%s/api" % host
    url = "{server}/{table}".format(**locals())
    kwargs = {'data': {}}
    for field in fields:
        if field == 'file':
            kwargs['files'] = fields[field]
        else:
            kwargs['data'][field] = fields[field]

    try:
        session.post(url, **kwargs)
        return True
    except ConnectionError:
        return False


if __name__ == '__main__':
    print(login(u'sam', u'sn25184369'))
    # update('project', id='74bb0d9a-5394-40e1-a63d-8deb31f3abb8', fps='24')
