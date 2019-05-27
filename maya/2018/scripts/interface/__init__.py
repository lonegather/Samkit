import os
import json
import requests
from requests.exceptions import ConnectionError
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide2.QtWidgets import QDialog, QWidget, QVBoxLayout, QSizePolicy
from PySide2.QtGui import QImage, QIcon
from PySide2.QtCore import QFile, QObject, Signal, QUrl, Qt
from PySide2.QtUiTools import QUiLoader
from shiboken2 import wrapInstance

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from maya.OpenMayaUI import MQtUtil
from maya import cmds

from connection.utils import *


def get_main_window():
    maya_win_ptr = MQtUtil.mainWindow()
    return wrapInstance(long(maya_win_ptr), QWidget)


def get_auth():
    dialog = AuthDialog(get_main_window())
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_info()
    else:
        return '*', '', '', '', '', '', ''


def setup_ui(container, ui):
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    loader = QUiLoader()
    file = QFile(ui)
    file.open(QFile.ReadOnly)
    container.ui = loader.load(file)
    layout.addWidget(container.ui)
    file.close()


class Docker(MayaQWidgetDockableMixin, QWidget):

    instance = None
    CONTROL_NAME = 'docker_control'
    DOCK_LABEL_NAME = 'Docker'

    @classmethod
    def setup(cls, restore=False):
        if cls.instance is None:
            docker = '%sWorkspaceControl' % cls.CONTROL_NAME
            if cmds.workspaceControl(docker, exists=True):
                cmds.deleteUI(docker)
            cls.instance = cls()
            cls.instance.setObjectName(cls.CONTROL_NAME)

        if restore:
            restored_control = MQtUtil.getCurrentParent()
            mixin_ptr = MQtUtil.findControl(cls.CONTROL_NAME)
            MQtUtil.addWidgetToMayaLayout(long(mixin_ptr), long(restored_control))
        else:
            cls.instance.show(
                area='right',
                dockable=True,
                label=cls.DOCK_LABEL_NAME,
                uiScript='%s.setup(restore=True)' % cls
            )

        return cls.instance

    def __init__(self, parent=None):
        super(Docker, self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setWindowTitle(self.DOCK_LABEL_NAME)
        self.setAttribute(Qt.WA_DeleteOnClose)


class AuthDialog(QDialog):

    UI_PATH = '%s\\ui\\auth.ui' % MODULE_PATH

    def __init__(self, parent=None):
        super(AuthDialog, self).__init__(parent)
        setup_ui(self, self.UI_PATH)

        self.setWindowTitle(self.ui.windowTitle())
        self.ui.tb_browse.setIcon(QIcon('%s\\icons\\folder_open.png' % MODULE_PATH))

        self.ui.accepted.connect(self.accept)
        self.ui.rejected.connect(self.reject)
        server = cmds.optionVar(q=OPT_HOST)
        server = server if server else ':'
        host = server.split(':')[0]
        port = server.split(':')[1]
        self.ui.le_host.setText(host)
        self.ui.le_port.setText(port if port else '8000')
        self.ui.btn_test.clicked.connect(self.test)
        self.ui.bbox.setEnabled(False)
        self.project_id = []
        self.project_root = []

    def test(self, *_):
        self.project_id = []
        self.project_root = []
        while self.ui.cb_project.count():
            self.ui.cb_project.removeItem(0)
        host = self.ui.le_host.text()
        port = self.ui.le_port.text()
        url = 'http://%s:%s/api/project' % (host, port)
        try:
            result = requests.get(url)
            projects = json.loads(result.text)
            for p in projects:
                self.ui.cb_project.addItem(p['info'])
                self.project_id.append(p['id'])
                self.project_root.append(p['root'])
            self.ui.btn_test.setStyleSheet('color: #000000; background-color: #33CC33')
        except ConnectionError:
            self.ui.btn_test.setStyleSheet('color: #000000; background-color: #CC3333')
        except ValueError:
            self.ui.btn_test.setStyleSheet('color: #000000; background-color: #CC3333')
        finally:
            self.ui.bbox.setEnabled(True)
            self.ui.wgt_workspace.setEnabled(True)

    def get_info(self):
        host = self.ui.le_host.text()
        port = self.ui.le_port.text()
        prj_id = self.project_id[self.ui.cb_project.currentIndex()] if len(self.project_id) else ''
        prj_root = self.project_root[self.ui.cb_project.currentIndex()] if len(self.project_root) else ''
        workspace = self.ui.le_workspace.text()

        if not os.path.exists(workspace):
            workspace = cmds.workspace(q=True, directory=True)
            workspace = os.path.normpath(workspace)
            workspace = os.path.dirname(workspace)

        return '%s:%s' % (host, port) if (host and port) else '', \
               self.ui.cb_project.currentText(), \
               prj_id, \
               prj_root, \
               workspace, \
               self.ui.le_usr.text(), \
               self.ui.le_pwd.text()


class ImageHub(QObject):

    ImageRequested = Signal(dict)
    manager = QNetworkAccessManager()
    icon_set = {}

    def __init__(self, parent=None):
        super(ImageHub, self).__init__(parent)
        self.manager.finished.connect(self.on_finished)

    def get(self, url):
        if not self.icon_set.get(url, None):
            self.icon_set[url] = 'loading'
            host = cmds.optionVar(q=OPT_HOST)
            req = QNetworkRequest(QUrl('http://%s%s' % (host, url)))
            self.manager.get(req)
        elif not self.icon_set[url] == 'loading':
            self.ImageRequested.emit(self.icon_set)

    def on_finished(self, reply):
        if reply.error() == QNetworkReply.NoError:
            url = reply.url().path()
            data = reply.readAll()
            image = QImage()
            image.loadFromData(data)
            self.icon_set[url] = image
            self.ImageRequested.emit(self.icon_set)
