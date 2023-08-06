import typing
from PyQt5             import QtCore, QtGui, QtWidgets
from .qspanheadermodel import QSpanHeaderModel

__all__ = [
    'QSpanHeaderView'
]

class QSpanHeaderView(QtWidgets.QHeaderView):
    sectionPressed = QtCore.pyqtSignal(int, int)

    def __init__(self, orientation: QtCore.Qt.Orientation, sections: int = 0, parent: typing.Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(orientation, parent)

        base_section_size = QtCore.QSize()

        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            base_section_size.setWidth(self.defaultSectionSize())
            base_section_size.setHeight(20)
            rows    = 1
            columns = sections
        else:
            base_section_size.setWidth(50)
            base_section_size.setHeight(self.defaultSectionSize())
            rows    = sections
            columns = 1

        model = QSpanHeaderModel(rows, columns)

        for row in range(rows):
            for col in range(columns):
                model.setData(model.index(row, col), base_section_size, QtCore.Qt.ItemDataRole.SizeHintRole)

        self.setModel(model)
        self.sectionResized.connect(self.onSectionResized)

    def setSectionCount(self, sections: int) -> None:
        model = self.model()

        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            current_sections = model.columnCount()

            if sections < current_sections:
                model.removeColumns(sections, current_sections - sections)
            elif sections > current_sections:
                model.insertColumns(current_sections, sections - current_sections)

                for col in range(current_sections, sections):
                    model.setData(model.index(0, col), QtCore.QSize(self.defaultSectionSize(), 20), QtCore.Qt.ItemDataRole.SizeHintRole)
        else:
            current_sections = model.rowCount()

            if sections < current_sections:
                model.removeRows(sections, current_sections - sections)
            elif sections > current_sections:
                model.insertRows(current_sections, sections - current_sections)

                for row in range(current_sections, sections):
                    model.setData(model.index(row, 0), QtCore.QSize(50, self.defaultSectionSize()), QtCore.Qt.ItemDataRole.SizeHintRole)

    def setSectionLabel(self, section: int, label: str) -> None:
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            index = self.model().index(0, section)
        else:
            index = self.model().index(section, 0)

        self.model().setData(index, label, QtCore.Qt.ItemDataRole.DisplayRole)

    def setSectionBackgroundColor(self, section: int, color: QtGui.QColor) -> None:
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            index = self.model().index(0, section)
        else:
            index = self.model().index(section, 0)

        self.model().setData(index, color, QtCore.Qt.ItemDataRole.BackgroundRole)

    def setSectionForegroundColor(self, section: int, color: QtGui.QColor) -> None:
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            index = self.model().index(0, section)
        else:
            index = self.model().index(section, 0)

        self.model().setData(index, color, QtCore.Qt.ItemDataRole.ForegroundRole)

    def indexAt(self, pos: QtCore.QPoint) -> QtCore.QModelIndex:
        tbl_model: QSpanHeaderModel = self.model()

        if tbl_model.columnCount() == 0 or tbl_model.rowCount() == 0:
            return QtCore.QModelIndex()

        logical_idx = self.logicalIndexAt(pos)
        delta = 0
        
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            cell_index = tbl_model.index(0, logical_idx)

            if cell_index.isValid():
                cell_size: QtCore.QSize = cell_index.data(QtCore.Qt.ItemDataRole.SizeHintRole)
                delta += cell_size.height()
                    
                if pos.y() <= delta:
                    return cell_index
            
        else:
            cell_index = tbl_model.index(logical_idx, 0)
            
            if cell_index.isValid():
                cell_size: QtCore.QSize = cell_index.data(QtCore.Qt.ItemDataRole.SizeHintRole)
                delta += cell_size.width()
                
                if pos.x() <= delta:
                    return cell_index

        return QtCore.QModelIndex()

    def paintSection(self, painter: QtGui.QPainter, rect: QtCore.QRect, logical_index: int) -> None:
        tbl_model: QSpanHeaderModel = self.model()

        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            cell_index = tbl_model.index(0, logical_index)
        else:
            cell_index = tbl_model.index(logical_index, 0)

        cell_size: QtCore.QSize = cell_index.data(QtCore.Qt.ItemDataRole.SizeHintRole)
        section_rect = QtCore.QRect(rect)

        section_rect.setSize(cell_size)

        # check up span column or row
        col_span_idx = self.columnSpanIndex(cell_index)
        row_span_idx = self.rowSpanIndex(cell_index)
        
        if col_span_idx.isValid():
            col_span_from     = col_span_idx.column()
            col_span_cnt: int = col_span_idx.data(QSpanHeaderModel.HeaderRole.ColumnSpanRole)
            col_span          = self.columnSpanSize(col_span_from, col_span_cnt)
            
            if self.orientation() == QtCore.Qt.Orientation.Horizontal:
                section_rect.setLeft(self.sectionViewportPosition(col_span_from))
            else:
                section_rect.setLeft(self.columnSpanSize(0, col_span_from))

            section_rect.setWidth(col_span)
            
            cell_index = col_span_idx
        
        if row_span_idx.isValid():
            row_span_from     = row_span_idx.row()
            row_span_cnt: int = row_span_idx.data(QSpanHeaderModel.HeaderRole.RowSpanRole)
            row_span          = self.rowSpanSize(row_span_from, row_span_cnt)
            
            if self.orientation() == QtCore.Qt.Orientation.Vertical:
                section_rect.setTop(self.sectionViewportPosition(row_span_from))
            else:
                section_rect.setTop(self.rowSpanSize(0, row_span_from))
            
            section_rect.setHeight(row_span)
            
            cell_index = row_span_idx

        # draw section with style
        opt = QtWidgets.QStyleOptionHeader()
        self.initStyleOption(opt)
        opt.textAlignment = QtCore.Qt.AlignmentFlag.AlignCenter
        opt.iconAlignment = QtCore.Qt.AlignmentFlag.AlignVCenter
        opt.section       = logical_index
        opt.text          = cell_index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        opt.rect          = section_rect

        bg = cell_index.data(QtCore.Qt.ItemDataRole.BackgroundRole)
        fg = cell_index.data(QtCore.Qt.ItemDataRole.ForegroundRole)
        
        if QtCore.QVariant(bg).canConvert(QtCore.QVariant.Type.Brush):
            opt.palette.setBrush(QtGui.QPalette.ColorRole.Button, QtGui.QBrush(bg))
            opt.palette.setBrush(QtGui.QPalette.ColorRole.Window, QtGui.QBrush(bg))
        
        if QtCore.QVariant(fg).canConvert(QtCore.QVariant.Type.Brush):
            opt.palette.setBrush(QtGui.QPalette.ColorRole.ButtonText, QtGui.QBrush(fg))

        painter.save()
        self.style().drawControl(QtWidgets.QStyle.ControlElement.CE_Header, opt, painter, self)
        painter.restore()

    def sectionSizeFromContents(self, logical_index: int) -> QtCore.QSize:
        tbl_model: QSpanHeaderModel = self.model()
                
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            cell_index = tbl_model.index(0, logical_index)
        else:
            cell_index = tbl_model.index(logical_index, 0)

        size = cell_index.data(QtCore.Qt.ItemDataRole.SizeHintRole)

        if size is None:
            size = super().sectionSizeFromContents(logical_index)
        
        return size

    def setSpan(self, section: int, span_count: int) -> None:
        md: QSpanHeaderModel = self.model()

        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            idx = md.index(0, section)
            md.setData(idx, 1,          QSpanHeaderModel.HeaderRole.RowSpanRole)
            md.setData(idx, span_count, QSpanHeaderModel.HeaderRole.ColumnSpanRole)
        else:
            idx = md.index(section, 0)
            md.setData(idx, span_count, QSpanHeaderModel.HeaderRole.RowSpanRole)
            md.setData(idx, 1,          QSpanHeaderModel.HeaderRole.ColumnSpanRole)

    def columnSpanIndex(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        tbl_model: QSpanHeaderModel = self.model()
        cur_row = index.row()
        cur_col = index.column()
        i = cur_col
        
        while i >= 0:
            span_index = tbl_model.index(cur_row, i)
            span: int  = span_index.data(QSpanHeaderModel.HeaderRole.ColumnSpanRole)
            
            if span is not None and span_index.column() + span - 1 >= cur_col:
                return span_index
            
            i -= 1
        
        return QtCore.QModelIndex()

    def rowSpanIndex(self, index: QtCore.QModelIndex) -> QtCore.QModelIndex:
        tbl_model: QSpanHeaderModel = self.model()
        cur_row = index.row()
        cur_col = index.column()
        i = cur_row
        
        while i >= 0:
            span_index = tbl_model.index(i, cur_col)
            span: int  = span_index.data(QSpanHeaderModel.HeaderRole.RowSpanRole)
            
            if span is not None and span_index.row() + span - 1 >= cur_row:
                return span_index
            
            i -= 1
        
        return QtCore.QModelIndex()

    def columnSpanSize(self, from_col: int, span_count: int) -> int:
        tbl_model: QSpanHeaderModel = self.model()
        span = 0
        
        for col in range(from_col, from_col + span_count):
            cell_size: QtCore.QSize = tbl_model.index(0, col).data(QtCore.Qt.ItemDataRole.SizeHintRole)
            span += cell_size.width()
        
        return span

    def rowSpanSize(self, from_row: int, span_count: int) -> int:
        tbl_model: QSpanHeaderModel = self.model()
        span = 0
        
        for row in range(from_row, from_row + span_count):
            cell_size: QtCore.QSize = tbl_model.index(row, 0).data(QtCore.Qt.ItemDataRole.SizeHintRole)
            span += cell_size.height()
        
        return span

    def getSectionRange(self, index: QtCore.QModelIndex, begin_section: int, end_section: int) -> int:
        col_span_idx = self.columnSpanIndex(index)
        row_span_idx = self.rowSpanIndex(index)

        if col_span_idx.isValid():
            col_span_from     = col_span_idx.column()
            col_span_cnt: int = col_span_idx.data(QSpanHeaderModel.HeaderRole.ColumnSpanRole)
            col_span_to       = col_span_from + col_span_cnt - 1
            
            if self.orientation() == QtCore.Qt.Orientation.Horizontal:
                begin_section = col_span_from
                end_section   = col_span_to
            else:
                sub_row_span_data = col_span_idx.data(QSpanHeaderModel.HeaderRole.RowSpanRole)
                
                if sub_row_span_data is not None:
                    subrow_span_from     = col_span_idx.row()
                    subrow_span_cnt: int = sub_row_span_data
                    subrow_span_to       = subrow_span_from + subrow_span_cnt - 1
                    begin_section = subrow_span_from
                    end_section = subrow_span_to

        elif row_span_idx.isValid():
            row_span_from     = row_span_idx.row()
            row_span_cnt: int = row_span_idx.data(QSpanHeaderModel.HeaderRole.RowSpanRole)
            row_span_to       = row_span_from + row_span_cnt - 1

            if self.orientation() == QtCore.Qt.Orientation.Vertical:
                begin_section = row_span_from
                end_section   = row_span_to
            else:
                subcol_span_data = row_span_idx.data(QSpanHeaderModel.HeaderRole.ColumnSpanRole)
            
                if subcol_span_data is not None:
                    subcol_span_from     = row_span_idx.column()
                    subcol_span_cnt: int = subcol_span_data
                    subcol_span_to       = subcol_span_from + subcol_span_cnt - 1
                    
                    begin_section = subcol_span_from
                    end_section   = subcol_span_to

        return begin_section, end_section

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(event)

        index = self.indexAt(event.pos())

        if index.isValid():
            if self.orientation() == QtCore.Qt.Orientation.Horizontal:
                begin_section = index.column()
            else:
                begin_section = index.row()
                        
            begin_section, end_section = self.getSectionRange(index, begin_section, begin_section)

            self.sectionPressed.emit(begin_section, end_section)

    @QtCore.pyqtSlot(int, int, int)
    def onSectionResized(self, logical_index: int, old_size: int, new_size: int) -> None:
        tbl_model: QSpanHeaderModel = self.model()

        pos = self.sectionViewportPosition(logical_index);

        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            xx, yy = pos, 0
            cell_index = tbl_model.index(0, logical_index)
        else:
            xx, yy = 0, pos
            cell_index = tbl_model.index(logical_index, 0)
        
        section_rect = QtCore.QRect(xx, yy, 0, 0)
        cell_size: QtCore.QSize = cell_index.data(QtCore.Qt.ItemDataRole.SizeHintRole)

        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            cell_size.setWidth(new_size)
        else:
            cell_size.setHeight(new_size)
        
        tbl_model.setData(cell_index, cell_size, QtCore.Qt.ItemDataRole.SizeHintRole)

        col_span_idx = self.columnSpanIndex(cell_index)
        row_span_idx = self.rowSpanIndex(cell_index)

        if col_span_idx.isValid():
            col_span_from = col_span_idx.column()
            
            if self.orientation() == QtCore.Qt.Orientation.Horizontal:
                section_rect.setLeft(self.sectionViewportPosition(col_span_from))
            else:
                section_rect.setLeft(self.columnSpanSize(0, col_span_from))

        if row_span_idx.isValid():
            row_span_from = row_span_idx.row()
            
            if self.orientation() == QtCore.Qt.Orientation.Vertical:
                section_rect.setTop(self.sectionViewportPosition(row_span_from))
            else:
                section_rect.setTop(self.rowSpanSize(0, row_span_from))

        rect_to_update = QtCore.QRect(section_rect)
        rect_to_update.setWidth(self.viewport().width() - section_rect.left())
        rect_to_update.setHeight(self.viewport().height() - section_rect.top())
        self.viewport().update(rect_to_update.normalized())