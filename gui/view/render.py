from markdown import Markdown
from PySide6.QtCore import Slot
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

from gui.viewmodel.mdtex import MDTeXViewModel


class _WebView(QWebEngineView):
    def dragEnterEvent(self, e: QDragEnterEvent) -> None:  # noqa: N802
        e.ignore()

    def dragMoveEvent(self, e: QDragMoveEvent) -> None:  # noqa: N802
        e.ignore()

    def dropEvent(self, e: QDropEvent) -> None:  # noqa: N802
        e.ignore()


class RenderView(QGroupBox):
    def __init__(
        self, mdtex_view_model: MDTeXViewModel, parent: QWidget | None = None
    ) -> None:
        # super init
        super().__init__(title="Render", parent=parent)

        # reference
        self.__mdtex_view_model: MDTeXViewModel = mdtex_view_model

        # variables
        self.__converter: Markdown = Markdown(extensions=["pymdownx.arithmatex"])

        # widgets
        self.__webview: _WebView = _WebView()

        # effects
        self.__mdtex_view_model.markdown.connect(self.__markdown_handler)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.__webview)
        self.setLayout(layout)

    def __html_skeleton(self, content: str) -> str:
        return (
            """
            <html><script async src=tex-chtml-full.js></script><script>window.MathJax = {
            options: {
                ignoreHtmlClass: 'tex2jax_ignore',
                processHtmlClass: 'tex2jax_process',
                renderActions: {
                find: [10, function (doc) {
                    for (const node of document.querySelectorAll('script[type^="math/tex"]')) {
                    const display = !!node.type.match(/; *mode=display/);
                    const math = new doc.options.MathItem(node.textContent, doc.inputJax[0], display);
                    const text = document.createTextNode('');
                    const sibling = node.previousElementSibling;
                    node.parentNode.replaceChild(text, node);
                    math.start = {node: text, delim: '', n: 0};
                    math.end = {node: text, delim: '', n: 0};
                    doc.math.push(math);
                    if (sibling && sibling.matches('.MathJax_Preview')) {
                        sibling.parentNode.removeChild(sibling);
                    }
                    }
                }, '']
                }
            }
            };</script><style>body{font-family:system-ui,sans-serif}</style></head><body>
            """
            + content
            + "</body></html>"
        )

    @Slot(str)
    def __markdown_handler(self, md: str) -> None:
        html_string: str = self.__converter.convert(md)
        self.__webview.setHtml(
            self.__html_skeleton(html_string),
            self.__mdtex_view_model.webview_base_url(),
        )
