from pydantic import ValidationError
from PySide6.QtCore import QDir, QFile, QStandardPaths, Qt, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from gui.annotations import Cfg, CfgFormulaNode, CfgMfdNode, CfgTextNode
from gui.utils import WarnMessageBox
from gui.viewmodel.infer import InferViewModel


class _MfrImporter(QWidget):
    back: Signal = Signal()

    def __init__(self, infer_view_model: InferViewModel) -> None:
        # super init
        super().__init__()

        # reference
        self.__infer_view_model = infer_view_model

        # widgets
        self.__importer_field = QGroupBox("MFR Model Importer")
        self.__importer_action = QGroupBox("Actions")
        self.__model_name_label: QLabel = QLabel("Model Name(*)")
        self.__model_name_lineedit: QLineEdit = QLineEdit()
        self.__model_backend_label: QLabel = QLabel("Model Backend(*)")
        self.__model_backend_lineedit: QLineEdit = QLineEdit()
        self.__model_dir_label: QLabel = QLabel("Model Directory to Copy(*)")
        self.__model_dir_lineedit: QLineEdit = QLineEdit()
        self.__model_dir_select_button: QPushButton = QPushButton("Select")
        self.__model_import_button: QPushButton = QPushButton("Import")
        self.__cancel_button: QPushButton = QPushButton("Cancel")

        # widgets setup
        self.__model_name_lineedit.setPlaceholderText("mfr-pro")
        self.__model_backend_lineedit.setPlaceholderText("onnx")
        self.__model_dir_lineedit.setPlaceholderText(
            "/Users/linus/.pix2text/1.1/mfr-pro-onnx"
        )
        self.__model_dir_select_button.setAutoDefault(False)
        self.__model_import_button.setAutoDefault(False)
        self.__cancel_button.setAutoDefault(False)

        # effects
        self.__model_dir_select_button.clicked.connect(self.__select_button_clicked)
        self.__model_import_button.clicked.connect(self.__import_button_clicked)
        self.__cancel_button.clicked.connect(self.back)

        # layout
        field_layout = QVBoxLayout()
        field_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        field_layout.addWidget(self.__model_name_label)
        field_layout.addWidget(self.__model_name_lineedit)
        field_layout.addWidget(self.__model_backend_label)
        field_layout.addWidget(self.__model_backend_lineedit)
        field_layout.addWidget(self.__model_dir_label)
        model_dir_layout = QHBoxLayout()
        model_dir_layout.addWidget(self.__model_dir_lineedit, 5)
        model_dir_layout.addWidget(self.__model_dir_select_button, 1)
        field_layout.addLayout(model_dir_layout)
        self.__importer_field.setLayout(field_layout)

        action_layout = QHBoxLayout()
        action_layout.addWidget(self.__model_import_button)
        action_layout.addWidget(self.__cancel_button)
        self.__importer_action.setLayout(action_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.__importer_field)
        layout.addWidget(self.__importer_action)
        self.setLayout(layout)

    def __validate(self, node: CfgFormulaNode) -> bool:
        # directory and files validation
        from_dir: QDir = QDir(node.model_dir)
        if not from_dir.exists():
            return False
        return set(
            [
                file.fileName()
                for file in from_dir.entryInfoList(
                    QDir.Filter.NoDotAndDotDot | QDir.Filter.Files
                )
            ]
        ) == set(
            [
                "config.json",
                "decoder_model.onnx",
                "encoder_model.onnx",
                "generation_config.json",
                "preprocessor_config.json",
                "tokenizer_config.json",
                "special_tokens_map.json",
                "tokenizer.json",
            ]
        )

    @Slot()
    def __select_button_clicked(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Model Directory",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.HomeLocation
            ),
        )
        if bool(path):
            self.__model_dir_lineedit.setText(path)

    @Slot()
    def __import_button_clicked(self) -> None:
        try:
            node = CfgFormulaNode(
                model_name=self.__model_name_lineedit.text(),
                model_backend=self.__model_backend_lineedit.text(),
                model_dir=self.__model_dir_lineedit.text(),
            )
            assert self.__validate(node) is True
        except (ValidationError, AssertionError):
            warn_box = WarnMessageBox("Invalid Input!")
            warn_box.exec()
            return
        self.__infer_view_model.p2t_config.set_formula(node)
        self.back.emit()


