from PySide6.QtCore import QMimeData, QTimer, Signal, Slot
from PySide6.QtGui import QClipboard, QImage
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.viewmodel.infer import InferViewModel
from gui.viewmodel.mdtex import MDTeXViewModel


class _TextEdit(QTextEdit):
    paste_image: Signal = Signal(QImage)

    def insertFromMimeData(self, source: QMimeData):  # noqa: N802
        if source.hasImage():
            image = QImage(source.imageData())
            if image.isNull():
                return
            self.paste_image.emit(image)
        else:
            super().insertFromMimeData(source)


class EditorView(QGroupBox):
    def __init__(
        self,
        infer_view_model: InferViewModel,
        mdtex_view_model: MDTeXViewModel,
        parent: QWidget | None = None,
    ) -> None:
        # super init
        super().__init__(title="Editor", parent=parent)

        # reference
        self.__infer_view_model: InferViewModel = infer_view_model
        self.__mdtex_view_model: MDTeXViewModel = mdtex_view_model

        # widgets
        self.__text_edit: _TextEdit = _TextEdit()
        self.__copy_button: QPushButton = QPushButton("Copy")
        self.__clear_button: QPushButton = QPushButton("Clear")

        # variables
        self.__debouncer: QTimer = QTimer()

        # setup
        self.__debouncer.setInterval(400)
        self.__debouncer.setSingleShot(True)

        # effects
        self.__text_edit.textChanged.connect(self.__debouncer.start)
        self.__infer_view_model.result.connect(self.__infer_result_handler)
        self.__debouncer.timeout.connect(self.__debounced)
        self.__copy_button.clicked.connect(self.__copy_button_clicked)
        self.__clear_button.clicked.connect(self.__clear_button_clicked)
        self.__text_edit.paste_image.connect(self.__paste_handler)

        # layout
        layout: QVBoxLayout = QVBoxLayout()
        button_layout: QHBoxLayout = QHBoxLayout()
        button_layout.addWidget(self.__copy_button)
        button_layout.addWidget(self.__clear_button)
        layout.addWidget(self.__text_edit, 4)
        layout.addLayout(button_layout, 1)
        self.setLayout(layout)

    @Slot(str)
    def __infer_result_handler(self, infer_result: str) -> None:
        self.__text_edit.clear()
        self.__mdtex_view_model.set_mardown(infer_result)
        self.__text_edit.setText(infer_result)

    @Slot()
    def __debounced(self) -> None:
        self.__mdtex_view_model.set_mardown(self.__text_edit.toPlainText())

    @Slot()
    def __copy_button_clicked(self) -> None:
        QClipboard().setText(self.__text_edit.toPlainText())
        self.__mdtex_view_model.copied.emit()

    @Slot()
    def __clear_button_clicked(self) -> None:
        self.__text_edit.clear()

    @Slot(QImage)
    def __paste_handler(self, data: QImage) -> None:
        if not self.__infer_view_model.available.get():
            return
        self.__infer_view_model.set_image(data)
        self.__infer_view_model.infer()
