from PySide6.QtCore import QStandardPaths, Slot
from PySide6.QtGui import QClipboard, QImage, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.utils import AppState, is_backend_available
from gui.viewmodel.infer import InferViewModel


class ControlView(QGroupBox):
    def __init__(
        self,
        infer_view_model: InferViewModel,
        parent: QWidget | None = None,
    ) -> None:
        """
        The control components.

        :param control_view_model: The control view model.
        :param schemas_view_model: The schemas view model.
        :param rlist_view_model: The result list view model.
        :param bar_view_model: The bar view model.
        :param parent: The parent widget, optional.
        """
        # super init
        super().__init__(title="Control", parent=parent)

        # references
        self.__infer_view_model: InferViewModel = infer_view_model

        # variables
        self.__shortcut: QShortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.__clipboard: QClipboard = QClipboard()

        # widgets
        self.__ocr_from_file_button: QPushButton = QPushButton("OCR from file")
        self.__rerun_button: QPushButton = QPushButton("Rerun")

        # widgets setup
        self.__state_handler(self.__infer_view_model.state.get())

        # effects
        self.__infer_view_model.state.changed.connect(self.__state_handler)
        self.__ocr_from_file_button.clicked.connect(self.__ocr_from_file_handler)
        self.__shortcut.activated.connect(self.__paste_handler)
        self.__rerun_button.clicked.connect(self.__rerun_handler)

        # layout
        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(self.__ocr_from_file_button)
        layout.addWidget(self.__rerun_button)
        self.setLayout(layout)

    @Slot(str)
    def __state_handler(self, data: AppState) -> None:
        flag: bool = is_backend_available(data)
        self.__ocr_from_file_button.setEnabled(flag)
        self.__rerun_button.setEnabled(flag)

    @Slot()
    def __ocr_from_file_handler(self) -> None:
        file, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.HomeLocation
            ),
            "Images (*.png *.xpm *.jpg, *.jpeg)",
        )
        if not bool(file):
            return
        image = QImage(file)
        if image.isNull():
            return
        self.__infer_view_model.set_image(image)
        self.__infer_view_model.infer()

    @Slot()
    def __rerun_handler(self) -> None:
        self.__infer_view_model.infer()

    @Slot()
    def __paste_handler(self) -> None:
        if not is_backend_available(self.__infer_view_model.state.get()):
            return

        image: QImage | None = None
        source = self.__clipboard.mimeData()

        if source.hasUrls():
            url = source.urls()[0]
            if url.isLocalFile() and url.toLocalFile().lower().endswith(
                (".png", ".jpg", ".jpeg")
            ):
                image = QImage(url.toLocalFile())
        elif source.hasImage():
            image = QImage(source.imageData())

        if image is not None and not image.isNull():
            self.__infer_view_model.set_image(image)
            self.__infer_view_model.infer()
