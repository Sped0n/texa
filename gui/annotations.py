from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field
from PySide6.QtGui import QImage

InferMode = Literal["text_and_formula", "text_only", "formula_only"]


@dataclass
class InferRequest:
    image: QImage
    mode: InferMode


class CfgMfdNode(BaseModel):
    model_path: str = Field(min_length=1)


class CfgFormulaNode(BaseModel):
    model_name: str = Field(min_length=1)
    model_backend: str = Field(min_length=1)
    model_dir: str = Field(min_length=1)


class CfgTextNode(BaseModel):
    rec_model_name: str = Field(min_length=1)
    rec_model_backend: str = Field(min_length=1)
    rec_model_fp: str = Field(min_length=1)


class Cfg(BaseModel):
    mfd: CfgMfdNode | None = None
    formula: CfgFormulaNode | None = None
    text: CfgTextNode | None = None
