from dataclasses import dataclass
from typing import Literal

from PySide6.QtGui import QImage

InferMode = Literal["text_and_formula", "text_only", "formula_only"]


@dataclass
class InferRequest:
    image: QImage
    mode: InferMode
