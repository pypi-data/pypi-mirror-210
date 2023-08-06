"""Models for OCR processing."""
from __future__ import annotations

import csv
import dataclasses
import logging
import math
import typing

if typing.TYPE_CHECKING:
    import pathlib
logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TextItem:
    """One found text item (could be a word or phrase) in an image."""

    text: str
    """The recognised text."""

    top_left_x: float
    top_left_y: float

    top_right_x: float
    top_right_y: float

    bottom_right_x: float
    bottom_right_y: float

    bottom_left_x: float
    bottom_left_y: float

    line_number: int | None = None
    line_order: int | None = None

    @property
    def top_left(self) -> tuple[float, float]:
        """Get the top left point.

        Returns:
            The x and y coordinates.
        """
        return self.top_left_x, self.top_left_y

    @property
    def top_right(self) -> tuple[float, float]:
        """Get the top right point.

        Returns:
            The x and y coordinates.
        """
        return self.top_right_x, self.top_right_y

    @property
    def bottom_right(self) -> tuple[float, float]:
        """Get the bottom right point.

        Returns:
             The x and y coordinates.
        """
        return self.bottom_right_x, self.bottom_right_y

    @property
    def bottom_left(self) -> tuple[float, float]:
        """Get the bottom left point.

        Returns:
            The x and y coordinates.
        """
        return self.bottom_left_x, self.bottom_left_y

    @property
    def top_length(self) -> float:
        """Get the length of the top side.

        Returns:
            float: The length.
        """
        # Get the length of the hypotenuse side.
        side1 = abs(self.top_right_x - self.top_left_x)
        side2 = abs(self.top_right_y - self.top_left_y)
        if side2 == 0:
            return side1
        return math.sqrt(pow(side1, 2) + pow(side2, 2))

    @property
    def left_length(self) -> float:
        """Get the length of the left side.

        Returns:
            float: The length.
        """
        # Get the length of the hypotenuse side.
        side1 = abs(self.top_left_y - self.bottom_left_y)
        side2 = abs(self.top_left_x - self.bottom_left_x)
        if side2 == 0:
            return side1
        return math.sqrt(pow(side1, 2) + pow(side2, 2))

    @property
    def line_bounds(self) -> tuple[float, float]:
        """Line bounds from top of text to bottom of text."""
        top_bound = min(
            [
                self.top_left_y,
                self.top_right_y,
                self.bottom_left_y,
                self.bottom_right_y,
            ],
        )
        bottom_bound = max(
            [
                self.top_left_y,
                self.top_right_y,
                self.bottom_left_y,
                self.bottom_right_y,
            ],
        )
        return top_bound, bottom_bound

    def is_same_line(self, other: TextItem) -> bool:
        """Check if the vertical midpoints of this item and another item overlap.

        Calculated as the midpoint +- 1/3 of the height of the text.

        Args:
            other (TextItem): The text item to compare.

        Returns:
            bool: True if this item and the other item overlap, otherwise false.
        """
        if not other:
            return False
        self_bounds = self.line_bounds
        self_top = self_bounds[0]
        self_bottom = self_bounds[1]
        self_third = (self_bottom - self_top) / 3
        self_top += self_third
        self_bottom -= self_third

        other_bounds = other.line_bounds
        other_top = other_bounds[0]
        other_bottom = other_bounds[1]
        other_third = (other_bottom - other_top) / 3
        other_top += other_third
        other_bottom -= other_third

        return self_top <= other_bottom and other_top <= self_bottom

    @property
    def slope_top_left_right(self) -> float:
        """Get the top slope from the left to the right.

        Returns:
            float: The slope.
        """
        return self._slope(
            self.top_left_x,
            self.top_left_y,
            self.top_right_x,
            self.top_right_y,
        )

    @property
    def slope_top_right_left(self) -> float:
        """Get the top slope from the right to the left.

        Returns:
            float: The slope.
        """
        return self._slope(
            self.top_right_x,
            self.top_right_y,
            self.top_left_x,
            self.top_left_y,
        )

    @property
    def slope_left_top_bottom(self) -> float:
        """Get the left slope from the top to the bottom.

        Returns:
            float: The slope.
        """
        return self._slope(
            self.top_left_x,
            self.top_left_y,
            self.bottom_left_x,
            self.bottom_left_y,
        )

    @property
    def slope_left_bottom_top(self) -> float:
        """Get the left slope from the bottom to the top.

        Returns:
            float: The slope.
        """
        return self._slope(
            self.bottom_left_x,
            self.bottom_left_y,
            self.top_left_x,
            self.top_left_y,
        )

    @property
    def slope_bottom_left_right(self) -> float:
        """Get the bottom slope from the left to the right.

        Returns:
            float: The slope.
        """
        return self._slope(
            self.bottom_left_x,
            self.bottom_left_y,
            self.bottom_right_x,
            self.bottom_right_y,
        )

    @property
    def slope_bottom_right_left(self) -> float:
        """Get the bottom slope from the right to the left.

        Returns:
            float: The slope.
        """
        return self._slope(
            self.bottom_right_x,
            self.bottom_right_y,
            self.bottom_left_x,
            self.bottom_left_y,
        )

    @property
    def slope_right_top_bottom(self) -> float:
        """Get the right slope from the top to the bottom.

        Returns:
            float: The slope.
        """
        return self._slope(
            self.top_right_x,
            self.top_right_y,
            self.bottom_right_x,
            self.bottom_right_y,
        )

    @property
    def slope_right_bottom_top(self) -> float:
        """Get the right slope from the bottom to the top.

        Returns:
            float: The slope.
        """
        return self._slope(
            self.bottom_right_x,
            self.bottom_right_y,
            self.top_right_x,
            self.top_right_y,
        )

    @property
    def is_horizontal_level(self) -> bool:
        """Check whether the left-to-right slope is approximately horizontal.

        Returns:
            bool: True if the item is approximately horizontal.
        """
        # -0.1 -> 0.1 is strictly horizontal
        # give a bit of buffer
        buffer = 0.09
        return -buffer <= self.slope_top_left_right <= buffer

    @property
    def is_vertical_level(self) -> bool:
        """Check whether the top-to-bottom slope is approximately vertical.

        Returns:
            bool: True if the item is approximately vertical.
        """
        # -0.1 -> 0.1 is strictly vertical
        # give a bit of buffer
        return self.slope_left_top_bottom == math.inf

    @classmethod
    def save(cls, path: pathlib.Path, items: list[TextItem]) -> None:
        """Save found text items to a file.

        Args:
            path: Write the items to this file.
            items: The items to save.

        Returns:
            None
        """
        logger.debug("Saving %s OCR output items.", len(items))

        fields = [
            "text",
            "line_number",
            "line_order",
            "top_left_x",
            "top_left_y",
            "top_right_x",
            "top_right_y",
            "bottom_right_x",
            "bottom_right_y",
            "bottom_left_x",
            "bottom_left_y",
        ]
        with open(path, "w", newline="", encoding="utf8") as file_path:
            writer = csv.DictWriter(file_path, fields)
            writer.writeheader()
            sorted_items = sorted(
                items,
                key=lambda i: (i.line_number or 0, i.line_order or 0),
            )
            writer.writerows([dataclasses.asdict(i) for i in sorted_items])

        logger.debug("Saved OCR items to '%s'.", path)

    @classmethod
    def load(cls, path: pathlib.Path) -> typing.Generator[TextItem, typing.Any, None]:
        """Load found text items from a file.

        Args:
            path: The path to the file containing items.

        Returns:
            typing.Generator["TextItem", typing.Any, None]: Items from the file.
        """
        logger.debug("Loading OCR output items.")
        count = 0

        with open(path, encoding="utf8") as file_path:
            reader = csv.DictReader(file_path)
            for row in reader:
                line_number = row.get("line_number", "").strip()
                line_number = int(line_number) if line_number else None

                line_order = row.get("line_order", "").strip()
                line_order = int(line_order) if line_order else None

                count += 1

                yield TextItem(
                    text=row["text"],
                    line_number=line_number,
                    line_order=line_order,
                    top_left_x=float(row["top_left_x"]),
                    top_left_y=float(row["top_left_y"]),
                    top_right_x=float(row["top_right_x"]),
                    top_right_y=float(row["top_right_y"]),
                    bottom_right_x=float(row["bottom_right_x"]),
                    bottom_right_y=float(row["bottom_right_y"]),
                    bottom_left_x=float(row["bottom_left_x"]),
                    bottom_left_y=float(row["bottom_left_y"]),
                )

        logger.debug("Loaded %s OCR items from '%s'.", count, path)

    @classmethod
    def from_prediction(
        cls,
        prediction: tuple[typing.Any, typing.Any],
    ) -> TextItem:
        """Convert from (text, box) to item.

        Box is (top left, top right, bottom right, bottom left).
        Its structure is [[startX,startY], [endX,startY], [endX,endY], [startX, endY]].

        Args:
            prediction: The text recognised in an image.

        Returns:
            TextItem: A text item representing the recognised text.
        """
        text, (
            (top_left_x, top_left_y),
            (top_right_x, top_right_y),
            (bottom_right_x, bottom_right_y),
            (bottom_left_x, bottom_left_y),
        ) = prediction
        return TextItem(
            text=text,
            top_left_x=top_left_x,
            top_left_y=top_left_y,
            top_right_x=top_right_x,
            top_right_y=top_right_y,
            bottom_right_x=bottom_right_x,
            bottom_right_y=bottom_right_y,
            bottom_left_x=bottom_left_x,
            bottom_left_y=bottom_left_y,
        )

    @classmethod
    def order_text_lines(
        cls,
        items: list[TextItem],
    ) -> list[list[TextItem]]:
        """Put items into lines of text (top -> bottom, left -> right)."""
        if not items:
            items = []

        logger.debug("Arranging text into lines.")

        lines = []
        current_line: list[TextItem] = []
        for item in items:
            if not item.is_horizontal_level:
                # exclude items that are too sloped
                continue

            if len(current_line) < 1:
                current_line.append(item)

            elif any(item.is_same_line(i) for i in current_line):
                current_line.append(item)

            elif len(current_line) > 0:
                # store current line
                current_line = sorted(current_line, key=lambda x: x.top_left)
                lines.append(current_line)

                # create new line
                current_line = [item]

        # include last items
        if len(current_line) > 0:
            lines.append(current_line)

        # update items to set line number and line order
        for line_index, line in enumerate(lines):
            for item_index, item in enumerate(line):
                item.line_number = line_index + 1
                item.line_order = item_index + 1

        return lines

    @property
    def to_prediction(
        self,
    ) -> tuple[
        str,
        tuple[
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
            tuple[float, float],
        ],
    ]:
        """Convert to prediction format."""
        return (
            self.text,
            (
                (self.top_left_x, self.top_left_y),
                (self.top_right_x, self.top_right_y),
                (self.bottom_right_x, self.bottom_right_y),
                (self.bottom_left_x, self.bottom_left_y),
            ),
        )

    def _slope(self, pt_x1, pt_y1, pt_x2, pt_y2) -> float:
        """Get the slope of a line."""
        y_diff = pt_y2 - pt_y1
        x_diff = pt_x2 - pt_x1
        try:
            return y_diff / x_diff
        except ZeroDivisionError:
            return math.inf if y_diff >= 0 else -math.inf

    def __str__(self) -> str:
        """Convert to a string."""
        line_info = f"({self.line_number or 0}:{self.line_order})"
        pos_info = f"[top left:{self.top_left}, top slope: {self.slope_top_left_right}]"
        return f"{self.text} {line_info} {pos_info}"


@dataclasses.dataclass
class KerasOcrResult:
    """Result from running keras-ocr."""

    output_dir: pathlib.Path
    annotations_file: pathlib.Path
    predictions_file: pathlib.Path
    items: list[list[TextItem]]
