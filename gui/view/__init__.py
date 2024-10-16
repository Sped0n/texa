from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import (
    QCloseEvent,
    QDragEnterEvent,
    QDragLeaveEvent,
    QDragMoveEvent,
    QDropEvent,
    QIcon,
    QImage,
    QResizeEvent,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from gui.utils import is_backend_available
from gui.view.control import ControlView
from gui.view.editor import EditorView
from gui.view.paste import PasteView
from gui.view.render import RenderView
from gui.view.statusbar import StatusBarView
from gui.viewmodel import ViewModel


class View(QMainWindow):
    def __init__(self, view_model: ViewModel) -> None:
        # super init
        super().__init__()

        # references
        self.__infer_view_model = view_model.infer_view_model

        # components
        self.__paste: PasteView = PasteView(view_model.infer_view_model)
        self.__render: RenderView = RenderView(view_model.mdtex_view_model)
        self.__control: ControlView = ControlView(view_model.infer_view_model)
        self.__editor: EditorView = EditorView(
            view_model.infer_view_model, view_model.mdtex_view_model
        )
        self.__stausbar: StatusBarView = StatusBarView(
            view_model.infer_view_model, view_model.mdtex_view_model
        )

        self.__overlay = QLabel(self)
        self.__overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__overlay.setText("Drop image here")
        self.__overlay.setStyleSheet("""
            background-color: rgba(50, 50, 50, 100);
            color: rgb(120, 120, 120);
            font-size: 36px;
            border: 4px dashed white;
        """)
        self.__overlay.hide()

        # setup
        self.setWindowTitle("Texa")
        self.setMinimumSize(900, 600)
        self.setStatusBar(self.__stausbar)
        self.setWindowIcon(QIcon(":/images/icon"))

        # layout
        upper_layout: QHBoxLayout = QHBoxLayout()
        upper_layout.addWidget(self.__paste, 1)
        upper_layout.addWidget(self.__render, 1)
        lower_layout: QHBoxLayout = QHBoxLayout()
        lower_layout.addWidget(self.__control, 1)
        lower_layout.addWidget(self.__editor, 2)
        layout: QVBoxLayout = QVBoxLayout()
        layout.addLayout(upper_layout, 3)
        layout.addLayout(lower_layout, 2)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(layout)

    def __is_mime_image(self, source: QMimeData) -> bool:
        image: QImage | None = None

        if source.hasUrls():
            url = source.urls()[0]
            if url.isLocalFile() and url.toLocalFile().lower().endswith(
                (".png", ".jpg", ".jpeg")
            ):
                image = QImage(url.toLocalFile())

        elif source.hasImage():
            image = QImage(source.imageData())

        if image is not None and not image.isNull():
            return True
        else:
            return False

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        confirmation: QMessageBox = QMessageBox()
        confirmation.setText("Confirmation")
        confirmation.setInformativeText("Are you sure you want to exit?")
        confirmation.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        confirmation.setDefaultButton(QMessageBox.StandardButton.No)
        confirmation.setIcon(QMessageBox.Icon.Question)
        confirmation.setWindowIcon(QIcon(":/images/icon"))
        confirmation.setOption(QMessageBox.Option.DontUseNativeDialog)
        confirmation.resize(200, 150)
        confirmation.setStyleSheet("font-size: 14px;")
        if confirmation.exec() == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self.__overlay.resize(self.size())

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if self.__is_mime_image(event.mimeData()):
            self.__overlay.resize(self.size())
            self.setEnabled(False)
            self.__overlay.show()
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:  # noqa: N802
        self.setEnabled(True)
        self.__overlay.hide()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:  # noqa: N802
        if self.__is_mime_image(event.mimeData()):
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        if not is_backend_available(self.__infer_view_model.state.get()):
            self.__overlay.hide()
            event.ignore()
            return

        source = event.mimeData()
        if not self.__is_mime_image(source):
            self.__overlay.hide()
            event.ignore()
            return

        image: QImage
        if source.hasUrls():
            image = QImage(source.urls()[0].toLocalFile())
        else:
            image = QImage(source.imageData())

        self.setEnabled(True)
        self.__overlay.hide()
        event.setDropAction(Qt.DropAction.CopyAction)
        event.accept()
        self.__infer_view_model.set_image(image)
        self.__infer_view_model.infer()
