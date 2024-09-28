from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from gui.view.control import ControlView
from gui.view.editor import EditorView
from gui.view.paste import PasteView
from gui.view.render import RenderView
from gui.viewmodel import ViewModel


class View(QMainWindow):
    def __init__(self, view_model: ViewModel) -> None:
        # super init
        super().__init__()

        # setup
        self.setWindowTitle("Texa")
        self.setMinimumSize(900, 600)

        # components
        self.__paste: PasteView = PasteView(view_model.infer_view_model)
        self.__render: RenderView = RenderView(view_model.mdtex_view_model)
        self.__control: ControlView = ControlView(view_model.infer_view_model)
        self.__editor: EditorView = EditorView(
            view_model.infer_view_model, view_model.mdtex_view_model
        )

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
