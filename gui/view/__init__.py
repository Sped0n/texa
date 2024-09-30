from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

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

        # components
        self.__paste: PasteView = PasteView(view_model.infer_view_model)
        self.__render: RenderView = RenderView(view_model.mdtex_view_model)
        self.__control: ControlView = ControlView(view_model.infer_view_model)
        self.__editor: EditorView = EditorView(
            view_model.infer_view_model, view_model.mdtex_view_model
        )
        self.__stausbar: StatusBarView = StatusBarView(view_model.infer_view_model)

        # setup
        self.setWindowTitle("Texa")
        self.setMinimumSize(900, 600)
        self.setStatusBar(self.__stausbar)
        self.setWindowIcon(QIcon(":/images/icon"))

        # layout
        layout: QVBoxLayout = QVBoxLayout()

        top_layout: QHBoxLayout = QHBoxLayout()
        top_layout.addWidget(self.__paste)
        top_layout.addWidget(self.__render)

        bottom_layout: QHBoxLayout = QHBoxLayout()
        bottom_layout.addWidget(self.__control, 1)
        bottom_layout.addWidget(self.__editor, 2)

        layout.addLayout(top_layout, 3)
        layout.addLayout(bottom_layout, 2)

        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(layout)

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
        if confirmation.exec() == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
