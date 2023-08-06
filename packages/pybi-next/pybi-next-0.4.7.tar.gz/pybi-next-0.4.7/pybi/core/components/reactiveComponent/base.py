from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Dict, Set, Any, Union

from pybi.utils.data_gen import Jsonable

from pybi.core.components import ComponentTag
from pybi.core.components.component import Component
from pybi.core.sql import SqlInfo

from pybi.core.dataSource import DataSourceView, DataSourceTable
import re


if TYPE_CHECKING:
    from pybi.core.dataSource import DataSourceTable


class UpdateInfo(Jsonable):
    def __init__(self, table: str, field: str) -> None:
        super().__init__()
        self.table = table
        self.field = field


class ReactiveComponent(Component):
    def __init__(self, tag: ComponentTag) -> None:
        super().__init__(tag)
        self._updateInfos: List[UpdateInfo] = []

    def add_updateInfo(self, table: str, field: str):
        self._updateInfos.append(UpdateInfo(table, field))
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["updateInfos"] = self._updateInfos

        return data


class SingleReactiveComponent(ReactiveComponent):
    def __init__(self, tag: ComponentTag, sql: SqlInfo) -> None:
        super().__init__(tag)
        self.sqlInfo = sql

    # def sql(self, sql: str):
    #     self._sql = sql
    #     return self
