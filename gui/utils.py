from typing import Literal

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox

AppState = Literal[
    "Initializing", "Initialization failed", "Ready", "Inferencing", "Inference failed"
]


def is_backend_available(state: AppState) -> bool:
    return state == "Ready" or state == "Inference failed"


class WarnMessageBox(QMessageBox):
    def __init__(self, text: str) -> None:
        # super init
        super().__init__()

        # widget setup
        self.setIcon(QMessageBox.Icon.Warning)
        self.setText("Warning")
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.setWindowIcon(QIcon(":/images/icon"))
        self.setOption(QMessageBox.Option.DontUseNativeDialog)
        self.setInformativeText(text)
        self.resize(200, 150)
        self.setStyleSheet("font-size: 14px;")
