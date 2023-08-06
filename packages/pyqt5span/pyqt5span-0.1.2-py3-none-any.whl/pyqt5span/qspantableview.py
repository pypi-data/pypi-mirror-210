import typing
from PyQt5            import QtCore, QtWidgets
from .qspanheaderview import QSpanHeaderView

__all__ = [
    'QSpanTableView'
]

class QSpanTableView(QtWidgets.QTableView):
    def __init__(self, parent: typing.Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)

        hheader = QSpanHeaderView(QtCore.Qt.Orientation.Horizontal)
        vheader = QSpanHeaderView(QtCore.Qt.Orientation.Vertical)

        self.setHorizontalHeader(hheader)
        self.setVerticalHeader(vheader)
        
        hheader.sectionPressed.connect(self.onHorizontalHeaderSectionPressed)
        vheader.sectionPressed.connect(self.onVerticalHeaderSectionPressed)

    def setModel(self, model: QtCore.QAbstractItemModel) -> None:
        old_model = self.model()

        if old_model is not None:
            old_model.modelReset.disconnect(self.onModelReset)
            old_model.columnsInserted.disconnect(self.onModelColumnsChanged)
            old_model.columnsRemoved.disconnect(self.onModelColumnsChanged)
            old_model.rowsInserted.disconnect(self.onModelRowsChanged)
            old_model.rowsRemoved.disconnect(self.onModelRowsChanged)

        hheader = self.spanHeaderView(QtCore.Qt.Orientation.Horizontal)
        vheader = self.spanHeaderView(QtCore.Qt.Orientation.Vertical)

        hheader_model = hheader.model()
        vheader_model = vheader.model()

        # `QTableView` also sets the model of both horizontal and vertical headers to `model`.
        # We don't want that, since `QSpanHeaderView` has its own model.
        super().setModel(model)

        hheader.setModel(hheader_model)
        vheader.setModel(vheader_model)
        
        hheader.setSectionCount(model.columnCount())
        vheader.setSectionCount(model.rowCount())

        model.modelReset.connect(self.onModelReset)
        model.columnsInserted.connect(self.onModelColumnsChanged)
        model.columnsRemoved.connect(self.onModelColumnsChanged)
        model.rowsInserted.connect(self.onModelRowsChanged)
        model.rowsRemoved.connect(self.onModelRowsChanged)

    def spanHeaderView(self, orientation: QtCore.Qt.Orientation) -> QSpanHeaderView:
        if orientation == QtCore.Qt.Orientation.Horizontal:
            return self.horizontalHeader()
        else:
            return self.verticalHeader()

    @QtCore.pyqtSlot(int, int)
    def onHorizontalHeaderSectionPressed(self, begin_section: int, end_section: int) -> None:
        self.clearSelection()
        old_selection_mode = self.selectionMode()
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

        for i in range(begin_section, end_section + 1):
            self.selectColumn(i)

        self.setSelectionMode(old_selection_mode)

    @QtCore.pyqtSlot(int, int)
    def onVerticalHeaderSectionPressed(self, begin_section: int, end_section: int) -> None:
        self.clearSelection()
        old_selection_mode = self.selectionMode()
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

        for i in range(begin_section, end_section + 1):
            self.selectRow(i)
            
        self.setSelectionMode(old_selection_mode)

    @QtCore.pyqtSlot()
    def onModelReset(self) -> None:
        hheader = self.spanHeaderView(QtCore.Qt.Orientation.Horizontal)
        vheader = self.spanHeaderView(QtCore.Qt.Orientation.Vertical)

        hheader.setSectionCount(self.model().columnCount())
        vheader.setSectionCount(self.model().rowCount())

    @QtCore.pyqtSlot()
    def onModelColumnsChanged(self) -> None:
        hheader = self.spanHeaderView(QtCore.Qt.Orientation.Horizontal)
        hheader.setSectionCount(self.model().columnCount())

    @QtCore.pyqtSlot()
    def onModelRowsChanged(self) -> None:
        vheader = self.spanHeaderView(QtCore.Qt.Orientation.Vertical)
        vheader.setSectionCount(self.model().rowCount())