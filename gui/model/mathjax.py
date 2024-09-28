from pathlib import Path
from shutil import unpack_archive

from PySide6.QtCore import QDir, QFile, QIODevice, QObject, QStandardPaths, QUrl


class MathjaxModel(QObject):
    def __init__(self, version: str, parent: QObject | None = None) -> None:
        # super init
        super().__init__(parent)

        # flags
        need_extarct: bool = False

        # mathjax dir
        app_data_dir: str = QStandardPaths.standardLocations(
            QStandardPaths.StandardLocation.AppDataLocation
        )[0]
        mathjax_dir: str = str(Path(app_data_dir).joinpath("mathjax"))
        qd: QDir = QDir()

        # check if mathjax exists
        if not qd.exists(app_data_dir):
            # flag
            need_extarct = True
            # mkdir
            qd.mkpath(app_data_dir)
            qd.mkpath(mathjax_dir)
        elif not qd.exists(mathjax_dir):
            # flag
            need_extarct = True
            # mkdir
            qd.mkpath(mathjax_dir)
        else:
            version_file: QFile = QFile(str(Path(mathjax_dir).joinpath("version.txt")))
            # if we have version file, validate it
            if version_file.exists() and version_file.open(
                QFile.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text
            ):
                if bytes(version_file.readAll().data()).decode().strip() != version:
                    qd = QDir(mathjax_dir)
                    qd.removeRecursively()
                    # flag
                    need_extarct = True
                version_file.close()
            # if we don't have version file, means we don't have mathjax installed
            else:
                # flag
                need_extarct = True

        # install mathjax
        if need_extarct:
            artifact: QFile = QFile(f":/mathjax/{version}")
            artifact_path: str = str(Path(app_data_dir).joinpath("artifact.zip"))
            artifact.copy(artifact_path)
            unpack_archive(artifact_path, mathjax_dir)
            artifact = QFile(artifact_path)
            artifact.remove()

        # base url
        self.__base_url: QUrl = QUrl.fromLocalFile(mathjax_dir + "/")

    @property
    def base_url(self) -> QUrl:
        return self.__base_url
