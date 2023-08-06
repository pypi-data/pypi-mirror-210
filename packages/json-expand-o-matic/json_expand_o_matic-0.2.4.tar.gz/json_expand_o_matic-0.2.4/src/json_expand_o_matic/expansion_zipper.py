import io
import logging
import os
import zipfile
from enum import Enum
from typing import Optional, Tuple, Union


class OutputChoice(Enum):
    KeepZip = "KeepZip"
    UnZipped = "UnZipped"
    Zipped = "Zipped"


class ExpansionZipper:
    def __init__(
        self,
        *,
        logger: logging.Logger,
        output_path: Optional[str] = None,  # . Where the output will be written.
        zip_root: Optional[str] = None,  # .... Where all the files are within the zip.
        zip_file: Optional[str] = None,  # .... Name of the zip file to create in `output_path`.
        zip_output: Union[str, OutputChoice] = OutputChoice.UnZipped,  # Keep zipped, unzip or both.
    ):
        assert logger, "logger is required"
        self.logger = logger
        self.work: list = list()

        self.output_mode = OutputChoice(zip_output)

        if output_path:
            if zip_file and zip_root:
                ...
            elif not zip_file and not zip_root:
                zip_file = os.path.basename(output_path)
                zip_root = os.path.basename(output_path)
                output_path = os.path.dirname(output_path)
            elif zip_file:
                zip_root = os.path.basename(output_path)
                output_path = os.path.dirname(output_path)
            elif zip_root:
                zip_file = os.path.basename(output_path)

        else:
            output_path = "."

        self.output_path = output_path
        self.zip_file = __name__ if not zip_file or zip_file == "." else zip_file
        self.zip_root = zip_root or "."

        if not self.zip_file.endswith(".zip"):
            self.zip_file += ".zip"

    def setup(self) -> Tuple["ExpansionZipper", list]:
        return self, self.work

    def finalize(self):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="a", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
            for directory, filename, data, checksum_filename, checksum in self.work:
                assert data is not None
                zip_file.writestr(f"{directory}/{filename}", data)
                if checksum is not None:
                    zip_file.writestr(
                        f"{directory}/{checksum_filename}", checksum, compress_type=zipfile.ZIP_STORED, compresslevel=0
                    )

        os.makedirs(self.output_path, exist_ok=True)
        with open(f"{self.output_path}/{self.zip_file}", "wb") as f:
            f.write(zip_buffer.getvalue())

        if self.output_mode == OutputChoice.Zipped:
            return

        zip_file = zipfile.ZipFile(f"{self.output_path}/{self.zip_file}")
        zip_file.extractall(self.output_path)

        if self.output_mode == OutputChoice.KeepZip:
            return

        os.remove(f"{self.output_path}/{self.zip_file}")
