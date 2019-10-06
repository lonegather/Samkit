import os
import json
import pickle
from maya import cmds
from requests.exceptions import ConnectionError


__all__ = [
    'TMP_PATH',
    'MODULE_PATH',
    'OPT_HOST',
    'OPT_USERNAME',
    'OPT_PROJECT',
    'OPT_PROJECT_ID',
    'OPT_PROJECT_ROOT',
    'OPT_WORKSPACE',
    'OPT_COOKIES',
    'AUTH_SUCCESS',
    'AUTH_FAILED',
    'AUTH_ABORT',
    'CONNECT_FAILED',
    'UE_ADD_CHARACTER',
    'UE_EDIT_CHARACTER',
    'UE_ADD_ANIMATION',
    'UE_EDIT_ANIMATION',
    'UE_ADD_SEQUENCE',
    'UE_EDIT_SEQUENCE',
    'clear_ov',
    'login',
    'update',
]

TMP_PATH = os.getenv('TMP')
MODULE_PATH = cmds.moduleInfo(path=True, moduleName='Samkit').replace('/', '\\')
OPT_HOST = 'samkit_host'
OPT_USERNAME = 'samkit_username'
OPT_PROJECT = 'samkit_project'
OPT_PROJECT_ID = 'samkit_project_id'
OPT_PROJECT_ROOT = 'samkit_project_root'
OPT_WORKSPACE = 'samkit_workspace'
OPT_COOKIES = 'samkit_cookies'
AUTH_SUCCESS = 0
AUTH_FAILED = 1
AUTH_ABORT = 2
CONNECT_FAILED = 3
UE_CONNECT = 0
UE_ADD_CHARACTER = 1
UE_EDIT_CHARACTER = 2
UE_ADD_ANIMATION = 3
UE_EDIT_ANIMATION = 4
UE_ADD_SEQUENCE = 5
UE_EDIT_SEQUENCE = 6


def clear_ov():
    cmds.optionVar(remove=OPT_HOST)
    cmds.optionVar(remove=OPT_USERNAME)
    cmds.optionVar(remove=OPT_PROJECT)
    cmds.optionVar(remove=OPT_PROJECT_ID)
    cmds.optionVar(remove=OPT_PROJECT_ROOT)
    cmds.optionVar(remove=OPT_WORKSPACE)
    cmds.optionVar(remove=OPT_COOKIES)


def login(session, host, username, password):
    server = "http://%s/auth/" % host
    kwargs = {
        'username': username,
        'password': password,
    }
    try:
        response = session.post(server, data=kwargs)
        if json.loads(response.text):
            cmds.optionVar(sv=(OPT_USERNAME, json.loads(response.text)['name']))
            cmds.optionVar(sv=(OPT_COOKIES, pickle.dumps(session.cookies)))
            return AUTH_SUCCESS
        else:
            cmds.optionVar(remove=OPT_USERNAME)
            cmds.optionVar(remove=OPT_COOKIES)
            return AUTH_FAILED
    except ConnectionError:
        return CONNECT_FAILED
    except ValueError:
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
