from maya import cmds
from PySide2.QtWidgets import \
    QWidget, \
    QListView, \
    QHBoxLayout, \
    QListWidgetItem, \
    QDialog
from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt

import connection
from connection.utils import *
from interface import setup_ui, get_main_window, Docker
from .model import GenusModel, TagModel, AssetModel, StageModel
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
        self.ui.cb_genus.activated.connect(self.refresh)

        self.ui.cb_genus.setModel(genus_model)
        self.ui.cb_tag.setModel(tag_model)
        self.ui.lv_asset.setModel(asset_model)
        self.ui.lv_asset.setWrapping(True)
        self.ui.lv_asset.setResizeMode(QListView.Adjust)
        self.ui.lv_asset.setViewMode(QListView.IconMode)
        self.ui.lv_asset.setItemDelegate(AssetDelegate())
        self.ui.tb_checkout.setIcon(QIcon('%s\\icons\\checkout.png' % MODULE_PATH))
        self.ui.tb_connect.setIcon(QIcon('%s\\icons\\connect.png' % MODULE_PATH))
        self.ui.tb_refresh.setIcon(QIcon('%s\\icons\\refresh.png' % MODULE_PATH))
        self.ui.tb_renew.setIcon(QIcon('%s\\icons\\refresh.png' % MODULE_PATH))
        self.ui.tb_reference.setIcon(QIcon('%s\\icons\\link.png' % MODULE_PATH))
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
        self.ui.lw_task.setItemDelegate(TaskDelegate())

        self.ui.cb_genus.currentIndexChanged.connect(genus_model.notify)
        self.ui.cb_tag.currentIndexChanged.connect(tag_model.notify)
        self.ui.tb_connect.clicked.connect(lambda *_: self.status_update(force=True))
        self.ui.tb_checkout.clicked.connect(self.checkout)
        self.ui.tb_refresh.clicked.connect(
            lambda *_: genus_model.update(
                self.ui.cb_genus.currentIndex()
            )
        )
        self.ui.tb_renew.clicked.connect(self.ws_refresh)
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
        self.ws_refresh()

    def refresh(self, *_):
        self.ui.cb_tag.setCurrentIndex(0)
        self.ui.cb_tag.setVisible(False)
        self.ui.cb_tag.setVisible(True)

    def checkout(self, *_):
        current_index = self.ui.lv_asset.currentIndex()
        asset_id = current_index.data(AssetModel.IdRole)
        dialog = StageDialog(asset_id, get_main_window())
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_info()
            if not data['owner'] and cmds.optionVar(exists=OPT_USERNAME):
                if connection.set_data(
                    'task',
                    id=data['id'],
                    owner=cmds.optionVar(q=OPT_USERNAME)
                ):
                    self.ui.tw_main.setCurrentIndex(1)
                    self.ws_refresh()

    def ws_refresh(self, *_):
        if not cmds.optionVar(exists=OPT_USERNAME):
            return

        data = connection.get_data('task', owner=cmds.optionVar(q=OPT_USERNAME))
        while self.ui.lw_task.count():
            self.ui.lw_task.takeItem(0)
        for task in data:
            widget = TaskItem(task['stage_info'])
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.ui.lw_task.addItem(item)
            self.ui.lw_task.setItemWidget(item, widget)
        '''for i in range(self.view.count()):
            it = self.view.item(i)
            it.setFlags(it.flags() & ~Qt.ItemIsSelectable)'''


class AssetSegment(QWidget):

    def __init__(self, parent=None):
        super(AssetSegment, self).__init__(parent)
        layout = QHBoxLayout(self)

        self.setLayout(layout)


class StageDialog(QDialog):

    UI_PATH = '%s\\ui\\stage.ui' % MODULE_PATH

    def __init__(self, asset_id, parent=None):
        super(StageDialog, self).__init__(parent)
        setup_ui(self, self.UI_PATH)
        self.ui.accepted.connect(self.accept)
        self.ui.rejected.connect(self.reject)
        self.ui.lv_stage.setModel(StageModel(asset_id))
        self.ui.lv_stage.clicked.connect(self.change)
        self._data = None

    def change(self, index):
        self._data = {
            'id': index.data(StageModel.IdRole),
            'info': index.data(Qt.DisplayRole),
            'path': index.data(StageModel.PathRole),
            'owner': index.data(StageModel.OwnerRole),
        }

    def get_info(self):
        return self._data


class TaskItem(QWidget):

    UI_PATH = '%s\\ui\\task.ui' % MODULE_PATH

    def __init__(self, stage, parent=None):
        super(TaskItem, self).__init__(parent)
        setup_ui(self, self.UI_PATH)

        self.ui.lbl_stage.setText(stage)
