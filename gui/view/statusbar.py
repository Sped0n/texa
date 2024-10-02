from typing import Literal

from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import QStatusBar, QWidget

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

        # variables
        self.__animation_timer: QTimer = QTimer()
        self.__animation_timer.setInterval(400)
        self.__animation_index: Literal[1, 2, 3] = 1
        self.__state: Literal["Initializing", "Inferencing", "Ready", "Copied"] = (
            "Initializing"
        )
        self.__prev_state: Literal["Initializing", "Inferencing", "Ready", "Copied"] = (
            "Initializing"
        )

        # references
        self.__infer_view_model: InferViewModel = infer_view_model
        self.__mdtex_view_model: MDTeXViewModel = mdtex_view_model

        # effects
        self.__animation_timer.timeout.connect(self.__animation_handler)
        self.__infer_view_model.available.changed.connect(
            self.__infer_view_model_available_handler
        )
        self.__mdtex_view_model.copied.connect(self.__mdtex_view_model_copied_handler)

        # setup
        self.showMessage(self.__state)
        self.__animation_timer.start()

    def state_transition(self) -> None:
        """
        The state transition.
        """
        if self.__state == "Copied":
            self.__state = self.__prev_state
            self.showMessage(self.__state)

    @Slot()
    def __animation_handler(self) -> None:
        """
        The animation handler.
        """
        if self.__state == "Ready" or self.__state == "Copied":
            return
        self.__animation_index = (self.__animation_index % 3) + 1
        self.showMessage(f"{self.__state}{'.' * self.__animation_index}")

    @Slot(bool)
    def __infer_view_model_available_handler(self, available: bool) -> None:
        """
        The available handler.
        """
        self.__state = "Ready" if available else "Inferencing"
        self.showMessage(self.__state)

    @Slot()
    def __mdtex_view_model_copied_handler(self) -> None:
        self.__prev_state = self.__state
        self.__state = "Copied"
        self.showMessage(self.__state)
        QTimer.singleShot(1500, self.state_transition)
