from maya import cmds
from PySide2.QtWidgets import \
    QWidget, \
    QListView, \
    QListWidgetItem, \
    QMenu, \
    QAction
from PySide2.QtGui import QIcon
from PySide2.QtCore import Signal

import action
import connection
from connection.utils import *
from interface import setup_ui, Docker
from .model import GenusModel, TagModel, AssetModel
from .delegate import AssetDelegate, TaskDelegate


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

        self.ui.cb_genus.setModel(genus_model)
        self.ui.cb_tag.setModel(tag_model)
        self.ui.lv_asset.setModel(asset_model)
        self.ui.lv_asset.setWrapping(True)
        self.ui.lv_asset.setResizeMode(QListView.Adjust)
        self.ui.lv_asset.setViewMode(QListView.IconMode)
        self.ui.lv_asset.setItemDelegate(AssetDelegate())
        self.ui.tb_reference.setIcon(QIcon('%s\\icons\\link.png' % MODULE_PATH))
        self.ui.tb_checkout.setIcon(QIcon('%s\\icons\\checkout.png' % MODULE_PATH))
        self.ui.tb_admin.setIcon(QIcon('%s\\icons\\admin.png' % MODULE_PATH))
        self.ui.tb_refresh.setIcon(QIcon('%s\\icons\\refresh.png' % MODULE_PATH))
        self.ui.tb_connect.setIcon(QIcon('%s\\icons\\setting.png' % MODULE_PATH))
        self.ui.tb_renew.setIcon(QIcon('%s\\icons\\refresh.png' % MODULE_PATH))
        self.ui.tb_open.setIcon(QIcon('%s\\icons\\edit.png' % MODULE_PATH))
        self.ui.tb_checkin.setIcon(QIcon('%s\\icons\\checkin.png' % MODULE_PATH))
        self.ui.tb_merge.setIcon(QIcon('%s\\icons\\merge.png' % MODULE_PATH))
        self.ui.tb_revert.setIcon(QIcon('%s\\icons\\revert.png' % MODULE_PATH))
        self.ui.tb_local.setIcon(QIcon('%s\\icons\\folder.png' % MODULE_PATH))
        self.ui.lw_task.setStyleSheet("""
            QListWidget {
                background: #00000000;
            }
            QListWidget:focus {
                border: none;
            }
        """)
        self.ui.lw_task.setItemDelegate(TaskDelegate())

        self.ui.cb_genus.activated.connect(self.refresh)
        self.ui.cb_genus.currentIndexChanged.connect(genus_model.notify)
        self.ui.cb_tag.currentIndexChanged.connect(tag_model.notify)
        self.ui.tb_connect.clicked.connect(lambda *_: self.status_update(force=True))
        self.ui.lv_asset.clicked.connect(lambda *_: self.build_menu())
        self.ui.tb_refresh.clicked.connect(
            lambda *_: genus_model.update(
                self.ui.cb_genus.currentIndex()
            )
        )
        self.ui.tb_renew.clicked.connect(self.ws_refresh)
        cmds.evalDeferred(self.status_update)

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

        if self.ui.cb_genus.currentIndex() == -1:
            self.ui.cb_genus.setCurrentIndex(0)
            self.ui.cb_genus.activated.emit(0)
        self.ui.cb_genus.model().update(self.ui.cb_genus.currentIndex())

        self.build_menu()
        self.ws_refresh()

    def refresh(self, *_):
        self.ui.cb_tag.setCurrentIndex(0)
        self.ui.cb_tag.setVisible(False)
        self.ui.cb_tag.setVisible(True)

    def build_menu(self, *_):
        current_index = self.ui.lv_asset.currentIndex()
        data_task = []
        asset_id = current_index.data(AssetModel.IdRole)
        if asset_id:
            data_task = connection.get_data('task', entity_id=asset_id)

        if not data_task:
            self.ui.tb_checkout.setMenu(None)
            self.ui.tb_reference.setMenu(None)
            self.ui.tb_checkout.setEnabled(False)
            self.ui.tb_reference.setEnabled(False)
            return

        checkout_menu = QMenu(self)
        reference_menu = QMenu(self)
        for task in data_task:
            checkout_action = TaskCheckoutAction(task, self)
            reference_action = TaskReferenceAction(task, self)
            checkout_action.Checked.connect(self.checkout)
            reference_action.Referred.connect(self.reference)
            checkout_menu.addAction(checkout_action)
            reference_menu.addAction(reference_action)
            owner = task['owner']
            if owner:
                checkout_action.setEnabled(False)
        self.ui.tb_checkout.setEnabled(cmds.optionVar(exists=OPT_USERNAME))
        self.ui.tb_reference.setEnabled(True)
        self.ui.tb_checkout.setMenu(checkout_menu if cmds.optionVar(exists=OPT_USERNAME) else None)
        self.ui.tb_reference.setMenu(reference_menu)

    def checkout(self, task):
        connection.set_data(
            'task',
            id=task['id'],
            owner=cmds.optionVar(q=OPT_USERNAME)
        )
        action.checkout(task['path'])
        self.ui.tw_main.setCurrentIndex(1)
        self.build_menu()
        self.ws_refresh()

    def reference(self, task):
        action

    def ws_refresh(self, *_):
        if not cmds.optionVar(exists=OPT_USERNAME):
            return

        data = connection.get_data('task', owner=cmds.optionVar(q=OPT_USERNAME))
        while self.ui.lw_task.count():
            self.ui.lw_task.takeItem(0)
        for task in data:
            widget = TaskItem(task)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.ui.lw_task.addItem(item)
            self.ui.lw_task.setItemWidget(item, widget)
        '''for i in range(self.view.count()):
            it = self.view.item(i)
            it.setFlags(it.flags() & ~Qt.ItemIsSelectable)'''


class TaskCheckoutAction(QAction):

    Checked = Signal(object)

    def __init__(self, task, parent=None):
        self._data = task
        super(TaskCheckoutAction, self).__init__(task['stage_info'], parent)
        self.triggered.connect(lambda *_: self.Checked.emit(self._data))


class TaskReferenceAction(QAction):

    Referred = Signal(object)

    def __init__(self, task, parent=None):
        self._data = task
        super(TaskReferenceAction, self).__init__(task['stage_info'], parent)
        self.triggered.connect(lambda *_: self.Referred.emit(self._data))


class TaskItem(QWidget):

    UI_PATH = '%s\\ui\\task.ui' % MODULE_PATH

    def __init__(self, task, parent=None):
        super(TaskItem, self).__init__(parent)
        setup_ui(self, self.UI_PATH)
        self._data = task

        self.ui.lbl_name.setText(task['entity'])
        self.ui.lbl_stage.setText(task['stage_info'])
