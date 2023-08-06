from pybi.core.components.component import Component
from .componentTag import ComponentTag
import re
import pybi as pbi

from typing import Optional, Union


class TextComponent(Component):
    def __init__(self, content: str) -> None:
        super().__init__(ComponentTag.Text)
        self.content = content


class UploadComponent(Component):
    def __init__(self) -> None:
        super().__init__(ComponentTag.Upload)


class SvgIconComponent(Component):
    replace_svg_size_pat = re.compile(r"(width|height)=.+?\s", re.I | re.DOTALL)

    def __init__(self, svg: str, size: str, color: str) -> None:
        super().__init__(ComponentTag.SvgIcon)

        svg = SvgIconComponent.replace_svg_size_pat.sub("", svg)
        self.svg = svg
        self.size = size
        self.color = color


class IconComponent(Component):
    def __init__(self, icon_id: str, size: str, color: str) -> None:
        super().__init__(ComponentTag.Icon)

        self.iconID = icon_id
        self.size = size
        self.color = color


class SpaceComponent(Component):
    def __init__(self, space: Optional[str] = None, auto_fill_row=False) -> None:
        super().__init__(ComponentTag.Space)
        self._space = space
        self._auto_fill_row = auto_fill_row

    # def __mul__(self, num: int) -> None:
    #     assert isinstance(num, int), "other must be int"

    #     if num < 1:
    #         raise ValueError("num must be greater than 0")

    #     if num == 1:
    #         return

    #     for _ in range(num):
    #         pbi.space(self.space)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        if not self._space is None:
            data["space"] = self._space

        if self._auto_fill_row:
            data["autoFillRow"] = self._auto_fill_row

        return data
