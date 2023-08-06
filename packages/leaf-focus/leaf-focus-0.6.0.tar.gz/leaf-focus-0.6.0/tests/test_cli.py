import logging
import shutil
from importlib_resources import as_file, files

from leaf_focus.cli import main


def test_cli_pdf_ocr_existing_files(capsys, caplog, tmp_path, resource_example1):
    output_dir = tmp_path / "output-dir"
    output_dir.mkdir(exist_ok=True, parents=True)

    re_ex1 = resource_example1
    package = re_ex1.package
    package_path = files(package)
    pdf_name = re_ex1.pdf_name
    pg = 22
    with as_file(package_path.joinpath(pdf_name)) as p:
        shutil.copyfile(p, output_dir / p.name)
    with as_file(package_path.joinpath(re_ex1.page_image(pg))) as p:
        shutil.copyfile(p, output_dir / p.name)
    with as_file(package_path.joinpath(re_ex1.info_name)) as p:
        shutil.copyfile(p, output_dir / p.name)

    example_text_file = package_path.joinpath(re_ex1.text_name(pg, pg, "dos"))
    current_text_file = package_path.joinpath(re_ex1.text_name(pg, pg))
    with as_file(example_text_file) as ex_p:
        shutil.copyfile(ex_p, output_dir / current_text_file.name)

    with as_file(package_path.joinpath(re_ex1.page_annotations(pg))) as p:
        shutil.copyfile(p, output_dir / p.name)
    with as_file(package_path.joinpath(re_ex1.page_predictions(pg))) as p:
        predictions_file = output_dir / p.name
        shutil.copyfile(p, predictions_file)

    exe_dir = tmp_path / "exe_dir"
    exe_dir.mkdir(parents=True, exist_ok=True)

    caplog.set_level(logging.DEBUG)

    result = main(
        [
            str(output_dir / pdf_name),
            str(output_dir),
            "--exe-dir",
            str(exe_dir),
            "--ocr",
            "--first",
            "22",
            "--last",
            "22",
            "--log-level",
            "debug",
        ]
    )

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""

    assert caplog.record_tuples[:-1] == [
        ("leaf_focus.app", 20, "Starting leaf-focus"),
        ("leaf_focus.app", 20, f"Using output directory '{output_dir}'."),
        ("leaf_focus.pdf.xpdf", 20, "Loading existing pdf info file."),
        (
            "leaf_focus.pdf.xpdf",
            20,
            "Loading extracted embedded text from existing file.",
        ),
        ("leaf_focus.pdf.xpdf", 20, "Saving each pdf page as an image."),
        ("leaf_focus.pdf.xpdf", 20, "Found existing pdf images."),
        (
            "leaf_focus.ocr.keras_ocr",
            10,
            f"Predictions and annotations files already exist for '{re_ex1.page_image_stem(pg)}'.",
        ),
        ("leaf_focus.ocr.model", 10, "Loading OCR output items."),
        (
            "leaf_focus.ocr.model",
            10,
            f"Loaded 304 OCR items from '{predictions_file}'.",
        ),
        ("leaf_focus.ocr.model", 10, "Arranging text into lines."),
    ]
    assert caplog.record_tuples[-1][0] == "leaf_focus.app"
    assert caplog.record_tuples[-1][1] == 20
    assert caplog.record_tuples[-1][2].startswith("Finished (duration 0:00:0")

    assert result == 0
