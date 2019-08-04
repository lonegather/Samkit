from Qt.QtCore import QAbstractListModel, QModelIndex, Qt, Signal

import samkit
from . import ImageHub


class GenusModel(QAbstractListModel):

    genusChanged = Signal(str)
    GenusRole = Qt.UserRole + 1

    def __init__(self, parent=None):
        super(GenusModel, self).__init__(parent)
        self._map = {
            Qt.DisplayRole: 'info',
            self.GenusRole: 'name',
        }
        # DATA FORMAT: [id, name, info]
        self._data = []
        self.current_id = ''

    def update(self):
        self._data = samkit.get_data('genus')
        self.dataChanged.emit(QModelIndex(), QModelIndex())
        self.notify(0)

    def notify(self, index):
        self.current_id = self._data[index]['id'] if self._data else ''
        self.genusChanged.emit(self.current_id)

    def rowCount(self, *_):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if self._data:
            return self._data[index.row()].get(self._map.get(role, None), None)


class TagModel(QAbstractListModel):

    tagChanged = Signal(str)
    TagRole = Qt.UserRole + 1

    def __init__(self, genus, parent=None):
        super(TagModel, self).__init__(parent)
        self._map = {
            Qt.DisplayRole: 'info',
            self.TagRole: 'name',
        }
        self._genus = genus
        # DATA FORMAT: [id, name, info, genus_id, genus_name, genus_info]
        self._data = []
        self.current_id = self._data[0]['id'] if self._data else ''
        self._genus.genusChanged.connect(self.update)

    def update(self, genus_id):
        self._data = samkit.get_data('tag', genus_id=genus_id, project_id=samkit.getenv(samkit.OPT_PROJECT_ID))
        self.dataChanged.emit(QModelIndex(), QModelIndex())
        self.notify(0)

    def notify(self, index):
        self.current_id = self._data[index]['id'] if self._data else ''
        self.tagChanged.emit(self.current_id)

    def rowCount(self, *_):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if self._data:
            return self._data[index.row()].get(self._map.get(role, None), None)


class AssetModel(QAbstractListModel):

    GenusRole = Qt.UserRole + 1
    IconRole = Qt.UserRole + 2
    IdRole = Qt.UserRole + 3

    filtered = Signal()
    
    def __init__(self, tag, parent=None):
        super(AssetModel, self).__init__(parent)
        self._map = {
            Qt.DisplayRole: 'info',
            self.GenusRole: 'genus_name',
            self.IconRole: 'image',
            self.IdRole: 'id',
        }
        self._filter = ''
        # DATA FORMAT: [id, name, info, genus_id, genus_name, genus_info, tag_id, tag_name, tag_info, link, thumb]
        self._data = []
        self._data_filter = []
        self._tag = tag
        self._hub = ImageHub()
        self._tag.tagChanged.connect(self.update)
        self._hub.ImageRequested.connect(self.image_received)

    def update(self, tag_id=None):
        tag_id = tag_id if tag_id else self._tag.current_id
        self._data = samkit.get_data('entity', tag_id=tag_id)
        self.filter(self._filter)
        for asset in self._data:
            self._hub.get(asset['thumb'])

    def filter(self, txt):
        self._filter = txt
        keys = [k.lower() for k in txt.split(' ') if k]
        self._data_filter = []

        for d in self._data:
            match = True
            for k in keys:
                if not (k in d['name'].lower() or k in d['info'].lower()):
                    match = False
                    break
            if match:
                self._data_filter.append(d)

        self.filtered.emit()
        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def rowCount(self, *_):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if len(self._data_filter) > index.row():
            return self._data_filter[index.row()].get(self._map.get(role, None), None)

    def image_received(self, icon_set):
        for url in icon_set:
            image = icon_set[url]
            for data in self._data:
                if data['thumb'] == url:
                    data['image'] = image

        self.dataChanged.emit(QModelIndex(), QModelIndex())

    def get_wrapper_data(self):
        result = []
        for asset in self._data:
            result.append({
                'id': asset['id'],
                'name': asset['name'],
                'info': asset['info'],
                'image': asset.get('image', None),
            })
        return result
