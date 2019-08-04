import os
import time
import json
import shutil
from maya import cmds
from pyblish_qml import show

import samcon
from samcon.utils import *


__all__ = [
    'evalDeferred',
    'scriptJob',
    'access',
    'get_data',
    'set_data',
    'getenv',
    'hasenv',
    'local_path_exists',
    'source_path_exists',
    'get_local_path',
    'get_source_path',
    'get_data_path',
    'get_context',
    'get_history',
    'new_file',
    'open_file',
    'revert',
    'merge',
    'sync',
    'checkout',
    'checkin',
    'reference',
    'MODULE_PATH',
    'OPT_HOST',
    'OPT_USERNAME',
    'OPT_PROJECT',
    'OPT_PROJECT_ID',
    'OPT_PROJECT_ROOT',
    'OPT_WORKSPACE',
    'OPT_COOKIES',
]

evalDeferred = cmds.evalDeferred
scriptJob = cmds.scriptJob
access = samcon.access
get_data = samcon.get_data
set_data = samcon.set_data


def getenv(key):
    return cmds.optionVar(q=key)


def hasenv(key):
    return cmds.optionVar(exists=key)


def local_path_exists(task):
    return os.path.exists(get_local_path(task))


def source_path_exists(task):
    return os.path.exists(get_source_path(task))


def get_local_path(task):
    return os.path.realpath(os.path.join(getenv(OPT_WORKSPACE), task['path'].split(';')[0]))


def get_source_path(task):
    return os.path.realpath(os.path.join(getenv(OPT_PROJECT_ROOT), task['path'].split(';')[0]))


def get_data_path(task):
    return os.path.realpath(os.path.join(getenv(OPT_PROJECT_ROOT), task['path'].split(';')[1]))


def get_context(key=None):
    empty_map = {
        'reference': []
    }
    task_info = cmds.fileInfo('samkit_context', q=True)
    task_info = task_info[0].replace(r'\"', '"').replace(r'\\\\', r'\\') if task_info else '{}'
    task = json.loads(task_info)
    return task.get(key, empty_map.get(key, None)) if key else task


def get_history(task):
    source_path = get_source_path(task)
    source_base = os.path.basename(source_path)
    source_dir = os.path.dirname(source_path)
    history_dir = os.path.join(source_dir, '.history')
    history_path = os.path.join(history_dir, '%s.json' % source_base)
    try:
        with open(history_path, 'r') as fp:
            history = json.load(fp)
        history['history'].sort(key=lambda e: e['version'], reverse=True)
        result = [{
            'time': history['time'],
            'version': 'v%03d' % len(history['history']),
            'comment': history['comment']
        }]
        for h in history['history']:
            result.append({
                'time': h['time'],
                'version': 'v%03d' % h['version'],
                'comment': h['comment']
            })
        return result if task['id'] == history['id'] else []
    except IOError:
        return []


def new_file():
    cmds.file(new=True, force=True)


def open_file(task):
    current_id = get_context('id')
    if task['id'] == current_id:
        return

    local_path = get_local_path(task)
    if os.path.exists(local_path):
        cmds.file(local_path, open=True, force=True)
        task['reference'] = get_context('reference')
        cmds.fileInfo('samkit_context', json.dumps(task))


def revert(task):
    context = get_context('id')
    if task['id'] == context:
        new_file()
    samcon.set_data('task', id=task['id'], owner='')


def merge(task):
    refs = get_context('reference')
    task['reference'] = refs
    local_path = get_local_path(task)
    cmds.fileInfo('samkit_context', json.dumps(task))
    cmds.file(rename=local_path)
    cmds.file(save=True, type='mayaAscii')


def sync(task, version):
    local_path = get_local_path(task)
    source_path = get_source_path(task)
    source_base = os.path.basename(source_path)
    history_dir = os.path.join(os.path.dirname(source_path), '.history')
    version_path = source_path if version == 'latest' else os.path.join(history_dir, '%s.%s' % (source_base, version))

    shutil.copyfile(version_path, local_path)
    open_file(task)


def checkout(task):
    samcon.set_data('task', id=task['id'], owner=getenv(OPT_USERNAME))
    task['owner'] = getenv(OPT_USERNAME)

    source_path = get_source_path(task)
    local_path = get_local_path(task)
    current_path = cmds.file(q=True, sn=True)

    basedir = os.path.dirname(source_path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    if not os.path.exists(source_path):
        if current_path:
            cmds.file(save=True)
        cmds.file(new=True, force=True)
        cmds.fileInfo('samkit_context', json.dumps(task))
        cmds.file(rename=source_path)
        cmds.file(save=True, type='mayaAscii')
        if current_path:
            cmds.file(current_path, open=True, force=True)
        else:
            cmds.file(new=True, force=True)

    source_base = os.path.basename(source_path)
    source_dir = os.path.dirname(source_path)
    history_dir = os.path.join(source_dir, '.history')
    history_path = os.path.join(history_dir, '%s.json' % source_base)

    if not os.path.exists(history_path):
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        history = {
            'id': task['id'],
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'comment': 'Initialization',
            'history': []
        }
    else:
        with open(history_path, 'r') as fp:
            history = json.load(fp)

    with open(history_path, 'w') as fp:
        json.dump(history, fp, indent=2)

    basedir = os.path.dirname(local_path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)

    shutil.copyfile(source_path, local_path)


def checkin(submit_list):
    submit_str = json.dumps(submit_list)
    cmds.optionVar(sv=('samkit_submit', submit_str))
    show()


def reference(task):
    context = get_context()
    refs = get_context('reference')
    refs.append(task['id'])
    context['reference'] = refs
    cmds.fileInfo('samkit_context', json.dumps(context))

    source_path = get_source_path(task)
    cmds.file(source_path, reference=True, namespace=task['entity'] + '_' + task['stage'])
