from PySide6.QtCore import QObject

from gui.model import Model
from gui.viewmodel.infer import InferViewModel
from gui.viewmodel.mdtex import MDTeXViewModel


class ViewModel(QObject):
    def __init__(self, model: Model, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self.infer_view_model = InferViewModel(model.txf_model)
        self.mdtex_view_model = MDTeXViewModel(model.mathjax_model)
