import maya.cmds as cmds
from PySide.QtGui import QWidget, QVBoxLayout, QSizePolicy
from PySide.QtCore import QFile
from PySide.QtUiTools import QUiLoader
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


module_path = cmds.moduleInfo(path=True, moduleName='Samkit').replace('/', '\\')


def dock_window(dialog_class):
    try:
        cmds.deleteUI(dialog_class.CONTROL_NAME)
    except: pass

    win = dialog_class()
    win.show(dockable=True, area='right', floating=False)

    # will return the class of the dock content.
    return win


class Docker(MayaQWidgetDockableMixin, QWidget):

    instances = list()
    CONTROL_NAME = 'docker_control'
    DOCK_LABEL_NAME = 'Docker'

    def __init__(self, parent=None):
        super(Docker, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.content())

    def content(self):
        return QWidget()


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
