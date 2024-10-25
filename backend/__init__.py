import base64
import io
from collections.abc import Sequence
from functools import reduce
from multiprocessing import Pipe
from time import sleep

from PIL import Image
from platformdirs import user_downloads_path
from result import Err, Ok, Result
from webview import OPEN_DIALOG, Window

from .file import File
from .helpers import PyFileTypes, PyResponse
from .worker import Worker


class API:
    __file: File = File()

    def __init__(self) -> None:
        self.__window: Window | None = None
        self.__worker: Worker | None = None

        self.__local_data_pipe, self.__worker_data_pipe = Pipe()
        self.__local_msg_pipe, self.__worker_msg_pipe = Pipe()

    def bind_window(self, window: Window) -> None:
        self.__window = window

    def open_image(self) -> PyResponse:
        if not self.__window:
            return PyResponse(
                "err", "pywebview window is not bound to python API class"
            )
        result: Sequence[str] | None = self.__window.create_file_dialog(
            OPEN_DIALOG,
            directory=str(user_downloads_path()),
            allow_multiple=False,
            file_types=["Image Files (*.png;*.jpg;*.jpeg)"],
        )
        if not result:
            return PyResponse("ok", "user cancelled")
        try:
            img = Image.open(result[0])
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            data_url = f"data:image/png;base64,{img_str}"
            print("hello")
            return PyResponse("ok", data_url)
        except Exception as e:
            return PyResponse("err", str(e))

    def init_pipeline(self) -> PyResponse:
        if reduce(lambda a, b: a and b, self.__file.get_status().values()):
            if self.__worker is not None:
                return PyResponse("ok", "model pipeline already initialized")
            self.__worker = Worker(
                self.__file.encoder_model_path,
                self.__file.decoder_model_path,
                self.__file.tokenizer_json_path,
                self.__worker_data_pipe,
                self.__worker_msg_pipe,
            )
            self.__worker.daemon = True
            self.__worker.start()
            while not self.__local_msg_pipe.poll(0.1):
                pass
            result: Result[str, str] = self.__local_msg_pipe.recv()
            if isinstance(result, Ok):
                return PyResponse("ok", result.value)
            else:
                return PyResponse("err", result.value)
        else:
            return PyResponse(
                "err", "missing model files, please download or import them in settings"
            )

    def destroy_pipeline(self) -> PyResponse:
        if self.__worker is None:
            return PyResponse(
                "ok", "model pipeline not initialized, nothing to destroy"
            )
        self.__local_msg_pipe.send(Err("Stop worker"))
        self.__worker.join()
        self.__worker = None
        return PyResponse("ok", "Model pipeline destroyed")

    def infer(self, image_data: str) -> PyResponse:
        if self.__worker is None or not self.__worker.is_alive():
            return PyResponse("err", "model pipeline not initialized")
        self.__local_data_pipe.send(
            Image.open(io.BytesIO(base64.b64decode(image_data.split(",")[1])))
        )
        while not self.__local_data_pipe.poll(0.1):
            pass
        result: Result[str, str] = self.__local_data_pipe.recv()
        if isinstance(result, Ok):
            return PyResponse("ok", result.value)
        else:
            return PyResponse("err", result.value)

    def get_file_status(self) -> dict[PyFileTypes, bool]:
        return self.__file.get_status()

    def import_file(self, file_type: PyFileTypes) -> PyResponse:
        if not self.__window:
            return PyResponse(
                "err", "pywebview window is not bound to python API class"
            )
        result: Sequence[str] | None = None
        if file_type == "encoder" or file_type == "decoder":
            result = self.__window.create_file_dialog(
                OPEN_DIALOG,
                directory=str(user_downloads_path()),
                allow_multiple=False,
                file_types=["ONNX files (*.onnx)"],
            )
        else:
            result = self.__window.create_file_dialog(
                OPEN_DIALOG,
                directory=str(user_downloads_path()),
                allow_multiple=False,
                file_types=["JSON files (*.json)"],
            )
        if not result:
            return PyResponse("ok", "user cancelled")
        return self.__file.import_file_from(file_type, result[0])

    def remove_file(self, file_type: PyFileTypes) -> PyResponse:
        return self.__file.remove_file(file_type)

    def download_missing_model_from_hf(self) -> PyResponse:
        status = self.__file.get_status()
        files = []
        if not status["encoder"]:
            files.append("encoder")
        if not status["decoder"]:
            files.append("decoder")
        if not status["tokenizer"]:
            files.append("tokenizer")
        if len(files) == 0:
            return PyResponse("ok", "no missing model files")
        else:
            return self.__file.download_from_hf(files)

    def quit(self) -> None:
        if self.__window and self.__window.create_confirmation_dialog(
            title="Quit?", message="Are you sure you want to quit?"
        ):
            self.destroy_pipeline()
            sleep(0.2)
            self.__window.destroy()
            exit(0)

    def minimize(self) -> None:
        if self.__window:
            self.__window.minimize()

    def on_closing(self) -> None:
        self.destroy_pipeline()
