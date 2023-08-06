"""PDF processing models."""

import dataclasses
import logging
import pathlib
import platform
import typing
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class XpdfArgs:
    """xpdf arguments common to all commands."""

    owner_password: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-opw", "cmd_type": "single"}},
        default=None,
    )
    """
    Specify the owner password for the PDF file.
    Providing this will bypass all security restrictions.

    -opw <string>          : owner password (for encrypted files)
    """

    user_password: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-upw", "cmd_type": "single"}},
        default=None,
    )
    """
    Specify the user password for the PDF file.

    -upw <string>          : user password (for encrypted files)
    """

    first_page: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-f", "cmd_type": "single"}},
        default=None,
    )
    """
    Specifies the first page to convert.

    -f <int>               : first page to convert
    """

    last_page: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-l", "cmd_type": "single"}},
        default=None,
    )
    """
    Specifies the last page to convert.

    -l <int>               : last page to convert
    """

    use_verbose: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-verbose", "cmd_type": "bool"}},
        default=False,
    )
    """
    Print a status message (to stdout) before processing each page.

    -verbose               : print per-page status information
    """

    config_file: typing.Optional[pathlib.Path] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-cfg", "cmd_type": "single"}},
        default=None,
    )
    """
    Read config-file in place of ~/.xpdfrc or the system-wide config file.

    -cfg <string>     : configuration file to use in place of .xpdfrc
    """

    program_info: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-v", "cmd_type": "bool"}},
        default=False,
    )
    """
    Print copyright and version information.

    -v                : print copyright and version info
    """


@dataclasses.dataclass
class XpdfInfoArgs(XpdfArgs):
    """Arguments for xpdf pdfinfo program."""

    include_page_bounding_boxes: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-box", "cmd_type": "bool"}},
        default=False,
    )
    """
    Prints the page box bounding boxes:
    MediaBox, CropBox, BleedBox, TrimBox, and ArtBox.

    -box              : print the page bounding boxes
    """

    include_metadata: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-meta", "cmd_type": "bool"}},
        default=False,
    )
    """
    Prints document-level metadata.
    This is the "Metadata" stream from the PDF file`s Catalog object.

    -meta             : print the document metadata (XML)
    """

    include_raw_dates: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-rawdates", "cmd_type": "bool"}},
        default=False,
    )
    """
    Prints the raw (undecoded) date strings, directly from the PDF file.

    -rawdates         : print the undecoded date strings directly from the PDF file
    """

    encoding: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-enc", "cmd_type": "single"}},
        default="Latin1",
    )
    """
    Sets the encoding to use for text output.
    The encoding-name must be defined with the unicodeMap command.
    This defaults to "Latin1" (which is a built-in encoding).

    -enc <string>          : output text encoding name
    """


@dataclasses.dataclass
class XpdfInfoResult:
    """Result from xpdf pdfinfo program."""

    # pdf info
    title: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Title"}},
    )
    subject: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Subject"}},
    )
    keywords: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Keywords"}},
    )
    author: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Author"}},
    )
    creator: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Creator"}},
    )
    producer: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Producer"}},
    )
    creation_date: typing.Optional[datetime] = dataclasses.field(
        metadata={"leaf_focus": {"name": "CreationDate"}},
    )
    modification_date: typing.Optional[datetime] = dataclasses.field(
        metadata={"leaf_focus": {"name": "ModDate"}},
    )

    # addtional info
    tagged: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Tagged"}},
    )
    form: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Form"}},
    )
    pages: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Pages"}},
    )
    encrypted: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Encrypted"}},
    )
    page_size: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Page size"}},
    )
    media_box: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "MediaBox"}},
    )
    crop_box: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "CropBox"}},
    )
    bleed_box: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "BleedBox"}},
    )
    trim_box: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "TrimBox"}},
    )
    art_box: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "ArtBox"}},
    )
    file_size_bytes: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"name": "File size"}},
    )
    optimized: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Optimized"}},
    )
    pdf_version: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"name": "PDF version"}},
    )

    # xml metadata
    metadata: typing.Optional[dict] = dataclasses.field(
        metadata={"leaf_focus": {"name": "Metadata"}},
    )


