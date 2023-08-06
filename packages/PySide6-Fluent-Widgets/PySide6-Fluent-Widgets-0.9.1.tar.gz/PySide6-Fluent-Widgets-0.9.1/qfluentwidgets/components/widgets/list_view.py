# coding:utf-8
from typing import List, Union

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyleOptionViewItem, QListView, QListView, QListWidget

from .scroll_bar import SmoothScrollDelegate
from .table_view import TableItemDelegate
from ...common.style_sheet import FluentStyleSheet, themeColor


class ListItemDelegate(TableItemDelegate):
    """ List item delegate """

    def __init__(self, parent: QListView):
        super().__init__(parent)

    def _drawBackground(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.drawRoundedRect(option.rect, 5, 5)

    def _drawIndicator(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        y, h = option.rect.y(), option.rect.height()
        ph = round(0.35*h if self.pressedRow == index.row() else 0.257*h)
        painter.setBrush(themeColor())
        painter.drawRoundedRect(0, ph + y, 3, h - 2*ph, 1.5, 1.5)


class ListBase:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.delegate = ListItemDelegate(self)
        self.scrollDelegate = SmoothScrollDelegate(self)

        FluentStyleSheet.LIST_VIEW.apply(self)
        self.setItemDelegate(self.delegate)
        self.setMouseTracking(True)

        self.entered.connect(lambda i: self._setHoverRow(i.row()))
        self.pressed.connect(lambda i: self._setPressedRow(i.row()))

    def _setHoverRow(self, row: int):
        """ set hovered row """
        self.delegate.setHoverRow(row)
        self.viewport().update()

    def _setPressedRow(self, row: int):
        """ set pressed row """
        self.delegate.setPressedRow(row)
        self.viewport().update()

    def _setSelectedRows(self, indexes: List[QModelIndex]):
        self.delegate.setSelectedRows(indexes)
        self.viewport().update()

    def leaveEvent(self, e):
        QListView.leaveEvent(self, e)
        self._setHoverRow(-1)

    def resizeEvent(self, e):
        QListView.resizeEvent(self, e)
        self.viewport().update()

    def keyPressEvent(self, e):
        QListView.keyPressEvent(self, e)
        self._updateSelectedRows()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            QListView.mousePressEvent(self, e)
        else:
            self._setPressedRow(self.indexAt(e.pos()).row())

    def mouseReleaseEvent(self, e):
        QListView.mouseReleaseEvent(self, e)

        row = self.indexAt(e.pos()).row()
        if row >= 0 and e.button() != Qt.RightButton:
            self._updateSelectedRows()
        else:
            self._setPressedRow(-1)

    def setItemDelegate(self, delegate: ListItemDelegate):
        self.delegate = delegate
        super().setItemDelegate(delegate)

    def setSelection(self, rect, command):
        QListView.setSelection(self, rect, command)
        self._updateSelectedRows()

    def clearSelection(self):
        QListView.clearSelection(self)
        self._updateSelectedRows()

    def setCurrentIndex(self, index: QModelIndex):
        QListView.setCurrentIndex(self, index)
        self._updateSelectedRows()

    def _updateSelectedRows(self):
        self._setSelectedRows(self.selectedIndexes())


class ListWidget(ListBase, QListWidget):
    """ List widget """

    def __init__(self, parent=None):
        super().__init__(parent)

    def setCurrentItem(self, item, command=None):
        self.setCurrentRow(self.row(item), command)

    def setCurrentRow(self, row: int, command=None):
        if not command:
            super().setCurrentRow(row)
        else:
            super().setCurrentRow(row, command)

        self._updateSelectedRows()


class ListView(ListBase, QListView):
    """ List view """

    def __init__(self, parent=None):
        super().__init__(parent)