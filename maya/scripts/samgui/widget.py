from Qt.QtWidgets import QWidget, QListView, QListWidgetItem, QMenu, QAction
from Qt.QtGui import QIcon, QPixmap
from Qt.QtCore import Signal, Qt

import samkit
from . import setup_ui, Docker
from .model import GenusModel, TagModel, AssetModel
from .delegate import AssetDelegate, TaskDelegate


class DockerMain(Docker):

    CONTROL_NAME = 'samkit_docker_control'
    DOCK_LABEL_NAME = 'Samkit'
    UI_PATH = '%s\\ui\\main.ui' % samkit.MODULE_PATH

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
        self.ui.tb_reference.setIcon(QIcon('%s\\icons\\link.png' % samkit.MODULE_PATH))
        self.ui.tb_checkout.setIcon(QIcon('%s\\icons\\checkout.png' % samkit.MODULE_PATH))
        self.ui.tb_admin.setIcon(QIcon('%s\\icons\\admin.png' % samkit.MODULE_PATH))
        self.ui.tb_refresh.setIcon(QIcon('%s\\icons\\refresh.png' % samkit.MODULE_PATH))
        self.ui.tb_connect.setIcon(QIcon('%s\\icons\\setting.png' % samkit.MODULE_PATH))
        self.ui.tb_renew.setIcon(QIcon('%s\\icons\\refresh.png' % samkit.MODULE_PATH))
        self.ui.tb_open.setIcon(QIcon('%s\\icons\\edit.png' % samkit.MODULE_PATH))
        self.ui.tb_checkin.setIcon(QIcon('%s\\icons\\checkin.png' % samkit.MODULE_PATH))
        self.ui.tb_merge.setIcon(QIcon('%s\\icons\\merge.png' % samkit.MODULE_PATH))
        self.ui.tb_revert.setIcon(QIcon('%s\\icons\\revert.png' % samkit.MODULE_PATH))
        self.ui.lw_task.setStyleSheet("""
            QListWidget {
                background: #00000000;
            }
            QListWidget:focus {
                border: none;
            }
        """)

        genus_model.dataChanged.connect(self.refresh_repository_genus)
        tag_model.dataChanged.connect(self.refresh_repository_tag)
        asset_model.dataChanged.connect(self.refresh_repository_asset)
        self.ui.cb_genus.currentIndexChanged.connect(genus_model.notify)
        self.ui.cb_tag.currentIndexChanged.connect(tag_model.notify)
        self.ui.tb_connect.clicked.connect(lambda *_: self.refresh_repository(force=True))
        self.ui.lv_asset.clicked.connect(lambda *_: self.refresh_repository_toolbar())
        self.ui.tb_refresh.clicked.connect(lambda *_: genus_model.update())

        self.ui.lw_task.clicked.connect(self.refresh_workspace_toolbar)
        self.ui.lw_task.doubleClicked.connect(self.open_workspace)
        self.ui.tb_open.clicked.connect(self.open_workspace)
        self.ui.tb_revert.clicked.connect(self.revert_workspace)
        self.ui.tb_renew.clicked.connect(self.refresh_workspace)
        self.ui.tb_merge.clicked.connect(self.merge_workspace)
        self.ui.tb_checkin.clicked.connect(self.checkin_workspace)

        samkit.scriptJob(event=['SceneOpened', self.refresh_workspace])
        samkit.evalDeferred(self.refresh_repository)

    def refresh_repository(self, force=False):
        self.project_id = ''
        self.ui.lbl_project.setStyleSheet('background-color: rgba(0, 0, 0, 0);')
        self.ui.lbl_project.setText('Retrieving...')

        samkit.access(force=force)

        self.connected = samkit.hasenv(samkit.OPT_HOST)
        self.authorized = samkit.hasenv(samkit.OPT_COOKIES)
        self.ui.lbl_project.setStyleSheet('color: #000000; background-color: #CC3333;')
        self.ui.lbl_project.setText('Server Connection Error')
        if self.connected:
            self.ui.lbl_project.setStyleSheet('color: #000000; background-color: #CCCC33;')
            self.ui.lbl_project.setText(samkit.getenv(samkit.OPT_PROJECT))
            self.project_id = samkit.getenv(samkit.OPT_PROJECT_ID)
        if self.authorized:
            self.ui.lbl_project.setStyleSheet('color: #000000; background-color: #33CC33;')
        self.ui.tw_main.setTabEnabled(1, samkit.hasenv(samkit.OPT_USERNAME))

        self.ui.cb_genus.model().update()
        self.refresh_repository_toolbar()
        self.refresh_workspace()

    def refresh_repository_genus(self, *_):
        self.ui.cb_genus.setCurrentIndex(0)

    def refresh_repository_tag(self, *_):
        self.ui.cb_tag.setCurrentIndex(0)
        self.ui.cb_tag.setVisible(False)
        self.ui.cb_tag.setVisible(True)

    def refresh_repository_asset(self, *_):
        model = self.ui.lv_asset.model()
        self.ui.lv_asset.setModel(None)
        self.ui.lv_asset.setModel(model)

    def refresh_repository_toolbar(self, *_):
        current_index = self.ui.lv_asset.currentIndex()
        data_task = []
        asset_id = current_index.data(AssetModel.IdRole)
        if asset_id:
            data_task = samkit.get_data('task', entity_id=asset_id)

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
            checkout_action.Checked.connect(self.checkout_repository)
            reference_action.Referred.connect(samkit.reference)
            checkout_menu.addAction(checkout_action)
            reference_menu.addAction(reference_action)
            owner = task['owner']
            if owner:
                checkout_action.setEnabled(False)
        self.ui.tb_checkout.setEnabled(samkit.hasenv(samkit.OPT_USERNAME))
        self.ui.tb_reference.setEnabled(True)
        self.ui.tb_checkout.setMenu(checkout_menu if samkit.hasenv(samkit.OPT_USERNAME) else None)
        self.ui.tb_reference.setMenu(reference_menu)

    def refresh_workspace(self, *_):
        if not samkit.hasenv(samkit.OPT_USERNAME):
            return

        data = samkit.get_data('task', owner=samkit.getenv(samkit.OPT_USERNAME))
        context = samkit.get_context('id')

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
        self.refresh_workspace_toolbar()

    def refresh_workspace_toolbar(self, *_):
        item = self.ui.lw_task.currentItem()
        if not item:
            self.ui.tb_open.setEnabled(False)
            self.ui.tb_revert.setEnabled(False)
            self.ui.tb_merge.setEnabled(False)
            self.ui.tb_checkin.setEnabled(False)
            return

        context = samkit.get_context('id')
        local_path_exists = samkit.path_exists(item.data(TaskItem.TASK))
        self.ui.tb_open.setEnabled(local_path_exists and item.data(TaskItem.ID) != context)
        self.ui.tb_revert.setEnabled(True)
        self.ui.tb_merge.setEnabled(item.data(TaskItem.ID) != context)
        self.ui.tb_checkin.setEnabled(local_path_exists)

    def checkout_repository(self, task):
        samkit.checkout(task)
        self.refresh_repository_toolbar()
        self.refresh_workspace()
        self.ui.tw_main.setCurrentIndex(1)

    def open_workspace(self, *_):
        item = self.ui.lw_task.currentItem()
        samkit.open_file(item.data(TaskItem.TASK))

    def revert_workspace(self, *_):
        item = self.ui.lw_task.currentItem()
        samkit.revert(item.data(TaskItem.ID))
        self.refresh_repository_toolbar()
        self.refresh_workspace()

    def merge_workspace(self, *_):
        pass

    def checkin_workspace(self, *_):
        context = samkit.get_context('id')
        item = self.ui.lw_task.currentItem()
        if item.data(TaskItem.ID) != context:
            samkit.open_file(item.data(TaskItem.TASK))
        samkit.evalDeferred(samkit.checkin)


