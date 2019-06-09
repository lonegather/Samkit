from PySide2.QtWidgets import QStyledItemDelegate, QStyle
from PySide2.QtGui import QPen, QColor
from PySide2.QtCore import QSize, Qt

from .model import AssetModel


class AssetDelegate(QStyledItemDelegate):

    ITEM_WIDTH = 100
    ITEM_HEIGHT = 130

    def __init__(self, parent=None):
        super(AssetDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        item_rect = option.rect.adjusted(1, 1, -1, -1)
        icon_rect = option.rect.adjusted(10, 10, -10, self.ITEM_WIDTH - self.ITEM_HEIGHT - 10)
        label_rect = item_rect.adjusted(0, self.ITEM_WIDTH, 0, 0)
        image = index.data(AssetModel.IconRole)
        painter.save()
        painter.setPen(QPen(QColor(0, 0, 0, 255)))
        painter.drawRect(item_rect)
        if option.state & QStyle.State_Selected:
            painter.fillRect(item_rect, QColor(82, 133, 166))
        if image:
            painter.drawImage(icon_rect, image)
        painter.setPen(QPen(QColor(200, 200, 200, 255)))
        painter.drawText(label_rect, Qt.AlignVCenter | Qt.AlignHCenter, index.data())
        painter.restore()

    def sizeHint(self, option, index):
        return QSize(self.ITEM_WIDTH, self.ITEM_HEIGHT)


class TaskDelegate(QStyledItemDelegate):

    ITEM_WIDTH = 100
    ITEM_HEIGHT = 50

    def __init__(self, parent=None):
        super(TaskDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        # option.state = QStyle.State_None
        option.rect = option.rect.adjusted(0, 8, 0, 0)
        super(TaskDelegate, self).paint(painter, option, index)

    def sizeHint(self, option, index):
        return QSize(self.ITEM_WIDTH, self.ITEM_HEIGHT)
