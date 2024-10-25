from json import JSONEncoder
from multiprocessing import freeze_support
from typing import Any

import webview

from backend import API

if __name__ == "__main__":
    # Monkey patch JSONEncoder to handle dataclasses
    def _default(self: JSONEncoder, obj: Any):  # pyright: ignore[]
        return getattr(obj.__class__, "to_dict", _default.default)(obj)  # pyright: ignore[]

    _default.default = JSONEncoder().default  # pyright: ignore[]
    JSONEncoder.default = _default  # pyright: ignore[]
    freeze_support()
    api = API()
    window = webview.create_window(
        "Texa",
        "http://localhost:3000",
        js_api=api,
        width=850,
        height=700,
        min_size=(600, 500),
        easy_drag=False,
        frameless=True,
    )
    window.events.closing += api.on_closing
    api.bind_window(window)
    webview.start(debug=True)
    exit(0)
