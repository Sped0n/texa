from __future__ import annotations

from multiprocessing import Process
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image
from result import Err, Ok, Result
from texifast.model import TxfModel
from texifast.pipeline import TxfPipeline

from .helpers import replace_katex_invalid

if TYPE_CHECKING:
    from multiprocessing.connection import PipeConnection


class Worker(Process):
    def __init__(
        self,
        encoder_model_path: Path,
        decoder_model_path: Path,
        tokenizer_json_path: Path,
        data_pipe: PipeConnection,
        msg_pipe: PipeConnection,
    ):
        super().__init__()

        self.__encoder_model_path = encoder_model_path
        self.__decoder_model_path = decoder_model_path
        self.__tokenizer_json_path = tokenizer_json_path
        self.__data_pipe = data_pipe
        self.__msg_pipe = msg_pipe

    def run(self):
        try:
            self.__model = TxfModel(
                self.__encoder_model_path, self.__decoder_model_path
            )
            self.__pipeline = TxfPipeline(self.__model, self.__tokenizer_json_path)
            self.__msg_pipe.send(Ok("Model pipeline initialized"))
        except Exception as e:
            self.__msg_pipe.send(Err(str(e)))
            return
        image: Image.Image | None = None
        while True:
            if self.__data_pipe.poll(0.1):
                image = self.__data_pipe.recv()
            if self.__msg_pipe.poll(0.1):
                msg: Result[str, str] = self.__msg_pipe.recv()
                if isinstance(msg, Err):
                    break  # stop worker
            if image is None:
                continue
            try:
                result = self.__pipeline(image, refine_output=True)
                result = replace_katex_invalid(result)
                self.__data_pipe.send(Ok(result))
                image = None
            except Exception as e:
                self.__data_pipe.send(Err(str(e)))
