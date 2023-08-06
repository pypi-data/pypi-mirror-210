from __future__ import annotations
import typing
from enum  import IntEnum
from PyQt5 import QtCore

__all__ = [
    'QSpanHeaderModel'
]

class _SpanHeaderItem:
    """Stores data of an index of `QSpanHeaderModel`."""

    __slots__ = (
        '_row',
        '_column',
        '_parent',
        '_children',
        '_data'
    )

    def __init__(self, row: int = 0, column: int = 0, parent: typing.Optional[_SpanHeaderItem] = None):
        self._row      = row
        self._column   = column
        self._parent   = parent
        self._children = {}
        self._data     = {}
    
    def insertChild(self, row: int, col: int) -> _SpanHeaderItem:
        child = _SpanHeaderItem(row, col, self)
        self._children[(row, col)] = child
        return child

    def child(self, row: int, col: int) -> typing.Optional[_SpanHeaderItem]:
        return self._children.get((row, col), None)

    def parent(self) -> typing.Optional[_SpanHeaderItem]:
        return self._parent

    def row(self) -> int:
        return self._row

    def column(self) -> int:
        return self._column

    def setData(self, data: typing.Any, role: int) -> None:
        self._data[role] = data

    def data(self, role: int) -> typing.Any:
        return self._data.get(role, None)

    def clear(self) -> None:
        for child in self._children.values():
            child.clear()
        
        self._children.clear()

class QSpanHeaderModel(QtCore.QAbstractTableModel):
    class HeaderRole(IntEnum):
        ColumnSpanRole = QtCore.Qt.ItemDataRole.UserRole + 1
        RowSpanRole    = ColumnSpanRole + 1

    def __init__(self, rows: int, columns: int, parent: typing.Optional[typing.Any] = None):
        super().__init__(parent)

        self._rows      = rows
        self._columns   = columns
        self._root_item = _SpanHeaderItem()

    def index(self, row: int, column: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parent_item = self._root_item
        else:
            parent_item: _SpanHeaderItem = parent.internalPointer()

        child_item = parent_item.child(row, column)

        if child_item is None:
            child_item = parent_item.insertChild(row, column)

        return self.createIndex(row, column, child_item)

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return self._rows

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        return self._columns

    def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        
        return super().flags(index)

    def data(self, index: QtCore.QModelIndex, role: int) -> typing.Any:
        if not index.isValid():
            return None

        if index.row() >= self._rows or index.row() < 0 or index.column() >= self._columns or index.column() < 0:
            return None

        item: _SpanHeaderItem = index.internalPointer()

        return item.data(role)

    def setData(self, index: QtCore.QModelIndex, value: typing.Any, role: int = QtCore.Qt.ItemDataRole.EditRole) -> bool:
        if index.isValid():
            item: _SpanHeaderItem = index.internalPointer()
            
            if role == QSpanHeaderModel.HeaderRole.ColumnSpanRole:
                col = index.column();
                span: int = value
            
                if span > 0:
                    if col + span - 1 >= self._columns:
                        span = self._columns - col
                
                    item.setData(span, QSpanHeaderModel.HeaderRole.ColumnSpanRole)
            
            elif role == QSpanHeaderModel.HeaderRole.RowSpanRole:
                row = index.row()
                span: int = value
                
                if span > 0:
                    if row + span - 1 > self._rows:
                        span = self._rows - row

                    item.setData(span, QSpanHeaderModel.HeaderRole.RowSpanRole)
                
            else:
                item.setData(value, role)

            return True
        
        return False
    
    def insertRows(self, row: int, count: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        self.beginInsertRows(parent, row, row + count - 1)
        self._rows += count
        self.endInsertRows()

        return True
    
    def removeRows(self, row: int, count: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        self.beginRemoveRows(parent, row, row + count - 1)
        self._rows -= count
        self.endRemoveRows()

        return True

    def insertColumns(self, column: int, count: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        self.beginInsertColumns(parent, column, column + count - 1)
        self._columns += count
        self.endInsertColumns()

        return True
    
    def removeColumns(self, column: int, count: int, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> bool:
        self.beginRemoveColumns(parent, column, column + count - 1)
        self._columns -= count
        self.endRemoveColumns()

        return True