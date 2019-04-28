import sys
import os
from maya import cmds, mel
from qtdocker import dock_window, Docker
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile


module_path = cmds.moduleInfo(path=True, moduleName='Samkit').replace('/','\\')
site_package = os.path.join(module_path, 'pydist\\python-2.7.11.amd64\\Lib\\site-packages')
sys.path.append(site_package)


class DockerMain(Docker):

    CONTROL_NAME = 'samkit_workspcae_control'
    DOCK_LABEL_NAME = 'Samkit'
    UI_PATH = '%s\\ui\\main.ui' % module_path

    def content(self):
        loader = QUiLoader()
        file = QFile(self.UI_PATH)
        file.open(QFile.ReadOnly)
        widget = loader.load(file, self)
        file.close()

        return widget


def setup(*_):
    print('--------Samkit starting--------')

    layout = mel.eval('$tmp = $gAttributeEditorButton').split('|attributeEditorButton')[0]
    height = cmds.formLayout(layout, q=True, height=True) - 1
    btn = cmds.iconTextCheckBox(
        parent=layout,
        width=height,
        height=height,
        image='tool_icon.svg',
        style='iconOnly'
    )
    cmds.formLayout(layout, e=True, width=138)
    cmds.formLayout(layout, e=True, attachForm=[(btn, 'right', 1), (btn, 'top', 1)])

    win = dock_window(DockerMain)
    cmds.inViewMessage(message='Samkit Ready', position='midCenter', fade=True)


cmds.evalDeferred(setup)
