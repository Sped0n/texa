from typing import Literal

from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import QStatusBar, QWidget

from gui.utils import AppState
from gui.viewmodel.infer import InferViewModel
from gui.viewmodel.mdtex import MDTeXViewModel


class StatusBarView(QStatusBar):
    def __init__(
        self,
        infer_view_model: InferViewModel,
        mdtex_view_model: MDTeXViewModel,
        parent: QWidget | None = None,
    ) -> None:
        # super init
        super().__init__(parent)

        # references
        self.__infer_view_model: InferViewModel = infer_view_model
        self.__mdtex_view_model: MDTeXViewModel = mdtex_view_model

        # variables
        self.__animation_timer: QTimer = QTimer()
        self.__animation_timer.setInterval(400)
        self.__animation_index: Literal[1, 2, 3] = 1
        self.__display_copied_msg: bool = False

        # effects
        self.__animation_timer.timeout.connect(self.__animation_handler)
        self.__infer_view_model.state.changed.connect(self.__state_handler)
        self.__mdtex_view_model.copied.connect(self.__mdtex_view_model_copied_handler)

        # setup
        self.showMessage(self.__infer_view_model.state.get())
        self.__animation_timer.start()

    def __copied_state_transition(self) -> None:
        """
        The state transition.
        """
        self.__display_copied_msg = False
        self.showMessage(self.__infer_view_model.state.get())

    @Slot()
    def __animation_handler(self) -> None:
        """
        The animation handler.
        """
        tmp = self.__infer_view_model.state.get()
        if (
            tmp == "Ready"
            or tmp == "Initialization failed"
            or tmp == "Inference failed"
            or self.__display_copied_msg is True
        ):
            return
        self.__animation_index = (self.__animation_index % 3) + 1
        self.showMessage(f"{tmp}{'.' * self.__animation_index}")

    @Slot(str)
    def __state_handler(self, data: AppState) -> None:
        """
        The available handler.
        """
        self.showMessage(data)

    @Slot()
    def __mdtex_view_model_copied_handler(self) -> None:
        self.__display_copied_msg = True
        self.showMessage("Copied to clipboard")
        QTimer.singleShot(1500, self.__copied_state_transition)
