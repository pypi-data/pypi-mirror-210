"""OCR using keras-ocr."""
import logging
import os
import pathlib
import typing

import numpy as np

from leaf_focus import utils
from leaf_focus.ocr import model

logger = logging.getLogger(__name__)


class OpticalCharacterRecognition:
    """OCR implementation using keras-ocr."""

    def __init__(self) -> None:
        """Create a new OpticalCharacterRecognition."""
        self._pipeline = None

    def engine_create(self) -> None:
        """Create the OCR engine.

        Returns:
            None
        """
        if self._pipeline is not None:
            return

        logger.warning("Creating keras ocr processing engine.")

        log_level = logger.getEffectiveLevel()

        # set TF_CPP_MIN_LOG_LEVEL before importing tensorflow
        # this allows changing the logging printed by tensorflow
        tf_log_level_map = {
            logging.DEBUG: "0",
            logging.INFO: "1",
            logging.WARNING: "2",
            logging.ERROR: "3",
        }
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = tf_log_level_map.get(log_level, "1")

        import tensorflow as tf  # pylint: disable=import-outside-toplevel

        # also set the tf logger level

        tf.get_logger().setLevel(log_level)

        # check the CPU / GPU in use
        gpus = tf.config.list_physical_devices("GPU")
        logger.info("GPUs in use: '%s'.", gpus)

        try:
            import keras_ocr  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError as error:
            msg = "Cannot run ocr on this Python version."
            logger.error(msg)
            raise utils.LeafFocusError(msg) from error

        # TODO: allow specifying path to weights files for detector
        # detector_weights_path = ""
        # detector = keras_ocr.detection.Detector(weights=None)
        # detector.model = keras_ocr.detection.build_keras_model(
        #     weights_path=detector_weights_path, backbone_name="vgg"
        # )
        # detector.model.compile(loss="mse", optimizer="adam")
        detector = None

        # TODO: allow specifying path to weights files for recogniser
        # recognizer_weights_path = ""
        # recognizer = keras_ocr.recognition.Recognizer(
        #     alphabet=keras_ocr.recognition.DEFAULT_ALPHABET, weights=None
        # )
        # recognizer.model.load_weights(recognizer_weights_path)
        recognizer = None

        # see: https://github.com/faustomorales/keras-ocr
        # keras-ocr will automatically download pretrained
        # weights for the detector and recognizer.
        self._pipeline = keras_ocr.pipeline.Pipeline(
            detector=detector,
            recognizer=recognizer,
        )

    def engine_run(
        self,
        image_file: pathlib.Path,
    ) -> typing.Tuple[typing.List, typing.Any]:
        """Run the recognition engine.

        Args:
            image_file: The path to the image file.

        Returns:
            typing.Tuple[typing.List, typing.Any]: The list of images
                and list of recognition results.
        """
        try:
            import keras_ocr  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError as error:
            msg = "Cannot run ocr on this Python version."
            logger.error(msg)
            raise utils.LeafFocusError(msg) from error

        self.engine_create()

        if not self._pipeline:
            msg = "Keras OCR pipeline has not been initialised yet."
            logger.error(msg)
            raise utils.LeafFocusError(msg)

        images = [keras_ocr.tools.read(str(image_file))]
        return images, self._pipeline.recognize(images)

    def engine_annotate(
        self,
        image: typing.Optional[np.ndarray],
        predictions: typing.List[typing.Tuple[typing.Any, typing.Any]],
        axis,
    ) -> None:
        """Run the annotation engine.

        Args:
            image: The image data.
            predictions: The recognised text from the image.
            axis: The plot axis for drawing annotations.

        Returns:
            None
        """
        try:
            import keras_ocr  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError as error:
            msg = "Cannot run ocr on this Python version."
            logger.error(msg)
            raise utils.LeafFocusError(msg) from error

        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=axis)

    def recognise_text(
        self,
        image_file: pathlib.Path,
        output_dir: pathlib.Path,
    ) -> model.KerasOcrResult:
        """Recognise text in an image file.

        Args:
            image_file: The path to the image file.
            output_dir: The directory to write the results.

        Returns:
            model.KerasOcrResult: The text recognition results.
        """
        if not image_file:
            msg = "Must supply image file."
            raise utils.LeafFocusError(msg)
        if not output_dir:
            msg = "Must supply output directory."
            raise utils.LeafFocusError(msg)
        if not image_file.exists():
            msg = f"Image file does not exist '{image_file}'."
            raise utils.LeafFocusError(msg) from FileNotFoundError(image_file)

        # check if output files already exist
        annotations_file = utils.output_root(image_file, "annotations", output_dir)
        annotations_file = annotations_file.with_suffix(".png")

        predictions_file = utils.output_root(image_file, "predictions", output_dir)
        predictions_file = predictions_file.with_suffix(".csv")

        result = model.KerasOcrResult(
            output_dir=output_dir,
            annotations_file=annotations_file,
            predictions_file=predictions_file,
            items=[],
        )

        if annotations_file.exists() and predictions_file.exists():
            logger.debug(
                "Predictions and annotations files already exist for '%s'.",
                image_file.stem,
            )
            all_items = list(model.TextItem.load(predictions_file))
            result.items = model.TextItem.order_text_lines(all_items)
            return result

        # read in the image
        logger.debug(
            "Creating predictions and annotations files for '%s'.",
            image_file.stem,
        )

        # Each list of predictions in prediction_groups is a list of
        # (word, box) tuples.
        images, prediction_groups = self.engine_run(image_file)

        # Plot and save the predictions
        for image, predictions in zip(images, prediction_groups):
            self.save_figure(annotations_file, image, predictions)

            items = self.convert_predictions(predictions)
            self.save_items(predictions_file, [item for line in items for item in line])
            result.items = items

        return result

    def save_figure(
        self,
        annotation_file: pathlib.Path,
        image: typing.Optional[np.ndarray],
        predictions: typing.List[typing.Tuple[typing.Any, typing.Any]],
    ) -> None:
        """Save the annotated image.

        Args:
            annotation_file: The path to the file containing annotations.
            image: The image data.
            predictions: The text recognition results.

        Returns:
            None
        """
        if not annotation_file:
            msg = "Must supply annotation file."
            raise utils.LeafFocusError(msg)

        expected_image_shape = 3
        if image is None or image.size < 1 or len(image.shape) != expected_image_shape:
            msg_image = image.shape if image is not None else None
            msg = f"Must supply valid image data, not '{msg_image}'."
            raise utils.LeafFocusError(msg)
        if not predictions:
            predictions = []

        logger.info("Saving OCR image to '%s'.", annotation_file)

        import matplotlib as mpl  # pylint: disable=import-outside-toplevel
        from matplotlib import pyplot as plt  # pylint: disable=import-outside-toplevel

        mpl.use("agg")

        annotation_file.parent.mkdir(exist_ok=True, parents=True)

        fig, axis = plt.subplots(figsize=(20, 20))

        self.engine_annotate(image, predictions, axis)

        fig.savefig(str(annotation_file))
        plt.close(fig)

    def convert_predictions(
        self,
        predictions: typing.List[typing.Tuple[typing.Any, typing.Any]],
    ) -> typing.List[typing.List[model.TextItem]]:
        """Convert predictions to items.

        Args:
            predictions: The list of recognised text.

        Returns:
            typing.List[typing.List[model.TextItem]]: The equivalent text items.
        """
        if not predictions:
            predictions = []

        items = []
        for prediction in predictions:
            items.append(model.TextItem.from_prediction(prediction))

        # order_text_lines sets the line number and line order
        line_items = model.TextItem.order_text_lines(items)

        return line_items

    def save_items(
        self,
        items_file: pathlib.Path,
        items: typing.Iterable[model.TextItem],
    ) -> None:
        """Save items to csv file.

        Args:
            items_file: Write the text items to this file.
            items: The text items to save.

        Returns:
            None
        """
        if not items_file:
            msg = "Must supply predictions file."
            raise utils.LeafFocusError(msg)
        if not items:
            msg = "Must supply predictions data."
            raise utils.LeafFocusError(msg)

        logger.info("Saving OCR predictions to '%s'.", items_file)

        items_list = list(items)
        model.TextItem.save(items_file, items_list)

    def _build_name(self, prefix: str, middle: str, suffix: str):
        """Build the file name.

        Args:
            prefix: The text to add at the start.
            middle: The text to add in the middle.
            suffix: The text to add at the end.

        Returns:
            str: The built name.
        """
        prefix = prefix.strip("-")
        middle = middle.strip("-")
        suffix = suffix if suffix.startswith(".") else "." + suffix
        return f"{prefix}-{middle}" + suffix
