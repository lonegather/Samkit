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
        host, project, prj_id, username, password = interface.get_auth()
        if host == '*':
            return AUTH_ABORT
        return login(session, host, project, prj_id, username, password) if host else CONNECT_FAILED
    else:
        print('Retrieve host and cookies from optionVar.')
        if not cookies:
            return AUTH_FAILED
        session.cookies.update(cookies)
        try:
            if not json.loads(session.get("http://%s/auth/" % host).text):
                cmds.optionVar(remove=OPT_COOKIES)
                return AUTH_FAILED
            else:
                return AUTH_SUCCESS
        except ConnectionError:
            cmds.optionVar(remove=OPT_HOST)
            cmds.optionVar(remove=OPT_PROJECT)
            cmds.optionVar(remove=OPT_PROJECT_ID)
            cmds.optionVar(remove=OPT_COOKIES)
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