class _MfdImporter(QWidget):
    back: Signal = Signal()

    def __init__(self, infer_view_model: InferViewModel) -> None:
        # super init
        super().__init__()
        # widgets
        self.__importer_field = QGroupBox("MFD Model Importer")
        self.__importer_action = QGroupBox("Actions")
        self.__model_dir_label = QLabel("Model Path to Copy(*)")
        self.__model_dir_lineedit = QLineEdit()
        self.__model_dir_select_button = QPushButton("Select")
        self.__model_import_button = QPushButton("Import")
        self.__cancel_button = QPushButton("Cancel")

        # reference
        self.__infer_view_model = infer_view_model

        # widgets setup
        self.__model_dir_lineedit.setPlaceholderText(
            "/Users/linus/.pix2text/1.1/mfd-onnx/mfd-v20240618.onnx"
        )
        self.__model_dir_select_button.setAutoDefault(False)
        self.__model_import_button.setAutoDefault(False)
        self.__cancel_button.setAutoDefault(False)

        # effects
        self.__model_dir_select_button.clicked.connect(self.__select_button_clicked)
        self.__model_import_button.clicked.connect(self.__import_button_clicked)
        self.__cancel_button.clicked.connect(self.back)

        # layout
        field_layout = QVBoxLayout()
        field_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        field_layout.addWidget(self.__model_dir_label)
        model_dir_layout = QHBoxLayout()
        model_dir_layout.addWidget(self.__model_dir_lineedit, 5)
        model_dir_layout.addWidget(self.__model_dir_select_button, 1)
        field_layout.addLayout(model_dir_layout)
        self.__importer_field.setLayout(field_layout)
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.__model_import_button)
        action_layout.addWidget(self.__cancel_button)
        self.__importer_action.setLayout(action_layout)
        layout = QVBoxLayout()
        layout.addWidget(self.__importer_field)
        layout.addWidget(self.__importer_action)
        self.setLayout(layout)

    def __validate(self, node: CfgMfdNode) -> bool:
        file = QFile(node.model_path)
        return file.exists() and file.fileName().endswith(".onnx")

    @Slot()
    def __select_button_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Model File",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.HomeLocation
            ),
            "ONNX Model (*.onnx)",
        )
        if bool(path):
            self.__model_dir_lineedit.setText(path)

    @Slot()
    def __import_button_clicked(self) -> None:
        try:
            cfg_node = CfgMfdNode(model_path=self.__model_dir_lineedit.text())
            assert self.__validate(cfg_node) is True
        except (ValidationError, AssertionError):
            warn_box = WarnMessageBox("Invalid Input!")
            warn_box.exec()
            return
        self.__infer_view_model.p2t_config.set_mfd(cfg_node)
        self.back.emit()


class _TextImporter(QWidget):
    back: Signal = Signal()

    def __init__(self, infer_view_model: InferViewModel) -> None:
        # super init
        super().__init__()

        # reference
        self.__infer_view_model = infer_view_model

        # widgets
        self.__importer_field = QGroupBox("Text Model Importer")
        self.__importer_action = QGroupBox("Actions")
        self.__model_name_label: QLabel = QLabel("Model Name(*)")
        self.__model_name_lineedit: QLineEdit = QLineEdit()
        self.__model_backend_label: QLabel = QLabel("Model Backend(*)")
        self.__model_backend_lineedit: QLineEdit = QLineEdit()
        self.__model_dir_label: QLabel = QLabel("Model Path to Copy(*)")
        self.__model_dir_lineedit: QLineEdit = QLineEdit()
        self.__model_dir_select_button: QPushButton = QPushButton("Select")
        self.__model_import_button: QPushButton = QPushButton("Import")
        self.__cancel_button: QPushButton = QPushButton("Cancel")

        # widgets setup
        self.__model_name_lineedit.setPlaceholderText("doc-densenet_lite_666-gru_large")
        self.__model_backend_lineedit.setPlaceholderText("onnx")
        self.__model_dir_lineedit.setPlaceholderText(
            "/Users/linus/.pix2text/1.1/doc-densenet_lite_666-gru_large-onnx"
        )

        # effects
        self.__model_dir_select_button.clicked.connect(self.__select_button_clicked)
        self.__model_import_button.clicked.connect(self.__import_button_clicked)
        self.__cancel_button.clicked.connect(self.back)

        # layout
        field_layout = QVBoxLayout()
        field_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        field_layout.addWidget(self.__model_name_label)
        field_layout.addWidget(self.__model_name_lineedit)
        field_layout.addWidget(self.__model_backend_label)
        field_layout.addWidget(self.__model_backend_lineedit)
        field_layout.addWidget(self.__model_dir_label)
        model_dir_layout = QHBoxLayout()
        model_dir_layout.addWidget(self.__model_dir_lineedit, 5)
        model_dir_layout.addWidget(self.__model_dir_select_button, 1)
        field_layout.addLayout(model_dir_layout)
        self.__importer_field.setLayout(field_layout)
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.__model_import_button)
        action_layout.addWidget(self.__cancel_button)
        self.__importer_action.setLayout(action_layout)
        layout = QVBoxLayout()
        layout.addWidget(self.__importer_field)
        layout.addWidget(self.__importer_action)
        self.setLayout(layout)

    def __validate(self, node: CfgTextNode) -> bool:
        # directory and files validation
        file = QFile(node.rec_model_fp)
        return file.exists() and file.fileName().endswith(".onnx")

    def __select_button_clicked(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Model File",
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.HomeLocation
            ),
            "ONNX Model (*.onnx)",
        )
        if bool(path):
            self.__model_dir_lineedit.setText(path)

    def __import_button_clicked(self) -> None:
        try:
            node = CfgTextNode(
                rec_model_name=self.__model_name_lineedit.text(),
                rec_model_backend=self.__model_backend_lineedit.text(),
                rec_model_fp=self.__model_dir_lineedit.text(),
            )
            assert self.__validate(node) is True
        except (ValidationError, AssertionError):
            warn_box = WarnMessageBox("Invalid Input!")
            warn_box.exec()
            return
        self.__infer_view_model.p2t_config.set_text(node)
        self.back.emit()


