from functools import partial
from queue import Empty, Queue
from threading import Event

from optimum.onnxruntime import ORTModelForVision2Seq
from optimum.pipelines import pipeline  # pyright: ignore[reportUnknownVariableType]
from PIL import ImageQt
from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    Slot,
)
from PySide6.QtGui import QImage
from result import Err, Ok, Result


class _TxfWroker(QObject):
    input: Signal = Signal(QImage)
    output: Signal = Signal(type(Result[str, str]))
    loaded: Signal = Signal(type(Result[None, str]))

    def __init__(self) -> None:
        # super init
        super().__init__()

        # variables
        self.__stop: Event = Event()
        self.__queue: Queue[QImage] = Queue(3)

        # effects
        self.__input_conn = self.input.connect(partial(self.__input_handler))

    @Slot(QImage)
    def __input_handler(self, data: QImage) -> None:
        self.__queue.put(data)

    def run(self) -> None:
        # init
        initialized: bool = False
        try:
            model = ORTModelForVision2Seq.from_pretrained(
                "Spedon/texify-quantized-onnx"
            )
            texify = pipeline(
                "image-to-text",
                model,
                feature_extractor="Spedon/texify-quantized-onnx",
                image_processor="Spedon/texify-quantized-onnx",
            )
            initialized = True
            self.loaded.emit(Ok(None))
        except Exception as e:
            self.loaded.emit(Err(str(e)))
        finally:
            if not initialized:
                return

        # inference loop
        while not self.__stop.wait(0.1):
            try:
                data: QImage = self.__queue.get(timeout=0.1)
            except Empty:
                continue
            try:
                image = ImageQt.fromqimage(data).convert("RGB")
                result: str = texify(image, max_new_tokens=768)[0]["generated_text"]  # pyright: ignore[reportIndexIssue,reportOptionalSubscript,reportArgumentType,reportAssignmentType,reportPossiblyUnboundVariable]
                self.output.emit(Ok(result))
            except Exception as e:
                self.output.emit(Err(str(e)))

    def stop(self) -> None:
        self.__stop.set()
        self.input.disconnect(self.__input_conn)


class TxfModel(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        # super init
        super().__init__(parent)

        # variables
        self.__worker: _TxfWroker = _TxfWroker()
        self.__thread: QThread = QThread()
        self.__loaded_state: bool = False

        # exposed signals
        self.input = self.__worker.input
        self.output = self.__worker.output
        self.loaded = self.__worker.loaded

        # effects
        self.loaded.connect(self.__loaded_handler)

        # setup
        self.__worker.moveToThread(self.__thread)
        self.__thread.started.connect(self.__worker.run)
        self.__thread.start()

    @Slot(type(Result[None, str]))
    def __loaded_handler(self, state: Result[None, str]) -> None:
        self.__loaded_state = isinstance(state, Ok)

    def is_loaded(self) -> bool:
        return self.__loaded_state

    def stop(self) -> None:
        self.__worker.stop()
        self.__thread.quit()
        self.__thread.wait()
        self.__worker.deleteLater()
        self.__thread.deleteLater()
        self.deleteLater()
