import json
import pickle
import requests
from requests.exceptions import ConnectionError
from maya import cmds

import interface
from .utils import *


session = requests.Session()


def access(force=False):
    host = cmds.optionVar(q=OPT_HOST)
    cookies = pickle.loads(cmds.optionVar(q=OPT_COOKIES)) if cmds.optionVar(exists=OPT_COOKIES) else None

    if force or not host:
        print('Get host and user info from user.')
        host, project, prj_id, prj_root, workspace, username, password = interface.get_auth()
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
    for field in filters:
        url += '%s=%s&' % (field, filters[field])
    try:
        return json.loads(requests.get(url).text)
    except ValueError:
        return []
    except ConnectionError:
        return []


def set_data(table, **filters):
    host = cmds.optionVar(q=OPT_HOST)
    return update(session, host, table, **filters)
