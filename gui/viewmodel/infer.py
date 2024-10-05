from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage
from result import Err, Result

from gui.model.txf import TxfModel
from gui.utils import AppState, WarnMessageBox, is_backend_available


class _State(QObject):
    changed: Signal = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.__value: AppState = "Initializing"
        self.__busy: bool = False
        self.__model_loaded: bool = False

    def get(self) -> AppState:
        return self.__value

    def set(self, value: AppState) -> None:
        self.__value = value
        self.changed.emit(self.__value)


class InferViewModel(QObject):
    state: _State = _State()
    result: Signal = Signal(str)
    image: Signal = Signal(QImage)

    def __init__(self, txf_model: TxfModel, parent: QObject | None = None) -> None:
        # super init
        super().__init__(parent)

        # references
        self.__txf_model = txf_model

        # variables
        self.state.set("Ready" if self.__txf_model.is_loaded() else "Initializing")
        self.__image: QImage | None = None

        # effects
        self.__txf_model.loaded.connect(self.__txf_loaded_handler)
        self.__txf_model.output.connect(self.__txf_output_handler)

    @Slot(type(Result[None, str]))
    def __txf_loaded_handler(self, data: Result[None, str]) -> None:
        if isinstance(data, Err):
            self.state.set("Initialization failed")
            warn_box = WarnMessageBox(data.err_value)
            warn_box.exec()
        else:
            self.state.set("Ready")

    @Slot(type(Result[str, str]))
    def __txf_output_handler(self, data: Result[str, str]) -> None:
        if isinstance(data, Err):
            self.state.set("Inference failed")
            self.result.emit("$$\\color{red}\\text{Inference  Error}$$")
            warn_box = WarnMessageBox(data.err_value)
            warn_box.exec()
        else:
            self.state.set("Ready")
            self.result.emit(data.ok_value)

    def set_image(self, image: QImage) -> None:
        self.__image = image
        self.image.emit(image)

    def infer(self) -> None:
        if not is_backend_available(self.state.get()):
            return
        self.state.set("Inferencing")
        self.__txf_model.input.emit(self.__image)
