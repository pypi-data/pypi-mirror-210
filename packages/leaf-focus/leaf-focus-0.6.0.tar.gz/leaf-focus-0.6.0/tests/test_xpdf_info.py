import os
import pathlib
import platform
import subprocess
from datetime import datetime
from subprocess import CompletedProcess

import pytest
from importlib_resources import as_file, files

from helper import check_skip_xpdf_exe_dir, check_skip_xpdf_exe_dir_msg
from leaf_focus.pdf.model import XpdfInfoArgs
from leaf_focus.pdf.xpdf import XpdfProgram


@pytest.mark.skipif(check_skip_xpdf_exe_dir(), reason=check_skip_xpdf_exe_dir_msg)
def test_xpdf_info_with_exe(capsys, caplog, resource_example1, tmp_path):
    package = resource_example1.package
    package_path = files(package)

    pdf_file = resource_example1.pdf_name
    with as_file(package_path.joinpath(pdf_file)) as p:
        pdf_path = p

    output_path = tmp_path / "output-dir"
    output_path.mkdir(exist_ok=True, parents=True)

    exe_dir = pathlib.Path(os.getenv("TEST_XPDF_EXE_DIR"))
    prog = XpdfProgram(exe_dir)
    args = XpdfInfoArgs(include_page_bounding_boxes=True, include_metadata=True)
    result = prog.info(pdf_path, output_path, args)

    assert result.title == "BkNVR450_Win7.book"
    assert not result.subject
    assert not result.keywords
    assert result.author == "ccampa"
    assert result.creator == "FrameMaker 2019.0.4"
    assert result.producer == "Acrobat Distiller 20.0 (Windows)"
    assert result.creation_date == datetime(2020, 8, 13, 11, 9, 0)
    assert result.modification_date == datetime(2020, 8, 14, 14, 58, 43)
    assert result.tagged is False
    assert result.form == "none"
    assert result.pages == 42
    assert result.encrypted is False
    assert result.page_size == "612 x 792 pts (letter) (rotated 0 degrees)"
    assert result.media_box == "0.00     0.00   612.00   792.00"
    assert result.crop_box == "0.00     0.00   612.00   792.00"
    assert result.bleed_box == "0.00     0.00   612.00   792.00"
    assert result.trim_box == "0.00     0.00   612.00   792.00"
    assert result.art_box == "0.00     0.00   612.00   792.00"
    assert result.file_size_bytes == 275855
    assert result.optimized is True
    assert result.pdf_version == "1.5"

    assert result.metadata == resource_example1.metadata

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""

    assert caplog.record_tuples == []


