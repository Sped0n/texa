from PySide6.QtCore import QObject, QUrl, Signal

from gui.model.mathjax import MathjaxModel


class MDTeXViewModel(QObject):
    markdown: Signal = Signal(str)

    def __init__(
        self,
        mathjax_model: MathjaxModel,
        parent: QObject | None = None,
    ) -> None:
        # super init
        super().__init__(parent)

        # references
        self.__mathjax_model: MathjaxModel = mathjax_model

    def webview_base_url(self) -> QUrl:
        return self.__mathjax_model.base_url

    def set_mardown(self, data: str) -> None:
        self.markdown.emit(data)
