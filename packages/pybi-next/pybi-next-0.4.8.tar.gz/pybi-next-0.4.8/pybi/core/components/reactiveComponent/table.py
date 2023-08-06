from __future__ import annotations
from typing import TYPE_CHECKING, List, Union


from pybi.core.components import ComponentTag
from .base import SingleReactiveComponent


if TYPE_CHECKING:
    from pybi.core.sql import SqlInfo


class Table(SingleReactiveComponent):
    def __init__(
        self,
        sql: SqlInfo,
    ) -> None:
        super().__init__(ComponentTag.Table, sql)
        self.pageSize = 10
        self.tableHeight = "initial"
        self.tableWidth = "initial"

    def set_page_size(self, size: int):
        """
        设置表格每页行数
        size: >=5 ,默认10
        """
        self.pageSize = max(size, 5)
        return self

    def set_table_height(self, height="initial"):
        """
        表格高度
        height: 'initial'(默认值),'30em','30%','30vh'
        如果设置为initial,则表格会以展示一页所有数据的高度作为固定高度
        """
        self.tableHeight = height
        return self

    def set_table_width(self, width="initial"):
        """
        表格高度
        width: 'initial'(默认值),'30em','30%','30vh'
        """
        self.tableWidth = width
        return self