def test_xpdf_info_without_exe(
    capsys, caplog, resource_example1, tmp_path, monkeypatch
):
    package = resource_example1.package
    package_path = files(package)

    pdf_file = resource_example1.pdf_name
    with as_file(package_path.joinpath(pdf_file)) as p:
        pdf_path = p

    output_path = tmp_path / "output-dir"
    output_path.mkdir(exist_ok=True, parents=True)

    exe_dir = tmp_path / "exe-dir"
    exe_dir.mkdir(exist_ok=True, parents=True)
    exe_xpdf_info_file = exe_dir / (
        "pdfinfo.exe" if platform.system() == "Windows" else "pdfinfo"
    )
    exe_xpdf_info_file.touch()

    def mock_subprocess_run(cmd, capture_output, check, timeout, text):
        cmd_args = [str(exe_xpdf_info_file), "-box", "-meta", str(pdf_path)]
        if cmd == cmd_args:
            return CompletedProcess(
                args=cmd_args,
                returncode=0,
                stdout='Title:          BkNVR450_Win7.book\nAuthor:         ccampa\nCreator:        FrameMaker 2019.0.4\nProducer:       Acrobat Distiller 20.0 (Windows)\nCreationDate:   Thu Aug 13 11:09:00 2020\nModDate:        Fri Aug 14 14:58:43 2020\nTagged:         no\nForm:           none\nPages:          42\nEncrypted:      no\nPage size:      612 x 792 pts (letter) (rotated 0 degrees)\nMediaBox:           0.00     0.00   612.00   792.00\nCropBox:            0.00     0.00   612.00   792.00\nBleedBox:           0.00     0.00   612.00   792.00\nTrimBox:            0.00     0.00   612.00   792.00\nArtBox:             0.00     0.00   612.00   792.00\nFile size:      275855 bytes\nOptimized:      yes\nPDF version:    1.5\nMetadata:\n<?xpacket begin="ï»¿" id="W5M0MpCehiHzreSzNTczkc9d"?>\n<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c017 91.164374, 2020/03/05-20:41:30        ">\n   <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n      <rdf:Description rdf:about=""\n            xmlns:xmp="http://ns.adobe.com/xap/1.0/"\n            xmlns:dc="http://purl.org/dc/elements/1.1/"\n            xmlns:pdf="http://ns.adobe.com/pdf/1.3/"\n            xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/">\n         <xmp:CreatorTool>FrameMaker 2019.0.4</xmp:CreatorTool>\n         <xmp:ModifyDate>2020-08-14T14:58:43-07:00</xmp:ModifyDate>\n         <xmp:CreateDate>2020-08-13T11:09Z</xmp:CreateDate>\n         <xmp:MetadataDate>2020-08-14T14:58:43-07:00</xmp:MetadataDate>\n         <dc:format>application/pdf</dc:format>\n         <dc:title>\n            <rdf:Alt>\n               <rdf:li xml:lang="x-default">BkNVR450_Win7.book</rdf:li>\n            </rdf:Alt>\n         </dc:title>\n         <dc:creator>\n            <rdf:Seq>\n               <rdf:li>ccampa</rdf:li>\n            </rdf:Seq>\n         </dc:creator>\n         <pdf:Producer>Acrobat Distiller 20.0 (Windows)</pdf:Producer>\n         <xmpMM:DocumentID>uuid:00610876-6f52-4cf5-80eb-06b821bd1586</xmpMM:DocumentID>\n         <xmpMM:InstanceID>uuid:155960e2-0900-46e3-8d6c-c02b0a9feb4e</xmpMM:InstanceID>\n      </rdf:Description>\n   </rdf:RDF>\n</x:xmpmeta>\n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                                                                                                    \n                           \n<?xpacket end="w"?>\n',
                stderr="",
            )
        else:
            raise ValueError(f"Unknown cmd '{cmd}'")

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

    prog = XpdfProgram(exe_dir)
    args = XpdfInfoArgs(include_page_bounding_boxes=True, include_metadata=True)
    result = prog.info(pdf_path, output_path, args)

    assert result.title == "BkNVR450_Win7.book"
    assert not result.subject
    assert not result.keywords
    assert result.author == "ccampa"
    assert result.creator == "FrameMaker 2019.0.4"
    assert result.producer == "Acrobat Distiller 20.0 (Windows)"
    assert result.creation_date == datetime(2020, 8, 13, 11, 9, 0)
    assert result.modification_date == datetime(2020, 8, 14, 14, 58, 43)
    assert result.tagged is False
    assert result.form == "none"
    assert result.pages == 42
    assert result.encrypted is False
    assert result.page_size == "612 x 792 pts (letter) (rotated 0 degrees)"
    assert result.media_box == "0.00     0.00   612.00   792.00"
    assert result.crop_box == "0.00     0.00   612.00   792.00"
    assert result.bleed_box == "0.00     0.00   612.00   792.00"
    assert result.trim_box == "0.00     0.00   612.00   792.00"
    assert result.art_box == "0.00     0.00   612.00   792.00"
    assert result.file_size_bytes == 275855
    assert result.optimized is True
    assert result.pdf_version == "1.5"

    assert result.metadata == resource_example1.metadata

    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert stderr == ""

    assert caplog.record_tuples == []
