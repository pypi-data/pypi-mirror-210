"""Small utility functions."""
from __future__ import annotations

import dataclasses
import datetime
import json
import platform
import re
import typing
import unicodedata
from enum import Enum

if typing.TYPE_CHECKING:
    import pathlib
    from xml.etree.ElementTree import Element

from importlib_metadata import PackageNotFoundError, distribution
from importlib_resources import as_file, files


def get_name_dash() -> str:
    """Get the package name with word separated by dashes."""
    return "leaf-focus"


def get_name_under() -> str:
    """Get the package name with word separated by underscores."""
    return "leaf_focus"


def get_version() -> str | None:
    """Get the package version."""
    try:
        dist = distribution(get_name_dash())
        return dist.version
    except PackageNotFoundError:
        pass

    try:
        with as_file(files(get_name_under()).joinpath("cli.py")) as file_path:
            return (file_path.parent.parent.parent / "VERSION").read_text().strip()
    except FileNotFoundError:
        pass

    return None


def parse_date(value: str) -> datetime.datetime | None:
    """Parse a date from a string."""
    formats = [
        # e.g. 'Thu Aug 13 11:09:00 2020'
        "%a %b %d %H:%M:%S %Y",
    ]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(value, fmt)
        except ValueError:
            pass
    return None


def validate(name: str, value, expected: list) -> None:
    """Validate that a value is one of the expected values."""
    if value is not None and value not in expected:
        opts = ", ".join(sorted([str(i) for i in expected]))
        msg = f"Invalid {name} '{value}'. Expected one of '{opts}'."
        raise LeafFocusError(msg)


class ValidatePathMethod(Enum):
    NO_OPINION = 0
    MUST_EXIST = 1


def validate_path(
    name: str,
    value: pathlib.Path,
    must_exist: ValidatePathMethod = ValidatePathMethod.NO_OPINION,
) -> pathlib.Path:
    """Validate a path."""
    if not value:
        msg = f"Must provide path {name}."
        raise LeafFocusError(msg)

    try:
        if must_exist == ValidatePathMethod.MUST_EXIST:
            abs_path = value.resolve(strict=True)
        else:
            abs_path = value.absolute()

        return abs_path
    except Exception as error:
        msg = f"Invalid path '{value}'."
        raise LeafFocusError(msg) from error


def select_exe(value: pathlib.Path) -> pathlib.Path:
    """Select the executable path based on the platform."""
    if platform.system() == "Windows":
        value = value.with_suffix(".exe")

    if not value.exists():
        msg = f"Exe file not found '{value}'."
        raise LeafFocusError(msg) from FileNotFoundError(value)

    return value


def output_root(
    input_file: pathlib.Path,
    output_type: str,
    output_path: pathlib.Path,
    additional: typing.Collection[str] | None = None,
) -> pathlib.Path:
    """Build the path to the output."""
    name_parts = [input_file.stem, output_type]
    name_parts.extend(additional or [])
    name_parts = [str(i) for i in name_parts if i is not None]
    name_parts = [str_norm(i.strip("-")) for i in name_parts if i and i.strip()]

    name = "-".join(name_parts)

    output = output_path / name

    return output


_slug_re_1 = re.compile(r"[^\w\s-]")
_slug_re_2 = re.compile(r"[-\s]+")


def str_norm(value: str) -> str:
    """Normalise a string into the 'slug' format."""
    separator = "-"
    encoding = "utf-8"

    norm = unicodedata.normalize("NFKD", value)
    enc = norm.encode(encoding, "ignore")
    de_enc = enc.decode(encoding)
    alpha_num_only = _slug_re_1.sub("", de_enc)
    alpha_num_tidy = alpha_num_only.strip().lower()
    result = _slug_re_2.sub(separator, alpha_num_tidy)
    return result


# 45206-win10-win8-win7-release-notes-page-image-gray-000022.png


class CustomJsonEncoder(json.JSONEncoder):
    """A custom json encoder."""

    def default(self, o: typing.Any) -> typing.Any:
        """Conversion used by default."""
        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()

        return super().default(o)


@dataclasses.dataclass
class XmlElement:
    """A simple xml element.

    <tag attrib>text<child/>...</tag>tail
    """

    attrib: typing.Collection[tuple[str, str, str]]
    tag: str
    name_space: str
    text: str
    tail: str
    children: typing.Collection[XmlElement]

    def to_dict(self) -> dict:
        """Convert xml element to a dict."""
        result: dict[str, typing.Any] = {"name": self.tag.strip()}

        value = ((self.text or "").strip() + " " + (self.tail or "").strip()).strip()
        if value:
            result["value"] = value

        attributes = {k.strip(): (v or "").strip() for n, k, v, in self.attrib}
        if attributes:
            result["attributes"] = attributes

        children = [i.to_dict() for i in self.children]
        if children:
            result["children"] = children

        return result

    def __str__(self) -> str:
        """Convert to a string."""
        tag1 = (self.tag or "").strip()
        tag2 = f"</{tag1}>"
        text = (self.text or "").strip()
        tail = (self.tail or "").strip()

        count = len(self.children)
        if count == 0:
            children = ""
        elif count == 1:
            children = "(1 child)"
        else:
            children = f"({count} children)"

        if text and children:
            children = " " + children

        if not text and not children:
            tag2 = ""

        count_attrib = len(self.attrib)
        if count_attrib == 0:
            attrib = ""
        elif count_attrib == 1:
            attrib = " (1 attribute)"
        else:
            attrib = f" ({count} attributes)"

        return f"<{tag1}{attrib}>{text}{children}{tag2}{tail}"


def xml_to_element(element: Element) -> XmlElement:
    """Convert xml into nested dicts."""
    attrib = element.attrib or {}
    tag = element.tag
    text = element.text
    tail = element.tail
    children = []

    for child in element:
        children.append(xml_to_element(child))

    tag_ns, tag_name = xml_tag_ns(tag)

    attrib_ns = []
    for key, value in attrib.items():
        extracted_ns, extracted_tag = xml_tag_ns(key)
        attrib_ns.append((extracted_ns, extracted_tag, value))

    item = XmlElement(
        attrib=attrib_ns,
        tag=tag_name,
        name_space=tag_ns,
        text=text or "",
        tail=tail or "",
        children=children,
    )

    return item


def xml_tag_ns(value: str) -> tuple[str, str]:
    """Get the XML namespace and name.

    Args:
        value: The combined namespace and name

    Returns:
        The separate namespace and name
    """
    if "}" in value:
        name_space, name = value.rsplit("}", maxsplit=1)
        name_space = name_space.strip("{}")
    else:
        name_space = ""
        name = value

    return name_space, name


class LeafFocusError(Exception):
    """A custom error for leaf focus."""
