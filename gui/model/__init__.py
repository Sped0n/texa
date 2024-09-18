import time

from PySide6.QtWidgets import QApplication

import gui.resources
from gui.model.mathjax import Mathjax


class Model:
    def __init__(self) -> None:
        """
        The model.
        """
        # app
        self.__app: QApplication = QApplication()
        self.__app.setApplicationName("TexifyQt")
        self.__app.setApplicationVersion("1.0.2")

        # resources
        assert gui.resources is not None

        # references
        self.mathjax = Mathjax("3.2.2")

    def run(self) -> None:
        """
        Run the application.
        """
        time.sleep(5)
        self.__app.exec()
