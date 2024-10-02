from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage
from result import Err, Result

from gui.annotations import InferMode, InferRequest
from gui.model.p2t import P2tModel
from gui.utils import WarnMessageBox


class _Available(QObject):
    changed: Signal = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.__available: bool = False
        self.__busy: bool = False
        self.__model_loaded: bool = False

    def __update_available(self) -> None:
        self.__available = not self.__busy and self.__model_loaded
        self.changed.emit(self.__available)

    def get(self) -> bool:
        return self.__available

    def set_busy(self, busy: bool) -> None:
        self.__busy = busy
        self.__update_available()

    def set_model_loaded(self, model_loaded: bool) -> None:
        self.__model_loaded = model_loaded
        self.__update_available()


class InferViewModel(QObject):
    available: _Available = _Available()
    result: Signal = Signal(str)
    image: Signal = Signal(QImage)

    def __init__(self, p2t_model: P2tModel, parent: QObject | None = None) -> None:
        # super init
        super().__init__(parent)

        # references
        self.__p2t_model: P2tModel = p2t_model
        self.p2t_config = self.__p2t_model.config

        # variables
        self.available.set_model_loaded(self.__p2t_model.is_loaded())
        self.__mode: InferMode = "text_and_formula"
        self.__image: QImage | None = None

        # effects
        self.__p2t_model.loaded.connect(self.__p2t_loaded_handler)
        self.__p2t_model.output.connect(self.__p2t_output_handler)

    @Slot(bool)
    def __p2t_loaded_handler(self, loaded: bool) -> None:
        self.available.set_model_loaded(loaded)

    @Slot(type(Result[str, str]))
    def __p2t_output_handler(self, data: Result[str, str]) -> None:
        self.available.set_busy(False)
        if isinstance(data, Err):
            print(data.err_value)
            warn_box = WarnMessageBox(data.err_value)
            self.result.emit("$$\\color{red}\\text{Inference  Error}$$")
            warn_box.exec()
        else:
            self.result.emit(data.ok_value)

    def set_mode(self, mode: InferMode) -> None:
        self.__mode = mode

    def set_image(self, image: QImage) -> None:
        self.__image = image
        self.image.emit(image)

    def infer(self) -> None:
        if not self.available.get() or self.__image is None:
            return
        self.available.set_busy(True)
        self.__p2t_model.request.emit(InferRequest(self.__image, self.__mode))
