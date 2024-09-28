from functools import partial
from queue import Empty, Queue
from threading import Event
from typing import Any

from PIL import ImageQt
from PySide6.QtCore import QObject, QThread, QTimer, Signal, SignalInstance, Slot
from texify.inference import (
    batch_inference,  # pyright: ignore[reportUnknownVariableType]
)
from texify.model.model import load_model
from texify.model.processor import VariableDonutProcessor, load_processor
from transformers import PreTrainedModel

from gui.annotations import InferRequest


class _TxfWroker(QObject):
    def __init__(
        self,
        request: SignalInstance,
        output: SignalInstance,
        loaded: SignalInstance,
    ) -> None:
        # super init
        super().__init__()

        # signals
        self.__request: SignalInstance = request
        self.__output: SignalInstance = output
        self.__loaded: SignalInstance = loaded

        # variables
        self.__stop: Event = Event()
        self.__queue: Queue[InferRequest] = Queue(3)

        # effects
        self.__conn1 = self.__request.connect(partial(self.__request_handler))

    @Slot(InferRequest)
    def __request_handler(self, data: InferRequest) -> None:
        self.__queue.put(data)

    def run(self) -> None:
        # load model and processor
        model: PreTrainedModel = load_model()
        processor: (  # pyright: ignore[reportUnknownVariableType]
            tuple[VariableDonutProcessor, dict[str, Any]] | VariableDonutProcessor
        ) = load_processor()
        self.__loaded.emit(True)

        # inference loop
        while not self.__stop.wait(0.1):
            try:
                request: InferRequest = self.__queue.get(timeout=0.1)
                result: str = batch_inference(
                    [ImageQt.fromqimage(request.image).convert("RGB")],
                    model,  # pyright: ignore[reportUnknownArgumentType]
                    processor,  # pyright: ignore[reportUnknownArgumentType]
                    request.tempreature,
                )[0]
                self.__output.emit(result)
            except Empty:
                pass

        # disconnect
        self.__request.disconnect(self.__conn1)

    def stop(self) -> None:
        self.__stop.set()


class TxfModel(QObject):
    request: Signal = Signal(InferRequest)
    output: Signal = Signal(str)
    loaded: Signal = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        # super init
        super().__init__(parent)

        # variables
        self.__worker: _TxfWroker | None = None
        self.__thread: QThread | None = None
        self.__loaded_state: bool = False

        # don't spin up worker immediately
        QTimer.singleShot(300, self.__start_worker)

        # effects
        self.loaded.connect(self.__loaded_handler)

    def __start_worker(self) -> None:
        self.__worker = _TxfWroker(self.request, self.output, self.loaded)  # pyright: ignore[reportUnknownArgumentType]
        self.__thread = QThread()
        self.__worker.moveToThread(self.__thread)
        self.__thread.started.connect(self.__worker.run)
        self.__thread.start()

    @Slot(bool)
    def __loaded_handler(self, state: bool) -> None:
        self.__loaded_state = state

    def is_loaded(self) -> bool:
        return self.__loaded_state

    def stop(self) -> None:
        if self.__worker is not None and self.__thread is not None:
            self.__worker.stop()
            self.__thread.quit()
            self.__thread.wait()
            self.__worker.deleteLater()
            self.__thread.deleteLater()
            self.deleteLater()
