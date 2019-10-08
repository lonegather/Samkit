import json
import pickle
import socket
from socket import error
import requests
from requests.exceptions import ConnectionError
from maya import cmds

import samgui
from .utils import *


session = requests.Session()


def access(force=False):
    host = cmds.optionVar(q=OPT_HOST)
    project_local = cmds.optionVar(q=OPT_PROJECT_ID)
    project_data = get_data('project')
    project_server = [prj['id'] for prj in project_data]
    cookies = pickle.loads(cmds.optionVar(q=OPT_COOKIES)) if cmds.optionVar(exists=OPT_COOKIES) else None

    if force or not host or (project_local not in project_server):
        print('Get host and user info from user.')
        host, project, prj_id, prj_root, workspace, username, password = samgui.get_auth()
        if host == '*':
            return AUTH_ABORT
        result = login(session, host, username, password) if host else CONNECT_FAILED

        cmds.optionVar(sv=(OPT_HOST, host))
        cmds.optionVar(sv=(OPT_PROJECT, project))
        cmds.optionVar(sv=(OPT_PROJECT_ID, prj_id))
        cmds.optionVar(sv=(OPT_PROJECT_ROOT, prj_root))
        cmds.optionVar(sv=(OPT_WORKSPACE, workspace))

        if result == CONNECT_FAILED:
            clear_ov()

        return result
    else:
        print('Retrieve host and cookies from optionVar.')
        for prj in project_data:
            if prj['id'] == project_local:
                cmds.optionVar(sv=(OPT_PROJECT, prj['info']))
                cmds.optionVar(sv=(OPT_PROJECT_ROOT, prj['root']))
        if not cookies:
            return AUTH_FAILED
        session.cookies.update(cookies)
        try:
            if not json.loads(session.get("http://%s/auth/" % host).text):
                cmds.optionVar(remove=OPT_USERNAME)
                cmds.optionVar(remove=OPT_COOKIES)
                return AUTH_FAILED
            else:
                return AUTH_SUCCESS
        except ConnectionError:
            clear_ov()
            return CONNECT_FAILED


def get_data(table, **filters):
    host = cmds.optionVar(q=OPT_HOST)
    url = 'http://%s/api/%s?' % (host, table)
    for field, value in filters.items():
        url += '{field}={value}&'.format(**locals())
    try:
        return json.loads(requests.get(url).text)
    except ValueError:
        return []
    except ConnectionError:
        return []


def set_data(table, **filters):
    host = cmds.optionVar(q=OPT_HOST)
    return update(session, host, table, **filters)


def ue_command(data):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 8888))
    except error:
        return False
    message = json.dumps(data)
    client.send('{message}\n'.format(**locals()).encode())
    client.close()
    return True
