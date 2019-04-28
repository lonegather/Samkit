import weakref

import maya.cmds as cmds
from maya.OpenMayaUI import MQtUtil
from shiboken2 import wrapInstance

from PySide2.QtWidgets import QWidget
from PySide2.QtCore import Qt


def dock_window(dialog_class):
    try:
        cmds.deleteUI(dialog_class.CONTROL_NAME)
    except: pass

    # building the workspace control with maya.cmds
    main_control = cmds.workspaceControl(
        dialog_class.CONTROL_NAME,
        ttc=["AttributeEditor", -1],
        iw=300,
        mw=True,
        wp='preferred',
        label=dialog_class.DOCK_LABEL_NAME
    )

    # now lets get a C++ pointer to it using OpenMaya
    control_widget = MQtUtil.findControl(dialog_class.CONTROL_NAME)
    # convert the C++ pointer to Qt object we can use
    control_wrap = wrapInstance(long(control_widget), QWidget)

    # control_wrap is the widget of the docking window and now we can start working with it:
    control_wrap.setAttribute(Qt.WA_DeleteOnClose)
    win = dialog_class(control_wrap)

    # after maya is ready we should restore the window since it may not be visible
    cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))

    # will return the class of the dock content.
    return win


class Docker(QWidget):

    instances = list()
    CONTROL_NAME = 'docker_control'
    DOCK_LABEL_NAME = 'Docker'
    UI_PATH = ''

    @staticmethod
    def delete_instances():
        for ins in Docker.instances:
            try:
                ins.setParent(None)
                ins.deleteLater()
                Docker.instances.remove(ins)
            except: pass
            del ins

    def __init__(self, parent=None):
        super(Docker, self).__init__(parent)

        # let's keep track of our docks so we only have one at a time.
        Docker.delete_instances()
        self.__class__.instances.append(weakref.proxy(self))

        layout = parent.layout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.content())

    def content(self):
        return QWidget()
