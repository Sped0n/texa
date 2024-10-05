import gc
import os
from functools import partial
from pathlib import Path
from queue import Empty, Queue
from threading import Event

from PIL import ImageQt
from pydantic import ValidationError
from PySide6.QtCore import (
    QDir,
    QFile,
    QIODevice,
    QObject,
    QStandardPaths,
    QThread,
    Signal,
    SignalInstance,
    Slot,
)
from result import Err, Ok, Result

from gui.annotations import (
    Cfg,
    CfgFormulaNode,
    CfgMfdNode,
    CfgTextNode,
    InferRequest,
)


class _P2tConfig(QObject):
    changed: Signal = Signal(Cfg)

    def __init__(self) -> None:
        # super init
        super().__init__()

        # paths
        app_data_dir: str = QStandardPaths.standardLocations(
            QStandardPaths.StandardLocation.AppDataLocation
        )[0]

        # for matplotlib
        mpl_config_dir: str = str(Path(app_data_dir).joinpath("mpl"))
        os.environ["MPLCONFIGDIR"] = mpl_config_dir

        # for p2t pro model files
        # check if the p2t model directory exists
        p2t_model_dir_str: str = str(Path(app_data_dir).joinpath("p2t"))
        self.__p2t_model_dir: QDir = QDir(p2t_model_dir_str)
        if not self.__p2t_model_dir.exists():
            self.__p2t_model_dir.mkpath(".")
        self.__config_file: QFile = QFile(
            str(Path(p2t_model_dir_str).joinpath("config.json"))
        )
        self.__config: Cfg
        need_recovery: bool = False
        # check if the config file exists
        if self.__config_file.exists():
            self.__config_file.open(
                QFile.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text
            )
            try:
                self.__config = Cfg.model_validate_json(
                    bytes(self.__config_file.readAll().data()).decode()
                )
            except ValidationError:
                need_recovery = True
            finally:
                self.__config_file.close()
        else:
            need_recovery = True
        # recover the config file if needed
        if need_recovery:
            self.__config = Cfg()
            self.__config_file.open(
                QFile.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text
            )
            self.__config_file.write(
                self.__config.model_dump_json(indent=2, exclude_none=True).encode()
            )
            self.__config_file.close()

        # effects
        self.changed.connect(self.__changed_handler)

    @Slot(Cfg)
    def __changed_handler(self, cfg: Cfg) -> None:
        self.__config_file.open(
            QFile.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text
        )
        self.__config_file.write(
            cfg.model_dump_json(indent=2, exclude_none=True).encode()
        )
        self.__config_file.close()

    def get_config(self) -> Cfg:
        return self.__config

    def set_mfd(self, node: CfgMfdNode) -> None:
        # create target directory if needed
        mfd_dir: QDir = QDir(Path(self.__p2t_model_dir.absolutePath()).joinpath("mfd"))
        if not mfd_dir.exists():
            mfd_dir.mkpath(mfd_dir.absolutePath())
        # copy file
        file = QFile(node.model_path)
        target_path = Path(mfd_dir.absolutePath()).joinpath(file.fileName())
        file.copy(target_path)
        # update config
        self.__config.mfd = CfgMfdNode(model_path=str(target_path))
        self.changed.emit(self.__config)

    def reset_mfd(self) -> None:
        # do nothing if the mfd is not set
        if self.__config.mfd is None:
            return None
        # remove file
        file = QFile(self.__config.mfd.model_path)
        file.remove()
        # update config
        self.__config.mfd = None
        self.changed.emit(self.__config)

    def set_formula(self, node: CfgFormulaNode) -> None:
        # create target directory if needed
        target_dir: QDir = QDir(
            Path(self.__p2t_model_dir.absolutePath())
            .joinpath("formula")
            .joinpath(node.model_name)
        )
        if not target_dir.exists():
            target_dir.mkpath(target_dir.absolutePath())
        # copy files
        from_dir: QDir = QDir(node.model_dir)
        for file_info in from_dir.entryInfoList(
            QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        ):
            file = QFile(file_info.absoluteFilePath())
            file.copy(Path(target_dir.absolutePath()).joinpath(file_info.fileName()))
        # update config
        self.__config.formula = CfgFormulaNode(
            model_name=node.model_name,
            model_backend=node.model_backend,
            model_dir=target_dir.absolutePath(),
        )
        self.changed.emit(self.__config)

    def reset_formula(self) -> None:
        # do nothing if the formula is not set
        if self.__config.formula is None:
            return None
        # remove files and directory
        target_dir: QDir = QDir(
            Path(self.__p2t_model_dir.absolutePath())
            .joinpath("formula")
            .joinpath(self.__config.formula.model_name)
        )
        for file_info in target_dir.entryInfoList(
            QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        ):
            file = QFile(file_info.absoluteFilePath())
            file.remove()
        target_dir.rmdir(target_dir.absolutePath())
        # update config
        self.__config.formula = None
        self.changed.emit(self.__config)

    def set_text(self, node: CfgTextNode) -> None:
        # create target directory if needed
        target_dir: QDir = QDir(
            Path(self.__p2t_model_dir.absolutePath()).joinpath("text")
        )
        if not target_dir.exists():
            target_dir.mkpath(target_dir.absolutePath())
        # copy file
        file = QFile(node.rec_model_fp)
        target_path = Path(target_dir.absolutePath()).joinpath(file.fileName())
        file.copy(target_path)
        # update config
        self.__config.text = CfgTextNode(
            rec_model_name=node.rec_model_name,
            rec_model_backend=node.rec_model_backend,
            rec_model_fp=str(target_path),
        )

    def reset_text(self) -> None:
        # do nothing if the text is not set
        if self.__config.text is None:
            return None
        # remove file
        file = QFile(self.__config.text.rec_model_fp)
        file.remove()
        # update config
        self.__config.text = None
        self.changed.emit(self.__config)