@dataclasses.dataclass
class XpdfTextArgs(XpdfArgs):
    """Arguments for xpdf pdftotext program."""

    use_original_layout: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-layout", "cmd_type": "bool"}},
        default=False,
    )
    """
    Maintain (as best as possible) the original physical layout of the text.

    -layout                : maintain original physical layout
    """

    use_simple_layout: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-simple", "cmd_type": "bool"}},
        default=False,
    )
    """
    optimized for simple one-column pages.
    This mode will do a better job of maintaining horizontal spacing,
    but it will only work properly with a single column of text.

    -simple                : simple one-column page layout
    """

    use_simple2_layout: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-simple2", "cmd_type": "bool"}},
        default=False,
    )
    """
    handles slightly rotated text (e.g., OCR output) better.
    Only works for pages with a single column of text.

    -simple2               : simple one-column page layout, version 2
    """

    use_table_layout: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-table", "cmd_type": "bool"}},
        default=False,
    )
    """
    Table mode is similar to physical layout mode, but optimized for tabular data,
    with the goal of keeping rows and columns aligned
    (at the expense of inserting extra whitespace).
    If the -fixed option is given, character spacing within
    each line will be determined by the specified character pitch.

    -table                 : similar to -layout, but optimized for tables
    """

    use_line_printer: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-lineprinter", "cmd_type": "bool"}},
        default=False,
    )
    """
    Line printer mode uses a strict fixed-character-pitch and -height layout.
    That is, the page is broken into a grid, and characters are placed into that grid.
    If the grid spacing is too small for the actual characters,
    the result is extra whitespace.
    If the grid spacing is too large, the result is missing whitespace.
    The grid spacing can be specified using the -fixed and -linespacing options.
    If one or both are not given on the command line,
    pdftotext will attempt to compute appropriate value(s).

    -lineprinter           : use strict fixed-pitch/height layout
    """

    use_raw_string_order: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-raw", "cmd_type": "bool"}},
        default=False,
    )
    """
    Keep the text in content stream order.
    Depending on how the PDF file was generated, this may or may not be useful.

    -raw                   : keep strings in content stream order
    """

    use_text_clip: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-clip", "cmd_type": "bool"}},
        default=False,
    )
    """
    Text which is hidden because of clipping is removed before doing layout,
    and then added back in. This can be helpful for tables where
    clipped (invisible) text would overlap the next column.

    -clip                  : separate clipped text
    """

    use_no_diag: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-nodiag", "cmd_type": "bool"}},
        default=False,
    )
    """
    Diagonal text, i.e., text that is not close to one of
    the 0, 90, 180, or 270 degree axes, is discarded.
    This is useful to skip watermarks drawn on top of body text, etc.

    -nodiag                : discard diagonal text
    """

    use_no_page_break: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-nopgbrk", "cmd_type": "bool"}},
        default=False,
    )
    """
    Don't insert a page break (form feed character) at the
    end of each page.

    -nopgbrk               : don't insert a page break at the end of each page
    """

    use_bom: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-nom", "cmd_type": "bool"}},
        default=False,
    )
    """
    Insert a Unicode byte order marker (BOM) at the start of the text output.

    -bom                   : insert a Unicode BOM at the start of the text file
    """

    use_verbose: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-verbose", "cmd_type": "bool"}},
        default=False,
    )
    """
    Print a status message (to stdout) before processing each page.

    -verbose               : print per-page status information
    """

    fixed_text_number: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-fixed", "cmd_type": "single"}},
        default=None,
    )
    """
    Specify the character pitch (character width), in points,
    for physical layout, table, or line printer mode.
    This is ignored in all other modes.

    -fixed <number>        : assume fixed-pitch (or tabular) text
    """

    line_space_number: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-linespacing", "cmd_type": "single"}},
        default=None,
    )
    """
    Specify the line spacing, in points, for line printer mode.
    This is ignored in all other modes.

    -linespacing <number>  : fixed line spacing for LinePrinter mode
    """

    line_end_type: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-eol", "cmd_type": "single"}},
        default=None,
    )
    """
    Sets the end-of-line convention to use for text output.

    -eol <string>          : output end-of-line convention (unix, dos, or mac)
    """

    margin_left_number: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-marginl", "cmd_type": "single"}},
        default=0,
    )
    """
    Specifies the left margin, in points.
    Text in the left margin
    (i.e., within that many points of the left edge of the page) is discarded.
    The default value is zero.

    -marginl <number>      : left page margin
    """

    margin_right_number: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-marginr", "cmd_type": "single"}},
        default=0,
    )
    """
    Specifies the right margin, in points.
    Text in the right margin (i.e., within that many points of the
    right edge of the page) is discarded.
    The default value is zero.

    -marginr <number>      : right page margin
    """

    margin_topnumber: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-margint", "cmd_type": "single"}},
        default=0,
    )
    """
    Specifies the top margin, in points.
    Text in the top margin (i.e., within that many points of the top
    edge of the page) is discarded.
    The default value is zero.

    -margint <number>      : top page margin
    """

    margin_bottom_number: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-marginb", "cmd_type": "single"}},
        default=0,
    )
    """
    Specifies the bottom margin, in points.
    Text in the bottom margin (i.e., within that many points of the
    bottom edge of the page) is discarded.
    The default value is zero.

    -marginb <number>      : bottom page margin
    """

    @classmethod
    def get_line_ending(cls) -> str:
        """Get the line endings based on the current platform.

        Returns:
            The line ending style.
        """
        opts = {
            "Linux": "unix",
            "Darwin": "mac",
            "Windows": "dos",
        }
        plat = platform.system()

        return opts[plat]


