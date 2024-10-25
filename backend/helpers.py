import re
from dataclasses import dataclass
from typing import Literal

PyFileTypes = Literal["encoder", "decoder", "tokenizer"]


@dataclass
class PyResponse:
    type: Literal["ok", "err"]
    data: str

    def to_dict(self) -> dict[str, str]:
        return {"type": self.type, "data": self.data}


def replace_katex_invalid(string: str) -> str:
    # KaTeX cannot render all LaTeX, so we need to replace some things
    string = re.sub(r"\\tag\{.*?\}", "", string)
    string = re.sub(r"\\(?:Bigg?|bigg?)\{(.*?)\}", r"\1", string)
    string = re.sub(r"\\quad\\mbox\{(.*?)\}", r"\1", string)
    string = re.sub(r"\\mbox\{(.*?)\}", r"\1", string)
    return string
