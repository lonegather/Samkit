import os
from maya import cmds
from PySide2.QtWidgets import QWidget, QListView, QListWidgetItem, QMenu, QAction
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtCore import Signal, Qt

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
        self.ui.lv_asset.setItemDelegate(AssetDelegate())
        self.ui.lw_task.setItemDelegate(TaskDelegate())

        self.ui.lv_asset.setWrapping(True)
        self.ui.lv_asset.setResizeMode(QListView.Adjust)
        self.ui.lv_asset.setViewMode(QListView.IconMode)
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
        self.ui.lw_task.setStyleSheet("""
            QListWidget {
                background: #00000000;
            }
            QListWidget:focus {
                border: none;
            }
        """)

        genus_model.dataChanged.connect(self.redraw_genus)
        tag_model.dataChanged.connect(self.redraw_tag)
        asset_model.dataChanged.connect(self.redraw_asset)
        self.ui.cb_genus.currentIndexChanged.connect(genus_model.notify)
        self.ui.cb_tag.currentIndexChanged.connect(tag_model.notify)
        self.ui.tb_connect.clicked.connect(lambda *_: self.status_update(force=True))
        self.ui.lv_asset.clicked.connect(lambda *_: self.build_menu())
        self.ui.tb_refresh.clicked.connect(lambda *_: genus_model.update())

        self.ui.lw_task.clicked.connect(self.ws_update_toolbar)
        self.ui.lw_task.doubleClicked.connect(self.ws_open)
        self.ui.tb_open.clicked.connect(self.ws_open)
        self.ui.tb_revert.clicked.connect(self.ws_revert)
        self.ui.tb_renew.clicked.connect(self.ws_refresh)
        self.ui.tb_merge.clicked.connect(self.ws_merge)
        self.ui.tb_checkin.clicked.connect(self.ws_checkin)

        cmds.scriptJob(event=['SceneOpened', self.ws_refresh])
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
        self.ui.tw_main.setTabEnabled(1, cmds.optionVar(exists=OPT_USERNAME))

        self.ui.cb_genus.model().update()
        self.build_menu()
        self.ws_refresh()

    def redraw_genus(self, *_):
        self.ui.cb_genus.setCurrentIndex(0)

    def redraw_tag(self, *_):
        self.ui.cb_tag.setCurrentIndex(0)
        self.ui.cb_tag.setVisible(False)
        self.ui.cb_tag.setVisible(True)

    def redraw_asset(self, *_):
        model = self.ui.lv_asset.model()
        self.ui.lv_asset.setModel(None)
        self.ui.lv_asset.setModel(model)

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
        connection.set_data('task', id=task['id'], owner=cmds.optionVar(q=OPT_USERNAME))
        task['owner'] = cmds.optionVar(q=OPT_USERNAME)
        action.checkout(task)
        self.build_menu()
        self.ws_refresh()
        self.ui.tw_main.setCurrentIndex(1)

    def reference(self, task):
        action.reference(task)

    def ws_refresh(self, *_):
        if not cmds.optionVar(exists=OPT_USERNAME):
            return

        data = connection.get_data('task', owner=cmds.optionVar(q=OPT_USERNAME))
        context = action.get_context('id')

        while self.ui.lw_task.count():
            self.ui.lw_task.takeItem(0)
        for task in data:
            item = TaskItem(task, context)
            item.setSizeHint(item.widget.sizeHint())
            self.ui.lw_task.addItem(item)
            self.ui.lw_task.setItemWidget(item, item.widget)
        '''for i in range(self.view.count()):
            it = self.view.item(i)
            it.setFlags(it.flags() & ~Qt.ItemIsSelectable)'''
        self.ws_update_toolbar()

    def ws_update_toolbar(self, *_):
        item = self.ui.lw_task.currentItem()
        if not item:
            self.ui.tb_open.setEnabled(False)
            self.ui.tb_revert.setEnabled(False)
            self.ui.tb_merge.setEnabled(False)
            self.ui.tb_checkin.setEnabled(False)
            return

        context = action.get_context('id')
        local_path = os.path.realpath(os.path.join(cmds.optionVar(q=OPT_WORKSPACE), item.data(TaskItem.PATH)))
        self.ui.tb_open.setEnabled(os.path.exists(local_path) and item.data(TaskItem.ID) != context)
        self.ui.tb_revert.setEnabled(True)
        self.ui.tb_merge.setEnabled(item.data(TaskItem.ID) != context)
        self.ui.tb_checkin.setEnabled(os.path.exists(local_path))

    def ws_open(self, *_):
        item = self.ui.lw_task.currentItem()
        action.open_file(item.data(TaskItem.PATH))

    def ws_revert(self, *_):
        context = action.get_context('id')
        item = self.ui.lw_task.currentItem()
        if item.data(TaskItem.ID) == context:
            cmds.file(new=True, force=True)
        connection.set_data('task', id=item.data(TaskItem.ID), owner='')
        self.build_menu()
        self.ws_refresh()

    def ws_merge(self, *_):
        pass

    def ws_checkin(self, *_):
        context = action.get_context('id')
        item = self.ui.lw_task.currentItem()
        if item.data(TaskItem.ID) != context:
            action.open_file(item.data(TaskItem.PATH))
        cmds.evalDeferred(action.checkin)


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


class TaskItem(QListWidgetItem):

    UI_PATH = '%s\\ui\\task.ui' % MODULE_PATH
    ID = Qt.UserRole + 1
    PATH = Qt.UserRole + 2

    def __init__(self, task, context, parent=None):
        super(TaskItem, self).__init__(parent)
        self.widget = QWidget()
        self._data = task
        self._map = {
            self.ID: 'id',
            self.PATH: 'path',
        }

        setup_ui(self.widget, self.UI_PATH)
        self.widget.setFocusPolicy(Qt.NoFocus)
        self.widget.ui.lbl_name.setText(task['entity'])
        self.widget.ui.lbl_stage.setText(task['stage_info'])
        self.update_icon(context)

    def data(self, role):
        return self._data[self._map[role]] if role in self._map else None

    def update_icon(self, context=None):
        path = os.path.realpath(os.path.join(cmds.optionVar(q=OPT_WORKSPACE), self._data['path']))
        if os.path.exists(path):
            if context == self._data['id']:
                self.widget.ui.lbl_icon.setPixmap(QPixmap('%s\\icons\\bookmark.png' % MODULE_PATH))
            else:
                self.widget.ui.lbl_icon.setPixmap(QPixmap('%s\\icons\\checked.png' % MODULE_PATH))
        else:
            self.widget.ui.lbl_icon.setPixmap(QPixmap('%s\\icons\\unavailable.png' % MODULE_PATH))

