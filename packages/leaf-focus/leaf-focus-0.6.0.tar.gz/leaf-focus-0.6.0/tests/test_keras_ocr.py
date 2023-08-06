import pathlib
import sys
import typing
from importlib_resources import as_file, files

import pytest
from hypothesis import given, strategies as st

from helper import check_skip_slow, check_skip_slow_msg, keras_max_version_minor
from leaf_focus import utils
from leaf_focus.ocr.keras_ocr import OpticalCharacterRecognition
from leaf_focus.ocr.model import TextItem


@pytest.mark.skipif(check_skip_slow(), reason=check_skip_slow_msg)
def test_keras_ocr_image_with_tensorflow(capsys, caplog, resource_example1, tmp_path):
    package = resource_example1.package
    package_path = files(package)
    pg = 22
    pdf_pg22_image = resource_example1.page_image(pg)
    with as_file(package_path.joinpath(pdf_pg22_image)) as p:
        image_file = p

    output_path = tmp_path / "output-dir"
    output_path.mkdir(exist_ok=True, parents=True)

    prog = OpticalCharacterRecognition()

    if sys.version_info.major == 3 and sys.version_info.minor > keras_max_version_minor:
        with pytest.raises(
            utils.LeafFocusError, match="Cannot run ocr on this Python version."
        ):
            prog.recognise_text(image_file, output_path)

    else:
        result = prog.recognise_text(image_file, output_path)
        expected_lines = 33
        expected_items = 300
        assert len(result.items) == expected_lines
        assert len([item for line in result.items for item in line]) == expected_items

        loaded_items = list(TextItem.load(result.predictions_file))
        loaded_items = TextItem.order_text_lines(loaded_items)

        assert len(loaded_items) == expected_lines
        assert len([item for line in loaded_items for item in line]) == expected_items

        stdout, stderr = capsys.readouterr()

        assert "craft_mlt_25k.h5" in stdout
        assert "crnn_kurapan.h5" in stdout

        assert stderr == ""

        assert caplog.record_tuples == [
            ("leaf_focus.ocr.keras_ocr", 30, "Creating keras ocr processing engine.")
        ]


def test_keras_ocr_image_without_tensorflow(
    capsys, caplog, resource_example1, tmp_path, monkeypatch
):
    package = resource_example1.package
    package_path = files(package)
    pg = 22
    pdf_pg22_image = resource_example1.page_image(22)
    with as_file(package_path.joinpath(pdf_pg22_image)) as p:
        image_file = p

    pdf_pg22_pred = resource_example1.page_predictions(pg)
    with as_file(package_path.joinpath(pdf_pg22_pred)) as p:
        pred_file = p

    pdf_pg22_anno = resource_example1.page_annotations(pg)
    with as_file(package_path.joinpath(pdf_pg22_anno)) as p:
        anno_file = p

    output_path = tmp_path / "output-dir"
    output_path.mkdir(exist_ok=True, parents=True)

    prog = OpticalCharacterRecognition()

    if sys.version_info.major == 3 and sys.version_info.minor > keras_max_version_minor:
        with pytest.raises(
            utils.LeafFocusError, match="Cannot run ocr on this Python version."
        ):
            prog.recognise_text(image_file, output_path)

    else:

        def mock_engine_create():
            pass

        monkeypatch.setattr(prog, "engine_create", mock_engine_create)

        def mock_engine_run(image_path: pathlib.Path):
            import cv2

            image = cv2.imread(str(image_path))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            prediction_groups = TextItem.load(pred_file)
            prediction_groups = [i.to_prediction for i in prediction_groups]
            return [image], [prediction_groups]

        monkeypatch.setattr(prog, "engine_run", mock_engine_run)

        def mock_engine_annotate(image, predictions, axis):
            pass

        monkeypatch.setattr(prog, "engine_annotate", mock_engine_annotate)

        result = prog.recognise_text(image_file, output_path)
        expected_lines = 33
        expected_items = 300
        assert len(result.items) == expected_lines
        assert len([item for line in result.items for item in line]) == expected_items

        loaded_items = list(TextItem.load(result.predictions_file))
        loaded_items = TextItem.order_text_lines(loaded_items)

        assert len(loaded_items) == expected_lines
        assert len([item for line in loaded_items for item in line]) == expected_items

        stdout, stderr = capsys.readouterr()

        assert stdout == ""
        assert stderr == ""

        output_annotated_png = output_path / anno_file.name
        assert output_annotated_png.exists()
        assert output_annotated_png.stat().st_size > 0

        assert caplog.record_tuples == []


@given(
    text=st.text(),
    top_left_x=st.floats(),
    top_left_y=st.floats(),
    top_right_x=st.floats(),
    top_right_y=st.floats(),
    bottom_right_x=st.floats(),
    bottom_right_y=st.floats(),
    bottom_left_x=st.floats(),
    bottom_left_y=st.floats(),
    line_number=st.one_of(st.none(), st.integers()),
    line_order=st.one_of(st.none(), st.integers()),
)
def test_fuzz_TextItem(
    text,
    top_left_x,
    top_left_y,
    top_right_x,
    top_right_y,
    bottom_right_x,
    bottom_right_y,
    bottom_left_x,
    bottom_left_y,
    line_number,
    line_order,
):
    TextItem(
        text=text,
        top_left_x=top_left_x,
        top_left_y=top_left_y,
        top_right_x=top_right_x,
        top_right_y=top_right_y,
        bottom_right_x=bottom_right_x,
        bottom_right_y=bottom_right_y,
        bottom_left_x=bottom_left_x,
        bottom_left_y=bottom_left_y,
        line_number=line_number,
        line_order=line_order,
    )


@given(
    prediction=st.from_type(
        typing.Tuple[
            str,
            typing.Tuple[
                typing.Tuple[float, float],
                typing.Tuple[float, float],
                typing.Tuple[float, float],
                typing.Tuple[float, float],
            ],
        ]
    )
)
def test_fuzz_TextItem_from_prediction(prediction):
    TextItem.from_prediction(prediction=prediction)


# TODO
# @given(path=st.builds(Path))
# def test_fuzz_TextItem_load(path):
#     list(TextItem.load(path=path))


@given(
    items=st.one_of(
        st.lists(
            st.builds(
                TextItem,
                text=st.text(),
                top_left_x=st.floats(),
                top_left_y=st.floats(),
                top_right_x=st.floats(),
                top_right_y=st.floats(),
                bottom_right_x=st.floats(),
                bottom_right_y=st.floats(),
                bottom_left_x=st.floats(),
                bottom_left_y=st.floats(),
                line_number=st.one_of(st.none(), st.one_of(st.none(), st.integers())),
                line_order=st.one_of(st.none(), st.one_of(st.none(), st.integers())),
            )
        )
    )
)
def test_fuzz_TextItem_order_text_lines(items):
    TextItem.order_text_lines(items=items)


# TODO
# @given(
#     path=st.builds(Path),
#     items=st.lists(
#         st.builds(
#             TextItem,
#             line_number=st.one_of(st.none(), st.one_of(st.none(), st.integers())),
#             line_order=st.one_of(st.none(), st.one_of(st.none(), st.integers())),
#         )
#     ),
# )
# def test_fuzz_TextItem_save(path, items):
#     TextItem.save(path=path, items=items)
