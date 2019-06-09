import os
import shutil

from connection.utils import *
from .plugins import *


def open_file(path):
    local_path = os.path.realpath(os.path.join(cmds.optionVar(q=OPT_WORKSPACE), path))
    if os.path.exists(local_path):
        cmds.file(local_path, open=True, force=True)


def checkout(task):
    remote_path = os.path.realpath(os.path.join(cmds.optionVar(q=OPT_PROJECT_ROOT), task['path']))
    local_path = os.path.realpath(os.path.join(cmds.optionVar(q=OPT_WORKSPACE), task['path']))

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


def checkin():
    import pyblish_qml
    pyblish.api.register_gui('pyblish_qml')
    pyblish.api.deregister_all_plugins()
    pyblish.api.register_plugin(EntityCollector)
    pyblish.api.register_plugin(ModelHistoryValidator)
    pyblish_qml.settings.WindowTitle = 'Submit Assistant'
    pyblish_qml.settings.WindowPosition = [500, 100]
    pyblish_qml.settings.WindowSize = [800, 600]
    pyblish_qml.show()


def reference(task):
    pass


def edit(path):
    print(path)
