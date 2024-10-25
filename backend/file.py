import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from huggingface_hub import hf_hub_download
from platformdirs import user_data_dir

from .helpers import PyFileTypes, PyResponse

APP_NAME = "Texa"
AUTHOR_NAME = "Spedon"

ENCODER_MODEL_NAME = "encoder_model_quantized.onnx"
DECODER_MODEL_NAME = "decoder_model_merged_quantized.onnx"
TOKENIZER_JSON_NAME = "tokenizer.json"

FileType = Literal["encoder", "decoder", "tokenizer"]


class File:
    def __init__(self):
        self.__texifast_path: Path = Path(
            user_data_dir(appname=APP_NAME, appauthor=AUTHOR_NAME)
        ).joinpath("texifast")
        if not self.__texifast_path.exists():
            self.__texifast_path.mkdir(parents=True, exist_ok=True)
        self.__encoder_model_path: Path = self.__texifast_path.joinpath(
            ENCODER_MODEL_NAME
        )
        self.__decoder_model_path: Path = self.__texifast_path.joinpath(
            DECODER_MODEL_NAME
        )
        self.__tokenizer_json_path: Path = self.__texifast_path.joinpath(
            TOKENIZER_JSON_NAME
        )

    @property
    def encoder_model_path(self) -> Path:
        return self.__encoder_model_path

    @property
    def decoder_model_path(self) -> Path:
        return self.__decoder_model_path

    @property
    def tokenizer_json_path(self) -> Path:
        return self.__tokenizer_json_path

    def get_status(self) -> dict[PyFileTypes, bool]:
        return {
            "encoder": self.__encoder_model_path.exists(),
            "decoder": self.__decoder_model_path.exists(),
            "tokenizer": self.__tokenizer_json_path.exists(),
        }

    def download_from_hf(self, files: list[FileType]) -> PyResponse:
        try:
            with TemporaryDirectory() as temp_location_str:
                for file_type in files:
                    match file_type:
                        case "encoder":
                            file_name = ENCODER_MODEL_NAME
                        case "decoder":
                            file_name = DECODER_MODEL_NAME
                        case "tokenizer":
                            file_name = TOKENIZER_JSON_NAME
                    hf_hub_download(
                        "Spedon/texify-quantized-onnx",
                        filename=file_name,
                        local_dir=temp_location_str,
                    )
                    file_path = Path(temp_location_str).joinpath(file_name)
                    shutil.copy(file_path, self.__texifast_path)
            return PyResponse("ok", "Download Complete")
        except Exception as e:
            return PyResponse("err", str(e))

    def import_file_from(
        self, file_type: PyFileTypes, file_path_str: str
    ) -> PyResponse:
        try:
            if file_type == "encoder":
                if self.__encoder_model_path.exists():
                    self.__encoder_model_path.unlink()
                shutil.copy(file_path_str, self.__encoder_model_path)
            elif file_type == "decoder":
                if self.__decoder_model_path.exists():
                    self.__decoder_model_path.unlink()
                shutil.copy(file_path_str, self.__decoder_model_path)
            else:
                if self.__tokenizer_json_path.exists():
                    self.__tokenizer_json_path.unlink()
                shutil.copy(file_path_str, self.__tokenizer_json_path)
            return PyResponse("ok", "import Complete")
        except Exception as e:
            return PyResponse("err", str(e))

    def remove_file(self, file_type: PyFileTypes) -> PyResponse:
        try:
            if file_type == "encoder":
                if self.__encoder_model_path.exists():
                    self.__encoder_model_path.unlink()
            elif file_type == "decoder":
                if self.__decoder_model_path.exists():
                    self.__decoder_model_path.unlink()
            else:
                if self.__tokenizer_json_path.exists():
                    self.__tokenizer_json_path.unlink()
            return PyResponse("ok", "File Removed")
        except Exception as e:
            return PyResponse("err", str(e))
