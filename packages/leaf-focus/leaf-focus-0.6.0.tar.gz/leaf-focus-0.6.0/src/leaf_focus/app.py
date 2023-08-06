"""Main application."""
import dataclasses
import datetime
import logging
import pathlib
import typing

from leaf_focus import utils
from leaf_focus.ocr import keras_ocr
from leaf_focus.ocr import model as ocr_model
from leaf_focus.pdf import model as pdf_model
from leaf_focus.pdf import xpdf
from leaf_focus.utils import ValidatePathMethod

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class AppArgs:
    """Arguments for running the application."""

    input_pdf: pathlib.Path
    """path to the pdf file"""

    output_dir: pathlib.Path
    """path to the output directory to save text files"""

    first_page: typing.Optional[int] = None
    """the first pdf page to process"""

    last_page: typing.Optional[int] = None
    """the last pdf page to process"""

    save_page_images: bool = False
    """save each page of the pdf to a separate image"""

    run_ocr: bool = False
    """run OCR over each page of the pdf"""

    log_level: typing.Optional[str] = None
    """the log level"""


class App:
    """The main application."""

    def __init__(self, exe_dir: pathlib.Path) -> None:
        """Create a new instance of the application.

        Args:
            exe_dir: The path to the directory containing the executable files.
        """
        if not exe_dir or not exe_dir.exists() or not exe_dir.is_dir():
            msg = f"The path '{exe_dir or ''}' is not a directory."
            raise NotADirectoryError(msg)
        self._exe_dir = exe_dir

    def run(self, app_args: AppArgs) -> bool:
        """Run the application.

        Args:
            app_args: The application arguments.

        Returns:
            bool: True if the text extraction succeeded, otherwise false.
        """
        timestamp_start = datetime.datetime.utcnow()
        logger.info("Starting leaf-focus")

        input_pdf = utils.validate_path(
            "input pdf",
            app_args.input_pdf,
            ValidatePathMethod.MUST_EXIST,
        )
        app_args.input_pdf = input_pdf

        output_dir = utils.validate_path(
            "output directory",
            app_args.output_dir,
            ValidatePathMethod.NO_OPINION,
        )
        app_args.output_dir = output_dir

        # create the output directory
        if not output_dir.is_dir():
            logger.warning("Creating output directory '%s'.", output_dir)
            output_dir.mkdir(exist_ok=True, parents=True)
        else:
            logger.info("Using output directory '%s'.", output_dir)

        # run the pdf text extraction
        xpdf_prog = xpdf.XpdfProgram(self._exe_dir)

        # pdf file info
        self.pdf_info(xpdf_prog, app_args)

        # pdf embedded text
        self.pdf_text(xpdf_prog, app_args)

        # pdf page image
        xpdf_image = None
        if app_args.save_page_images or app_args.run_ocr:
            xpdf_image = self.pdf_images(xpdf_prog, app_args)

        # pdf page image ocr
        if app_args.run_ocr and xpdf_image:
            list(self.pdf_ocr(xpdf_image, app_args))

        timestamp_finish = datetime.datetime.utcnow()
        program_duration = timestamp_finish - timestamp_start
        logger.info("Finished (duration %s)", program_duration)
        return True

    def pdf_info(
        self,
        prog: xpdf.XpdfProgram,
        app_args: AppArgs,
    ) -> pdf_model.XpdfInfoResult:
        """Get the pdf file information.

        Args:
            prog: The program to run.
            app_args: The application arguments.

        Returns:
            pdf_model.XpdfInfoResult: The result from the program.
        """
        xpdf_info_args = pdf_model.XpdfInfoArgs(
            include_metadata=True,
            first_page=app_args.first_page,
            last_page=app_args.last_page,
        )
        return prog.info(app_args.input_pdf, app_args.output_dir, xpdf_info_args)

    def pdf_text(
        self,
        prog: xpdf.XpdfProgram,
        app_args: AppArgs,
    ) -> pdf_model.XpdfTextResult:
        """Get the text embedded in the pdf.

        Args:
            prog: The program to run.
            app_args: The application arguments.

        Returns:
            pdf_model.XpdfTextResult: The result from the program.
        """
        xpdf_text_args = pdf_model.XpdfTextArgs(
            line_end_type=pdf_model.XpdfTextArgs.get_line_ending(),
            use_original_layout=True,
            first_page=app_args.first_page,
            last_page=app_args.last_page,
        )
        return prog.text(app_args.input_pdf, app_args.output_dir, xpdf_text_args)

    def pdf_images(
        self,
        prog: xpdf.XpdfProgram,
        app_args: AppArgs,
    ) -> pdf_model.XpdfImageResult:
        """Get each page in the pdf as a separate image.

        Args:
            prog: The program to run.
            app_args: The application arguments.

        Returns:
            pdf_model.XpdfImageResult: The result from the program.
        """
        xpdf_image_args = pdf_model.XpdfImageArgs(use_grayscale=True)
        xpdf_image = prog.image(
            app_args.input_pdf,
            app_args.output_dir,
            xpdf_image_args,
        )
        return xpdf_image

    def pdf_ocr(
        self,
        xpdf_image: pdf_model.XpdfImageResult,
        app_args: AppArgs,
    ) -> typing.Generator[ocr_model.KerasOcrResult, typing.Any, None]:
        """Recognise text on the pdf page images.

        Args:
            xpdf_image: The result from the pdf image program.
            app_args: The application arguments.

        Returns:
            typing.Generator[ocr_model.KerasOcrResult, typing.Any, None]: Yield text
                recognition results for each pdf page image.
        """
        keras_ocr_prog = keras_ocr.OpticalCharacterRecognition()
        for xpdf_image_file in xpdf_image.output_files:
            yield keras_ocr_prog.recognise_text(xpdf_image_file, app_args.output_dir)
