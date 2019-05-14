import json
import pickle
from maya import cmds
from requests.exceptions import ConnectionError


__all__ = [
    'MODULE_PATH',
    'OPT_HOST',
    'OPT_USERNAME',
    'OPT_PROJECT',
    'OPT_PROJECT_ID',
    'OPT_COOKIES',
    'AUTH_SUCCESS',
    'AUTH_FAILED',
    'AUTH_ABORT',
    'CONNECT_FAILED',
    'clear_ov',
    'login',
    'update',
]

MODULE_PATH = cmds.moduleInfo(path=True, moduleName='Samkit').replace('/', '\\')
OPT_HOST = 'samkit_host'
OPT_USERNAME = 'samkit_username'
OPT_PROJECT = 'samkit_project'
OPT_PROJECT_ID = 'samkit_project_id'
OPT_COOKIES = 'samkit_cookies'
AUTH_SUCCESS = 0
AUTH_FAILED = 1
AUTH_ABORT = 2
CONNECT_FAILED = 3


def clear_ov():
    cmds.optionVar(remove=OPT_HOST)
    cmds.optionVar(remove=OPT_USERNAME)
    cmds.optionVar(remove=OPT_PROJECT)
    cmds.optionVar(remove=OPT_PROJECT_ID)
    cmds.optionVar(remove=OPT_COOKIES)


# DO NOT USE ADMIN ACCOUNT FOR TESTING
def login(session, host, project, prj_id, username, password):
    server = "http://%s/auth/" % host
    kwargs = {
        'username': username,
        'password': password,
    }
    try:
        response = session.post(server, data=kwargs)
        cmds.optionVar(sv=(OPT_HOST, host))
        cmds.optionVar(sv=(OPT_PROJECT, project))
        cmds.optionVar(sv=(OPT_PROJECT_ID, prj_id))
        if json.loads(response.text):
            cmds.optionVar(sv=(OPT_USERNAME, json.loads(response.text)['name']))
            cmds.optionVar(sv=(OPT_COOKIES, pickle.dumps(session.cookies)))
            return AUTH_SUCCESS
        else:
            cmds.optionVar(remove=OPT_USERNAME)
            cmds.optionVar(remove=OPT_COOKIES)
            return AUTH_FAILED
    except ConnectionError:
        clear_ov()
        return CONNECT_FAILED
    except ValueError:
        clear_ov()
        return CONNECT_FAILED


def update(session, host, table, **fields):
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
