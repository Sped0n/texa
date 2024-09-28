from dataclasses import dataclass

from PySide6.QtGui import QImage


@dataclass
class InferRequest:
    image: QImage
    tempreature: float
