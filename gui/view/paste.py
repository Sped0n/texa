from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QColor, QImage, QPainter, QPaintEvent, QPixmap
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from gui.utils import AppState
from gui.viewmodel.infer import InferViewModel


class _ImageWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.__pixmap: QPixmap | None = None
        self.__is_gray: bool = False

    def setImage(self, image: QImage | QPixmap) -> None:  # noqa: N802
        if isinstance(image, QImage):
            self.__pixmap = QPixmap.fromImage(image)
        else:
            self.__pixmap = image
        self.update()

    def setGray(self, is_gray: bool) -> None:  # noqa: N802
        self.__is_gray = is_gray
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        if self.__pixmap is None:
            return
        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        scaled_pixmap: QPixmap = self.__pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x: int = (self.width() - scaled_pixmap.width()) // 2
        y: int = (self.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)

        if self.__is_gray:
            painter.setBrush(QColor(128, 128, 128, 180))
            painter.drawRect(x, y, scaled_pixmap.width(), scaled_pixmap.height())

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(300, 200)


class PasteView(QGroupBox):
    def __init__(
        self, infer_view_model: InferViewModel, parent: QWidget | None = None
    ) -> None:
        # super init
        super().__init__(title="Paste", parent=parent)

        # widget
        self.__image_widget: _ImageWidget = _ImageWidget()

        # references
        self.__infer_view_model: InferViewModel = infer_view_model

        # effects
        self.__infer_view_model.image.connect(self.__image_widget.setImage)
        self.__infer_view_model.state.changed.connect(self.__state_handler)

        # layout
        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(self.__image_widget)
        self.setLayout(layout)

    @Slot(str)
    def __state_handler(self, data: AppState) -> None:
        self.__image_widget.setGray(data == "Inferencing")
