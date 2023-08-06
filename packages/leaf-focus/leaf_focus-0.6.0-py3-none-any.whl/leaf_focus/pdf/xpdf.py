"""Text extraction from pdf using xpdf tools."""
from __future__ import annotations

import dataclasses
import json
import logging
import pathlib
import subprocess
import typing
from datetime import datetime

from defusedxml import ElementTree

from leaf_focus import utils
from leaf_focus.pdf import model

logger = logging.getLogger(__name__)


class XpdfProgram:
    """Interact with xpdf tools."""

    OPTS_TEXT_ENCODING = [
        "Latin1",
        "ASCII7",
        "Symbol",
        "ZapfDingbats",
        "UTF-8",
        "UCS-2",
    ]
    OPTS_TEXT_LINE_ENDING = ["unix", "dos", "mac"]
    OPTS_IMAGE_ROTATION = [0, 90, 180, 270]
    OPTS_IMAGE_FREETYPE = ["yes", "no"]
    OPTS_IMAGE_ANTI_ALIAS = ["yes", "no"]
    OPTS_IMAGE_VEC_ANTI_ALIAS = ["yes", "no"]

    def __init__(self, directory: pathlib.Path) -> None:
        """Create a new xpdf program class to interact with xpdf tools.

        Args:
            directory: The path to the directory containing xpdf tools.
        """
        self._directory = directory

    def info(
        self,
        pdf_path: pathlib.Path,
        output_dir: pathlib.Path,
        xpdf_args: model.XpdfInfoArgs,
    ) -> model.XpdfInfoResult:
        """Get information from a pdf file.

        Args:
            pdf_path: The path to the pdf file.
            output_dir: The directory to save pdf info file.
            xpdf_args: The program arguments.

        Returns:
            The pdf file information.
        """
        # validation
        enc = xpdf_args.encoding
        utils.validate("text encoding", enc, self.OPTS_TEXT_ENCODING)

        if not pdf_path.exists():
            msg = f"Pdf file not found '{pdf_path}'."
            raise utils.LeafFocusError(msg) from FileNotFoundError(pdf_path)

        output_file = utils.output_root(pdf_path, "info", output_dir)
        output_file = output_file.with_suffix(".json")

        if output_file.exists():
            logger.info("Loading existing pdf info file.")
            with pathlib.Path.open(output_file, encoding="utf-8") as info_file:
                return model.XpdfInfoResult(**json.load(info_file))

        logger.info("Extracting pdf info and saving to file.")

        # build command
        exe_path = utils.select_exe(self._directory / "pdfinfo")
        cmd = [str(exe_path)]

        cmd_args = self.build_cmd(xpdf_args)

        cmd.extend(cmd_args)
        cmd.append(str(pdf_path.resolve()))

        # execute program
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            timeout=30,
            text=True,
        )
        lines = result.stdout.splitlines()

        fields_map = {
            field.metadata.get("leaf_focus", {}).get("name"): field
            for field in dataclasses.fields(model.XpdfInfoResult)
        }
        metadata_line_index: int | None = None

        data: dict[str, typing.Any] = {i.name: None for i in fields_map.values()}
        for index, line in enumerate(lines):
            if line.startswith("Metadata:"):
                metadata_line_index = index
                break

            value: typing.Any = None
            key, value = line.split(":", maxsplit=1)
            key = key.strip()

            field = fields_map.get(key)
            if not field:
                raise ValueError(f"Unknown pdf info key '{key}' in '{pdf_path}'.")

            data_key = field.name
            if data.get(data_key) is not None:
                raise ValueError(f"Duplicate pdf info key '{key}' in '{pdf_path}'.")

            if field.type == str or str in typing.get_args(field.type):
                value = value.strip()
            elif field.type == datetime or datetime in typing.get_args(field.type):
                value = utils.parse_date(value.strip())
            elif field.type == bool or bool in typing.get_args(field.type):
                value = value.strip().lower() == "yes"
            elif field.type == int or int in typing.get_args(field.type):
                if data_key == "file_size_bytes":
                    value = value.replace(" bytes", "")
                value = int(value.strip().lower())
            else:
                raise ValueError(f"Unknown key '{key}' type '{field.type}'")

            data[data_key] = value

        # metadata
        if metadata_line_index is not None:
            start = metadata_line_index + 1
            metadata = "\n".join(lines[start:])
            root = ElementTree.fromstring(metadata)
            data["metadata"] = utils.xml_to_element(root).to_dict()

        if output_dir and output_dir.exists():
            logger.debug("Saving pdf info to '%s'.", output_file)
            output_file.write_text(
                json.dumps(data, indent=2, cls=utils.CustomJsonEncoder),
            )

        return model.XpdfInfoResult(**data)

    def text(
        self,
        pdf_path: pathlib.Path,
        output_path: pathlib.Path,
        xpdf_args: model.XpdfTextArgs,
    ) -> model.XpdfTextResult:
        """Get the text from a pdf file.

        Args:
            pdf_path: The path to the pdf file.
            output_path: The directory to save output files.
            xpdf_args: The pdf program arguments.

        Returns:
            The result from running the text extraction program.
        """
        # validation
        eol = xpdf_args.line_end_type
        utils.validate("end of line", eol, self.OPTS_TEXT_LINE_ENDING)

        if not pdf_path.exists():
            msg = f"Pdf file not found '{pdf_path}'."
            raise utils.LeafFocusError(msg) from FileNotFoundError(str(pdf_path))

        # build command

        cmd_args = self.build_cmd(xpdf_args)

        output_file = utils.output_root(pdf_path, "output", output_path, cmd_args)
        output_file = output_file.with_suffix(".txt")

        # check if embedded text file already exists
        if output_file.exists():
            logger.info("Loading extracted embedded text from existing file.")
            return model.XpdfTextResult(
                stdout=[],
                stderr=[],
                output_path=output_file,
            )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Did not find expected output file '%s'", output_file.name)
            logger.debug("Listing items in '%s'", output_file.parent)
            item_count = 0
            for item in output_file.parent.iterdir():
                item_count += 1
                logger.debug("Found item '%s'", item)
            logger.debug("Found %s items in dir.", item_count)

        logger.info("Extracting pdf embedded text and saving to file.")

        exe_path = utils.select_exe(self._directory / "pdftotext")

        cmd = [str(exe_path)]

        cmd.extend([*cmd_args, str(pdf_path), str(output_file)])

        # execute program
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            timeout=30,
            text=True,
        )

        logger.debug("Saving pdf embedded text to '%s'.", output_file)

        return model.XpdfTextResult(
            stdout=(result.stdout or "").splitlines(),
            stderr=(result.stderr or "").splitlines(),
            output_path=output_file,
        )

    def image(
        self,
        pdf_path: pathlib.Path,
        output_path: pathlib.Path,
        xpdf_args: model.XpdfImageArgs,
    ) -> model.XpdfImageResult:
        """Create images of pdf pages.

        Args:
            pdf_path: The path to the pdf file.
            output_path: The directory to save output files.
            xpdf_args: The program arguments.

        Returns:
            The  pdf file image info.
        """
        # validation
        rot = xpdf_args.rotation
        utils.validate("rotation", rot, self.OPTS_IMAGE_ROTATION)

        free_type = xpdf_args.free_type
        utils.validate("freetype", free_type, self.OPTS_IMAGE_FREETYPE)

        anti_alias = xpdf_args.anti_aliasing
        utils.validate("anti-aliasing", anti_alias, self.OPTS_IMAGE_ANTI_ALIAS)

        anti_alias_vec = xpdf_args.anti_aliasing
        utils.validate(
            "vector anti-aliasing",
            anti_alias_vec,
            self.OPTS_IMAGE_VEC_ANTI_ALIAS,
        )

        if not pdf_path.exists():
            msg = f"Pdf file not found '{pdf_path}'."
            raise utils.LeafFocusError(msg) from FileNotFoundError(str(pdf_path))

        logger.info("Saving each pdf page as an image.")

        # build command
        cmd_args = self.build_cmd(xpdf_args)

        output_type = "page-image"

        # don't include the page limits when building the output prefix
        xpdf_args.first_page = None
        xpdf_args.last_page = None
        output_cmd_args = self.build_cmd(xpdf_args)
        output_dir = utils.output_root(
            pdf_path,
            output_type,
            output_path,
            output_cmd_args,
        )

        for pdf_image_file in output_dir.parent.iterdir():
            if not pdf_image_file.name.startswith(output_dir.name):
                continue

            logger.info("Found existing pdf images.")

            output_files = self.find_images(output_dir)
            return model.XpdfImageResult(
                stdout=[],
                stderr=[],
                output_dir=output_dir,
                output_files=output_files,
            )

        exe_path = utils.select_exe(self._directory / "pdftopng")
        cmd = [str(exe_path)]

        cmd.extend([*cmd_args, str(pdf_path), str(output_dir)])

        # execute program
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            timeout=30,
            text=True,
        )

        logger.debug("Created pdf page images using prefix '%s'.", output_dir)

        output_files = self.find_images(output_dir)

        return model.XpdfImageResult(
            stdout=(result.stdout or "").splitlines(),
            stderr=(result.stderr or "").splitlines(),
            output_dir=output_dir,
            output_files=output_files,
        )

    def build_cmd(self, tool_args):
        """Build the command arguments from a data class."""
        arg_class = tool_args.__class__
        cmd_args = []
        for field in dataclasses.fields(arg_class):
            name = field.name
            value = getattr(tool_args, name)

            field_default = field.default

            # TODO: account for default_factory

            # validate the arg config
            cmd_key = field.metadata.get("leaf_focus", {}).get("cmd")
            if not cmd_key:
                msg = f"Args incorrectly configured: missing 'cmd' for '{name}'."
                raise ValueError(msg)

            cmd_type = field.metadata.get("leaf_focus", {}).get("cmd_type")
            if not cmd_type:
                msg = f"Args incorrectly configured: missing 'cmd_type' for '{name}'."
                raise ValueError(msg)

            # add the arg
            if cmd_type == "bool":
                if value is not None and value is not True and value is not False:
                    msg = f"Argument '{name}' must be None, True, or False, not '{value}'."
                    raise ValueError(msg)

                if value is True:
                    cmd_args.extend([str(cmd_key)])

            elif cmd_type == "single":
                if field_default is None and value is not None:
                    cmd_args.extend([str(cmd_key), str(value)])
                elif field_default != value:
                    cmd_args.extend([str(cmd_key), str(value)])

            else:
                msg = (
                    f"Argument '{name}' has unknown cmd_type '{cmd_type}'. "
                    "Expected one of 'bool, single'."
                )
                raise ValueError(msg)

        return cmd_args

    def find_images(self, output_dir: pathlib.Path) -> list[pathlib.Path]:
        """Find image files in a directory."""
        stem_parts = 7
        stem_digit_parts = 6
        output_files = []
        for file_path in output_dir.parent.iterdir():
            if not file_path.is_file():
                continue
            if not file_path.name.startswith(output_dir.stem):
                continue
            if file_path.suffix != ".png":
                continue
            if len(file_path.stem) < stem_parts:
                continue
            if file_path.stem[-stem_parts] != "-":
                continue
            if not all(i.isdigit() for i in file_path.stem[-stem_digit_parts:]):
                continue
            output_files.append(file_path)

        if not output_files:
            logger.warning("No page images found.")

        return output_files
