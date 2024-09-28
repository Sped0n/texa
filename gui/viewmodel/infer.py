from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage

from gui.annotations import InferRequest
from gui.model.txf import TxfModel


class Available(QObject):
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
    available: Available = Available()
    result: Signal = Signal(str)
    image: Signal = Signal(QImage)

    def __init__(self, txf_model: TxfModel, parent: QObject | None = None) -> None:
        # super init
        super().__init__(parent)

        # references
        self.__txf_model: TxfModel = txf_model

        # variables
        self.available.set_model_loaded(self.__txf_model.is_loaded())
        self.__tempreature: float = 0.5
        self.__image: QImage | None = None

        # effects
        self.__txf_model.loaded.connect(self.__txf_loaded_handler)
        self.__txf_model.output.connect(self.__txf_output_handler)

    @Slot(bool)
    def __txf_loaded_handler(self, loaded: bool) -> None:
        self.available.set_model_loaded(loaded)

    @Slot(str)
    def __txf_output_handler(self, data: str) -> None:
        self.result.emit(data)
        self.available.set_busy(False)

    def set_temperature(self, temperature: float) -> None:
        self.__tempreature = temperature

    def set_image(self, image: QImage) -> None:
        self.__image = image
        self.image.emit(image)

    def infer(self) -> None:
        if not self.available.get() or self.__image is None:
            return
        self.available.set_busy(True)
        self.__txf_model.request.emit(InferRequest(self.__image, self.__tempreature))
