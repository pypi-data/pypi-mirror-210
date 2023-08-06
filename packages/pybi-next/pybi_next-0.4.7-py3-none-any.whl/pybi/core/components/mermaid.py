from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Union, Dict
from pybi.core.components.component import Component


from pybi.utils.data_gen import Jsonable, get_global_id
from .componentTag import ComponentTag


class Mermaid(Component):
    def __init__(self, graph: str) -> None:
        super().__init__(ComponentTag.Mermaid)
        self.graph = graph