class _P2tWroker(QObject):
    def __init__(
        self,
        cfg: _P2tConfig,
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
        self.__cfg_inst: _P2tConfig = cfg
        self.__cfg: Cfg = self.__cfg_inst.get_config()
        self.__stop: Event = Event()
        self.__queue: Queue[InferRequest] = Queue(3)

        # effects
        self.__conn1 = self.__request.connect(partial(self.__request_handler))
        self.__conn2 = self.__cfg_inst.changed.connect(partial(self.__config_handler))

    @Slot(InferRequest)
    def __request_handler(self, data: InferRequest) -> None:
        self.__queue.put(data)

    @Slot(Cfg)
    def __config_handler(self, cfg: Cfg) -> None:
        self.__cfg = cfg

    def run(self) -> None:
        # load the ocr engine
        from texify.inference import batch_inference
        from texify.model.model import load_model
        from texify.model.processor import load_processor

        model = load_model()
        processor = None
        self.__loaded.emit(True)

        # inference loop
        while not self.__stop.wait(0.1):
            try:
                request: InferRequest = self.__queue.get(timeout=0.1)
            except Empty:
                continue
            try:
                if processor is None:
                    processor = load_processor()
                image = ImageQt.fromqimage(request.image).convert("RGB")
                result: str = batch_inference([image], model, processor)[0]
                self.__output.emit(Ok(result))
            except Exception as e:
                self.__output.emit(Err(str(e)))
            del processor
            processor = None
            gc.collect()

        # disconnect
        self.__request.disconnect(self.__conn1)
        self.__cfg_inst.changed.disconnect(self.__conn2)

    def stop(self) -> None:
        self.__stop.set()


class P2tModel(QObject):
    request: Signal = Signal(InferRequest)
    output: Signal = Signal(type(Result[str, str]))
    loaded: Signal = Signal(bool)

    config: _P2tConfig = _P2tConfig()

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
        self.__worker = _P2tWroker(self.config, self.request, self.output, self.loaded)  # pyright: ignore[reportUnknownArgumentType]
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
