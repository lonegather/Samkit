import os
import json
import shutil
from maya import cmds
from pyblish_qml import show

from samcon.utils import *


__all__ = [
    'evalDeferred',
    'scriptJob',
    'getenv',
    'hasenv',
    'path_exists',
    'get_local_path',
    'get_context',
    'open_file',
    'checkout',
    'reference',
    'show',
]

evalDeferred = cmds.evalDeferred
scriptJob = cmds.scriptJob


def getenv(key):
    return cmds.optionVar(q=key)


def hasenv(key):
    return cmds.optionVar(exists=key)


def path_exists(task):
    path = os.path.realpath(os.path.join(getenv(OPT_WORKSPACE), task['path'].split(';')[0]))
    return os.path.exists(path)


def get_local_path(task):
    return os.path.realpath(os.path.join(getenv(OPT_WORKSPACE), task['path'].split(';')[0]))


def get_source_path(task):
    return os.path.realpath(os.path.join(getenv(OPT_PROJECT_ROOT), task['path'].split(';')[0]))


def get_data_path(task):
    return os.path.realpath(os.path.join(getenv(OPT_PROJECT_ROOT), task['path'].split(';')[1]))


def get_context(key=None):
    task_info = cmds.fileInfo('samkit_context', q=True)
    task_info = task_info[0].replace(r'\"', '"').replace(r'\\\\', r'\\') if task_info else '{}'
    task = json.loads(task_info)
    return task.get(key, None) if key else task


def new_file():
    cmds.file(new=True, force=True)


def open_file(task):
    local_path = os.path.realpath(os.path.join(getenv(OPT_WORKSPACE), task['path'].split(';')[0]))
    if os.path.exists(local_path):
        cmds.file(local_path, open=True, force=True)
        cmds.fileInfo('samkit_context', json.dumps(task))


def checkout(task):
    remote_path = os.path.realpath(os.path.join(getenv(OPT_PROJECT_ROOT), task['path'].split(';')[0]))
    local_path = os.path.realpath(os.path.join(getenv(OPT_WORKSPACE), task['path'].split(';')[0]))

    basedir = os.path.dirname(remote_path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    if not os.path.exists(remote_path):
        cmds.file(new=True, force=True)
        cmds.fileInfo('samkit_context', json.dumps(task))
        cmds.file(rename=remote_path)
        cmds.file(save=True, type='mayaAscii')

    basedir = os.path.dirname(local_path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    shutil.copyfile(remote_path, local_path)


def reference(task):
    pass


def edit(path):
    print(path)
