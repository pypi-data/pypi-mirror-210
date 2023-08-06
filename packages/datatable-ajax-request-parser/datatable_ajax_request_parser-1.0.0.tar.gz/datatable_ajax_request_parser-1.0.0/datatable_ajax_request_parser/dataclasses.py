from dataclasses import asdict, dataclass
from typing import List


@dataclass
class DictHelperMixin:
    def to_dict(self):
        return asdict(self)


@dataclass
class DTOrder(DictHelperMixin):
    index: int
    column: int
    direction: str  # asc/desc

    def __str__(self):
        return f'index: {self.index} column: {self.column}, direction: {self.direction}'


@dataclass
class DTColumn(DictHelperMixin):
    data: str
    name: str
    searchable: bool
    orderable: bool
    search_value: str
    search_is_regex: bool

    def __str__(self):
        return f'data: {self.data}, name: {self.name}'


@dataclass
class DTRequest(DictHelperMixin):
    draw: int
    start: int
    length: int
    search_value: str
    search_regex: bool
    columns: List[DTColumn]
    order: List[DTOrder]
