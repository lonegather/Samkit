from maya import cmds
from maya.OpenMayaUI import MQtUtil
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2.QtWidgets import QWidget, QSizePolicy, QListView, QTabBar
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt

import connection
from connection.utils import *
from interface import setup_ui
from .model import GenusModel, TagModel, AssetModel
from .delegate import AssetDelegate


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


class DockerMain(Docker):

    CONTROL_NAME = 'samkit_docker_control'
    DOCK_LABEL_NAME = 'Samkit'
    UI_PATH = '%s\\ui\\main.ui' % MODULE_PATH

    def __init__(self, parent=None):
        super(DockerMain, self).__init__(parent=parent)
        setup_ui(self, self.UI_PATH)
        self.connected = False
        self.authorized = False
        self.project_id = ''

        genus_model = GenusModel()
        tag_model = TagModel(genus_model)
        asset_model = AssetModel(tag_model)
        self.ui.cb_genus.activated.connect(self.refresh)

        self.ui.cb_genus.setModel(genus_model)
        self.ui.cb_tag.setModel(tag_model)
        self.ui.lv_asset.setModel(asset_model)
        self.ui.lv_asset.setWrapping(True)
        self.ui.lv_asset.setResizeMode(QListView.Adjust)
        self.ui.lv_asset.setViewMode(QListView.IconMode)
        self.ui.lv_asset.setItemDelegate(AssetDelegate())
        self.ui.tw_main.setTabsClosable(True)
        self.ui.tw_main.setTabBarAutoHide(True)
        self.ui.tb_connect.setIcon(QIcon('%s\\icons\\connect.png' % MODULE_PATH))
        self.ui.tb_refresh.setIcon(QIcon('%s\\icons\\refresh.png' % MODULE_PATH))

        tab_bar = self.ui.tw_main.tabBar()
        tab_bar.tabButton(0, QTabBar.RightSide).deleteLater()
        tab_bar.setTabButton(0, QTabBar.RightSide, None)

        self.ui.tw_main.tabCloseRequested.connect(lambda index: self.ui.tw_main.removeTab(index))
        self.ui.cb_genus.currentIndexChanged.connect(genus_model.notify)
        self.ui.cb_tag.currentIndexChanged.connect(tag_model.notify)
        self.ui.tb_connect.clicked.connect(lambda *_: self.status_update(force=True))
        self.ui.tb_refresh.clicked.connect(
            lambda *_: genus_model.update(
                self.ui.cb_genus.currentIndex()
            )
        )
        self.status_update()

    def status_update(self, force=False):
        self.project_id = ''
        self.ui.lbl_project.setStyleSheet('background-color: rgba(0, 0, 0, 0);')
        self.ui.lbl_project.setText('Retrieving...')
        connection.access(force=force)
        self.connected = cmds.optionVar(exists=OPT_HOST)
        self.authorized = cmds.optionVar(exists=OPT_COOKIES)
        self.ui.lbl_project.setStyleSheet('color: #000000; background-color: #CC3333;')
        self.ui.lbl_project.setText('Server Connection Error')
        if self.connected:
            self.ui.lbl_project.setStyleSheet('color: #000000; background-color: #CCCC33;')
            self.ui.lbl_project.setText(cmds.optionVar(q=OPT_PROJECT))
            self.project_id = cmds.optionVar(q=OPT_PROJECT_ID)
        if self.authorized:
            self.ui.lbl_project.setStyleSheet('color: #000000; background-color: #33CC33;')

        self.ui.cb_genus.model().update(self.ui.cb_genus.currentIndex())

    def refresh(self, *_):
        self.ui.cb_tag.setCurrentIndex(0)
        self.ui.cb_tag.setVisible(False)
        self.ui.cb_tag.setVisible(True)
