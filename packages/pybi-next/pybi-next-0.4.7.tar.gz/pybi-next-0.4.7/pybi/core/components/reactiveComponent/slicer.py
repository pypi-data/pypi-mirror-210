from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict


from pybi.core.components import ComponentTag
from .base import SingleReactiveComponent


if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo


class Slicer(SingleReactiveComponent):
    def __init__(self, sql: SqlInfo) -> None:
        super().__init__(ComponentTag.Slicer, sql)
        self.title = ""
        self.multiple = True

    def set_title(self, title: str):
        self.title = title
        return self

    def set_multiple(self, multiple: bool):
        self.multiple = multiple
        return self

    def set_props(self, props: Dict):
        """
        [slicer props](https://element-plus.gitee.io/zh-CN/component/select.html#select-attributes)
        e.g
        >>> .add_slicer(...).set_props({'placeholder':'my define placeholder'})
        """
        return super().set_props(props)
