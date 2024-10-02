from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import (
    QGridLayout,
    QMainWindow,
    QMessageBox,
    QWidget,
)

from gui.view.config import ConfigView
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
        self.__stausbar: StatusBarView = StatusBarView(
            view_model.infer_view_model, view_model.mdtex_view_model
        )
        self.__config: ConfigView = ConfigView(view_model.infer_view_model)

        # setup
        self.setWindowTitle("Texa")
        self.setMinimumSize(1000, 700)
        self.setStatusBar(self.__stausbar)
        self.setWindowIcon(QIcon(":/images/icon"))

        # layout
        layout: QGridLayout = QGridLayout()
        layout.addWidget(self.__paste, 0, 0, 5, 3)
        layout.addWidget(self.__render, 0, 3, 5, 3)
        layout.addWidget(self.__control, 5, 0, 3, 2)
        layout.addWidget(self.__config, 8, 0, 1, 2)
        layout.addWidget(self.__editor, 5, 2, 4, 4)
        layout.setVerticalSpacing(20)
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