class TaskCheckoutAction(QAction):

    Checked = Signal(object)

    def __init__(self, task, parent=None):
        self._data = task
        label = task['stage_info']
        label += ' [checked out by %s]' % task['owner'] if task['owner'] else ''
        super(TaskCheckoutAction, self).__init__(label, parent)
        self.triggered.connect(lambda *_: self.Checked.emit(self._data))


class TaskReferenceAction(QAction):

    Referred = Signal(object)

    def __init__(self, task, parent=None):
        self._data = task
        super(TaskReferenceAction, self).__init__(task['stage_info'], parent)
        self.triggered.connect(lambda *_: self.Referred.emit(self._data))


class TaskItem(QListWidgetItem):

    UI_PATH = '%s\\ui\\task.ui' % samkit.MODULE_PATH
    ID = Qt.UserRole + 1
    PATH = Qt.UserRole + 2
    TASK = Qt.UserRole + 3

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
        if role in self._map:
            return self._data[self._map[role]]
        elif role == self.TASK:
            return self._data
        return None

    def update_icon(self, context=None):
        if samkit.path_exists(self._data):
            if context == self._data['id']:
                self.widget.ui.lbl_icon.setPixmap(QPixmap('%s\\icons\\bookmark.png' % samkit.MODULE_PATH))
            else:
                self.widget.ui.lbl_icon.setPixmap(QPixmap('%s\\icons\\checked.png' % samkit.MODULE_PATH))
        else:
            self.widget.ui.lbl_icon.setPixmap(QPixmap('%s\\icons\\unavailable.png' % samkit.MODULE_PATH))