@dataclasses.dataclass
class XpdfTextResult:
    """Result for xpdf pdftotext program."""

    output_path: pathlib.Path
    stdout: typing.Collection[str] = dataclasses.field(default_factory=list)
    stderr: typing.Collection[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class XpdfImageArgs(XpdfArgs):
    """Arguments for xpdf pdftopng program."""

    resolution: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-r", "cmd_type": "single"}},
        default=150,
    )
    """
    Specifies the resolution, in DPI. The default is 150 DPI.

    -r <number>       : resolution, in DPI (default is 150)
    """
    use_monochrome: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-mono", "cmd_type": "bool"}},
        default=False,
    )
    """
    Generate a monochrome image (instead of a color image).

    -mono             : generate a monochrome PNG file
    """

    use_grayscale: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-gray", "cmd_type": "bool"}},
        default=False,
    )
    """
    Generate a grayscale image (instead of a color image).

    -gray             : generate a grayscale PNG file
    """
    use_alpha_channel: typing.Optional[bool] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-alpha", "cmd_type": "bool"}},
        default=False,
    )
    """
    Generate an alpha channel in the PNG file.
    This is only useful with PDF files that have been constructed
    with a transparent background.
    The -alpha flag cannot be used with -mono.

    -alpha            : include an alpha channel in the PNG file
    """

    rotation: typing.Optional[int] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-rot", "cmd_type": "single"}},
        default=None,
    )
    """
    Rotate pages by 0 (the default), 90, 180, or 270 degrees.

    -rot <int>        : set page rotation: 0, 90, 180, or 270
    """

    free_type: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-freetype", "cmd_type": "single"}},
        default="yes",
    )
    """
    Enable or disable FreeType (a TrueType / Type 1 font rasterizer).
    This defaults to "yes".

    -freetype <string>: enable FreeType font rasterizer: yes, no
    """
    anti_aliasing: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-aa", "cmd_type": "single"}},
        default="yes",
    )
    """
    Enable or disable font anti-aliasing.
    This defaults to "yes".

    -aa <string>      : enable font anti-aliasing: yes, no
    """
    vector_anti_aliasing: typing.Optional[str] = dataclasses.field(
        metadata={"leaf_focus": {"cmd": "-aaVector", "cmd_type": "single"}},
        default="yes",
    )
    """
    Enable or disable vector anti-aliasing.
    This defaults to "yes".

     -aaVector <string>: enable vector anti-aliasing: yes, no
    """


@dataclasses.dataclass
class XpdfImageResult:
    """Result for xpdf pdftopng program."""

    output_dir: pathlib.Path
    output_files: typing.Collection[pathlib.Path]
    stdout: typing.Collection[str] = dataclasses.field(default_factory=list)
    stderr: typing.Collection[str] = dataclasses.field(default_factory=list)
