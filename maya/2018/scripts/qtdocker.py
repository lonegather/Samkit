from maya import cmds
from maya.OpenMayaUI import MQtUtil
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import Qt, QFile
from PySide2.QtUiTools import QUiLoader
from shiboken2 import wrapInstance


class Docker(MayaQWidgetDockableMixin, QWidget):

    instance = None
    CONTROL_NAME = 'docker_control'
    DOCK_LABEL_NAME = 'Docker'

    @classmethod
    def setup(cls, restore=False):
        ''' When the control is restoring, the workspace control has already been created and
            all that needs to be done is restoring its UI.
        '''
        if restore:
            # Grab the created workspace control with the following.
            restoredControl = MQtUtil.getCurrentParent()

        if cls.instance is None:
            print('Creating mixin widget', cls.CONTROL_NAME)
            cls.instance = cls()
            cls.instance.setObjectName(cls.CONTROL_NAME)

        if restore:
            print('Restoring mixin widget', cls.CONTROL_NAME)
            # Add custom mixin widget to the workspace control
            mixinPtr = MQtUtil.findControl(cls.CONTROL_NAME)
            MQtUtil.addWidgetToMayaLayout(long(mixinPtr), long(restoredControl))
        else:
            print('Creating workspace control', cls)
            # Create a workspace control for the mixin widget by passing all the needed parameters.
            cls.instance.show(
                dockable=True,
                height=600,
                width=480,
                label=cls.DOCK_LABEL_NAME,
                uiScript='%s.setup(restore=True)' % cls
            )

        return cls.instance

    def __init__(self, parent=None):
        super(Docker, self).__init__(parent=parent)
        self.setWindowTitle(self.DOCK_LABEL_NAME)
        self.setAttribute(Qt.WA_DeleteOnClose)


class DockerMain(Docker):

    CONTROL_NAME = 'samkit_docker_control'
    DOCK_LABEL_NAME = 'Samkit'
    UI_PATH = '%s\\ui\\main.ui' % cmds.moduleInfo(path=True, moduleName='Samkit').replace('/', '\\')

    def __init__(self, parent=None):
        super(DockerMain, self).__init__(parent=parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        loader = QUiLoader()
        file = QFile(self.UI_PATH)
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file)
        layout.addWidget(self.ui)
        file.close()

        print("init from DockerMain")