class _ModelStatus(QGroupBox):
    def __init__(self, title: str) -> None:
        # super init
        super().__init__(title=title)

        # widgets
        self.model_label = QLabel("Model: ")
        self.model_info = QLabel("Default")
        self.import_button = QPushButton("Import")
        self.reset_button = QPushButton("Reset")

        # widget setup
        self.model_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.model_label.setStyleSheet("font-weight: bold;")
        self.model_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.import_button.setAutoDefault(False)
        self.reset_button.setAutoDefault(False)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.model_label)
        layout.addWidget(self.model_info)
        layout.addWidget(self.import_button)
        layout.addWidget(self.reset_button)
        self.setLayout(layout)


class ModelsDialog(QDialog):
    def __init__(self, infer_view_model: InferViewModel) -> None:
        # super init
        super().__init__()

        # reference
        self.__infer_view_model = infer_view_model

        # widgets
        self.__model_status_widget = QWidget()
        self.__mfd_group_box = _ModelStatus("MFD Model")
        self.__mfr_group_box = _ModelStatus("MFR Model")
        self.__text_group_box = _ModelStatus("Text Model")
        self.__mfr_importer = _MfrImporter(infer_view_model)
        self.__mfd_importer = _MfdImporter(infer_view_model)
        self.__text_importer = _TextImporter(infer_view_model)

        # widgets setup
        self.setWindowIcon(QIcon(":/images/icon"))
        self.setWindowTitle("Models")
        self.resize(400, 200)

        # setup
        self.__p2t_config_changed_handler(
            self.__infer_view_model.p2t_config.get_config()
        )

        # effects
        self.__infer_view_model.p2t_config.changed.connect(
            self.__p2t_config_changed_handler
        )
        self.__mfr_group_box.import_button.clicked.connect(self.__go_to_mfr_importer)
        self.__mfr_group_box.reset_button.clicked.connect(self.__mfr_reset_handler)
        self.__mfr_importer.back.connect(self.__return_to_status)
        self.__mfd_group_box.import_button.clicked.connect(self.__go_to_mfd_importer)
        self.__mfd_group_box.reset_button.clicked.connect(self.__mfd_reset_handler)
        self.__mfd_importer.back.connect(self.__return_to_status)
        self.__text_group_box.import_button.clicked.connect(self.__go_to_text_importer)
        self.__text_group_box.reset_button.clicked.connect(self.__text_reset_handler)
        self.__text_importer.back.connect(self.__return_to_status)

        # layout
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.__mfd_group_box)
        status_layout.addWidget(self.__mfr_group_box)
        status_layout.addWidget(self.__text_group_box)
        self.__model_status_widget.setLayout(status_layout)

        self.__stack = QStackedLayout()
        self.__stack.addWidget(self.__model_status_widget)
        self.setLayout(self.__stack)

    @Slot()
    def __return_to_status(self) -> None:
        # remove all other widgets
        for i in range(1, self.__stack.count()):
            self.__stack.removeWidget(self.__stack.widget(i))
        self.__stack.setCurrentWidget(self.__model_status_widget)
        # resize back
        self.resize(400, 200)

    @Slot(Cfg)
    def __p2t_config_changed_handler(self, cfg: Cfg) -> None:
        if cfg.formula is not None:
            self.__mfr_group_box.model_info.setText(cfg.formula.model_name)
        else:
            self.__mfr_group_box.model_info.setText("Default")
        if cfg.mfd is not None:
            self.__mfd_group_box.model_info.setText(cfg.mfd.model_path)
        else:
            self.__mfd_group_box.model_info.setText("Default")
        if cfg.text is not None:
            self.__text_group_box.model_info.setText(cfg.text.rec_model_name)
        else:
            self.__text_group_box.model_info.setText("Default")

    @Slot()
    def __go_to_mfr_importer(self) -> None:
        self.__stack.addWidget(self.__mfr_importer)
        self.__stack.setCurrentWidget(self.__mfr_importer)

    @Slot()
    def __mfr_reset_handler(self) -> None:
        self.__infer_view_model.p2t_config.reset_formula()

    @Slot()
    def __go_to_mfd_importer(self) -> None:
        self.__stack.addWidget(self.__mfd_importer)
        self.__stack.setCurrentWidget(self.__mfd_importer)

    @Slot()
    def __mfd_reset_handler(self) -> None:
        self.__infer_view_model.p2t_config.reset_mfd()

    @Slot()
    def __go_to_text_importer(self) -> None:
        self.__stack.addWidget(self.__text_importer)
        self.__stack.setCurrentWidget(self.__text_importer)

    @Slot()
    def __text_reset_handler(self) -> None:
        self.__infer_view_model.p2t_config.reset_text()
