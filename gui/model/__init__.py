from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import gui.resources
from gui.model.mathjax import MathjaxModel
from gui.model.txf import TxfModel


class Model:
    def __init__(self) -> None:
        """
        The model.
        """
        # app
        self.__app: QApplication = QApplication()
        self.__app.setApplicationName("Texa")
        self.__app.setApplicationVersion("0.0.1")

        # resources
        assert gui.resources is not None

        # models
        self.mathjax_model: MathjaxModel = MathjaxModel("3.2.2")
        self.txf_model: TxfModel = TxfModel()

        # effects
        self.__app.aboutToQuit.connect(self.__quit_handler)

        # setup
        self.__app.setWindowIcon(QIcon(":/images/icon"))

    @Slot()
    def __quit_handler(self) -> None:
        """
        Quit the application.
        """
        self.txf_model.stop()

    def run(self) -> None:
        """
        Run the application.
        """
        self.__app.exec()
