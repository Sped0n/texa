from functools import partial
from pathlib import Path
from queue import Empty, Queue
from threading import Event

from huggingface_hub import (
    hf_hub_download,  # pyright: ignore[reportUnknownVariableType]
)
from PIL import ImageQt
from PySide6.QtCore import (
    QDir,
    QFile,
    QObject,
    QStandardPaths,
    QThread,
    Signal,
    Slot,
)
from PySide6.QtGui import QImage
from result import Err, Ok, Result
from texifast.model import TxfModel as TexifastModel
from texifast.pipeline import TxfPipeline as TexifastPipeline

ENCODER_MODEL_NAME = "encoder_model_quantized.onnx"
DECODER_MODEL_NAME = "decoder_model_merged_quantized.onnx"
TOKENIZER_JSON_NAME = "tokenizer.json"


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
        self.__texifast_path: Path = Path(
            QStandardPaths.standardLocations(
                QStandardPaths.StandardLocation.AppDataLocation
            )[0]
        ).joinpath("texifast")
        qd = QDir()
        if not qd.exists(str(self.__texifast_path)):
            qd.mkpath(str(self.__texifast_path))
        self.__encoder_model_path_str = str(
            self.__texifast_path.joinpath(ENCODER_MODEL_NAME)
        )
        self.__decoder_model_path_str: str = str(
            self.__texifast_path.joinpath(DECODER_MODEL_NAME)
        )
        self.__tokenizer_json_path_str: str = str(
            self.__texifast_path.joinpath(TOKENIZER_JSON_NAME)
        )

        # effects
        self.__input_conn = self.input.connect(partial(self.__input_handler))

    @Slot(QImage)
    def __input_handler(self, data: QImage) -> None:
        self.__queue.put(data)

    def __prepare_model(self) -> None:
        temp_location_str = QStandardPaths.standardLocations(
            QStandardPaths.StandardLocation.TempLocation
        )[0]
        qf = QFile()
        if not qf.exists(self.__encoder_model_path_str):
            hf_hub_download(
                "Spedon/texify-quantized-onnx",
                filename=ENCODER_MODEL_NAME,
                local_dir=temp_location_str,
            )
            f = QFile(str(Path(temp_location_str).joinpath(ENCODER_MODEL_NAME)))
            f.copy(self.__encoder_model_path_str)
            f.remove()
        if not qf.exists(self.__decoder_model_path_str):
            hf_hub_download(
                "Spedon/texify-quantized-onnx",
                filename=DECODER_MODEL_NAME,
                local_dir=temp_location_str,
            )
            f = QFile(str(Path(temp_location_str).joinpath(DECODER_MODEL_NAME)))
            f.copy(self.__decoder_model_path_str)
            f.remove()
        if not qf.exists(self.__tokenizer_json_path_str):
            hf_hub_download(
                "Spedon/texify-quantized-onnx",
                filename=TOKENIZER_JSON_NAME,
                local_dir=temp_location_str,
            )
            f = QFile(str(Path(temp_location_str).joinpath(TOKENIZER_JSON_NAME)))
            f.copy(self.__tokenizer_json_path_str)
            f.remove()

    def run(self) -> None:
        # init
        try:
            self.__prepare_model()
            model = TexifastModel(
                self.__encoder_model_path_str, self.__decoder_model_path_str
            )
            texifast = TexifastPipeline(model, self.__tokenizer_json_path_str)
            self.loaded.emit(Ok(None))
        except Exception as e:
            self.loaded.emit(Err(str(e)))
            return None

        # inference loop
        while not self.__stop.wait(0.1):
            try:
                data: QImage = self.__queue.get(timeout=0.1)
            except Empty:
                continue
            try:
                image = ImageQt.fromqimage(data).convert("RGB")
                result: str = texifast(image, max_new_tokens=768, refine_output=True)
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
