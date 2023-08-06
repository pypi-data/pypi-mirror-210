import os
import pathlib
import platform
import subprocess
from importlib_resources import files, as_file
from subprocess import CompletedProcess

import pytest

from helper import check_skip_xpdf_exe_dir, check_skip_xpdf_exe_dir_msg
from leaf_focus.pdf.model import XpdfTextArgs
from leaf_focus.pdf.xpdf import XpdfProgram


@pytest.mark.skipif(check_skip_xpdf_exe_dir(), reason=check_skip_xpdf_exe_dir_msg)
def test_xpdf_text_with_exe(capsys, caplog, resource_example1, tmp_path):
    package = resource_example1.package
    package_path = files(package)

    pdf = resource_example1.pdf_name
    with as_file(package_path.joinpath(pdf)) as p:
        pdf_path = p

    output_path = tmp_path / "output-dir"
    output_path.mkdir(exist_ok=True, parents=True)

    exe_dir = pathlib.Path(os.getenv("TEST_XPDF_EXE_DIR"))

    prog = XpdfProgram(exe_dir)
    args = XpdfTextArgs(
        line_end_type="dos",
        use_verbose=True,
        use_simple2_layout=True,
    )
    result = prog.text(pdf_path, output_path, args)

    assert result.output_path.read_text().startswith(
        "Release 450 Driver for Windows, Version"
    )

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""

    assert caplog.record_tuples == []


def test_xpdf_text_without_exe(
    capsys, caplog, resource_example1, tmp_path, monkeypatch
):
    package = resource_example1.package
    package_path = files(package)
    pg = 22
    pdf = resource_example1.pdf_name
    with as_file(package_path.joinpath(pdf)) as p:
        pdf_path = p

    output_path = tmp_path / "output-dir"
    output_path.mkdir(exist_ok=True, parents=True)

    exe_dir = tmp_path / "exe-dir"
    exe_dir.mkdir(exist_ok=True, parents=True)
    exe_xpdf_text_file = exe_dir / (
        "pdftotext.exe" if platform.system() == "Windows" else "pdftotext"
    )
    exe_xpdf_text_file.touch()
    output_file = (
        f"{resource_example1.prefix_norm}-output-f-22-l-22-verbose-simple2-eol-dos.txt"
    )

    def mock_subprocess_run(cmd, capture_output, check, timeout, text):
        cmd_args = [
            str(exe_xpdf_text_file),
            "-f",
            str(pg),
            "-l",
            str(pg),
            "-verbose",
            "-simple2",
            "-eol",
            "dos",
            str(pdf_path),
            str(output_path / output_file),
        ]
        if cmd == cmd_args:
            return CompletedProcess(
                args=cmd_args, returncode=0, stdout="[processing page 22]\n", stderr=""
            )
        raise ValueError(f"Unknown cmd '{cmd}'")

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

    prog = XpdfProgram(exe_dir)
    args = XpdfTextArgs(
        line_end_type="dos",
        use_verbose=True,
        use_simple2_layout=True,
        first_page=22,
        last_page=22,
    )
    result = prog.text(pdf_path, output_path, args)

    assert result.output_path.name == output_file

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""

    assert caplog.record_tuples == []
