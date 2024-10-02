from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QWidget

from gui.view.modal.models import ModelsDialog
from gui.viewmodel.infer import InferViewModel


class ConfigView(QGroupBox):
    def __init__(
        self, infer_view_model: InferViewModel, parent: QWidget | None = None
    ) -> None:
        # super init
        super().__init__(title="Configuration", parent=parent)

        # references
        self.__infer_view_model: InferViewModel = infer_view_model

        # widgets
        self.__models_button: QPushButton = QPushButton("Models")

        # effects
        self.__models_button.clicked.connect(self.__models_button_clicked)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.__models_button)
        self.setLayout(layout)

    def __models_button_clicked(self) -> None:
        dialog = ModelsDialog(self.__infer_view_model)
        dialog.exec()
