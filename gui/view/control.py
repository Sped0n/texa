from PySide6.QtCore import QStandardPaths, Slot
from PySide6.QtGui import QClipboard, QImage, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.annotations import InferMode
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
        self.__mode_label: QLabel = QLabel("Mode")
        self.__mode_combobox: QComboBox = QComboBox()
        self.__ocr_from_file_button: QPushButton = QPushButton("OCR from file")
        self.__rerun_button: QPushButton = QPushButton("Rerun")

        # widgets setup
        self.__mode_combobox.addItems(["Text and Formula", "Text Only", "Formula Only"])
        self.__mode_combobox.setCurrentIndex(0)
        self.__ocr_from_file_button.setEnabled(False)
        self.__rerun_button.setEnabled(False)

        # effects
        self.__infer_view_model.available.changed.connect(self.__available_handler)
        self.__ocr_from_file_button.clicked.connect(self.__ocr_from_file_handler)
        self.__mode_combobox.currentIndexChanged.connect(self.__mode_index_handler)
        self.__shortcut.activated.connect(self.__paste_handler)
        self.__rerun_button.clicked.connect(self.__rerun_handler)

        # layout
        temp_layout: QHBoxLayout = QHBoxLayout()
        temp_layout.addWidget(self.__mode_label, 1)
        temp_layout.addWidget(self.__mode_combobox, 4)
        layout: QVBoxLayout = QVBoxLayout()
        layout.addLayout(temp_layout)
        layout.addWidget(self.__ocr_from_file_button)
        layout.addWidget(self.__rerun_button)
        self.setLayout(layout)

    @Slot(bool)
    def __available_handler(self, available: bool) -> None:
        self.__mode_combobox.setEnabled(available)
        self.__ocr_from_file_button.setEnabled(available)
        self.__rerun_button.setEnabled(available)

    @Slot(int)
    def __mode_index_handler(self, index: int) -> None:
        mode: InferMode | None = None
        match index:
            case 0:
                mode = "text_and_formula"
            case 1:
                mode = "text_only"
            case 2:
                mode = "formula_only"
            case _:
                return
        self.__infer_view_model.set_mode(mode)

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
        if not self.__infer_view_model.available.get():
            return
        self.__infer_view_model.infer()

    @Slot()
    def __paste_handler(self) -> None:
        if not self.__infer_view_model.available.get():
            return
        if self.__clipboard.mimeData().hasImage():
            image: QImage = self.__clipboard.image()
            if image.isNull():
                return
            self.__infer_view_model.set_image(image)
            self.__infer_view_model.infer()
