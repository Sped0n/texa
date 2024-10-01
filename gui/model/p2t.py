import gc
import os
from functools import partial
from pathlib import Path
from queue import Empty, Queue
from threading import Event

from PIL import ImageQt
from PySide6.QtCore import (
    QObject,
    QStandardPaths,
    QThread,
    Signal,
    SignalInstance,
    Slot,
)

from gui.annotations import InferRequest


class _P2tWroker(QObject):
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

        # for matplotlib
        app_data_dir: str = QStandardPaths.standardLocations(
            QStandardPaths.StandardLocation.AppDataLocation
        )[0]
        mpl_config_dir: str = str(Path(app_data_dir).joinpath("mpl"))
        os.environ["MPLCONFIGDIR"] = mpl_config_dir

        # effects
        self.__conn1 = self.__request.connect(partial(self.__request_handler))

    @Slot(InferRequest)
    def __request_handler(self, data: InferRequest) -> None:
        self.__queue.put(data)

    def run(self) -> None:
        # load the ocr engine
        from pix2text import Pix2Text

        p2t: Pix2Text | None = None
        self.__loaded.emit(True)

        # inference loop
        while not self.__stop.wait(0.1):
            try:
                if p2t is None:
                    p2t = Pix2Text()
                request: InferRequest = self.__queue.get(timeout=0.1)
                image = ImageQt.fromqimage(request.image).convert("RGB")
                result: str | None = None
                match request.mode:
                    case "text_and_formula":
                        result = str(p2t.recognize_text_formula(image, line_sep="\n\n"))
                    case "text_only":
                        result = str(p2t.recognize_text(image))
                    case "formula_only":
                        result = str(p2t.recognize_formula(image))
                self.__output.emit(result)
                del p2t
                p2t = None
                gc.collect()
            except Empty:
                pass

        # disconnect
        self.__request.disconnect(self.__conn1)

    def stop(self) -> None:
        self.__stop.set()


class P2tModel(QObject):
    request: Signal = Signal(InferRequest)
    output: Signal = Signal(str)
    loaded: Signal = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        # super init
        super().__init__(parent)

        # variables
        self.__worker: _P2tWroker | None = None
        self.__thread: QThread | None = None
        self.__loaded_state: bool = False

        # effects
        self.loaded.connect(self.__loaded_handler)

        # setup
        self.__start_worker()

    def __start_worker(self) -> None:
        self.__worker = _P2tWroker(self.request, self.output, self.loaded)  # pyright: ignore[reportUnknownArgumentType]
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
