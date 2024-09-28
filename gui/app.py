from gui.model import Model
from gui.view import View
from gui.viewmodel import ViewModel


def main() -> None:
    """
    The main function.
    """
    model: Model = Model()
    view_model: ViewModel = ViewModel(model)
    view: View = View(view_model)
    view.show()
    model.run()
