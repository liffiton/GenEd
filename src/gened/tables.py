# SPDX-FileCopyrightText: 2024 Mark Liffiton <liffiton@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-only

from dataclasses import dataclass, replace
from sqlite3 import Row
from typing import Any, Final, Literal, Never


def table_prep(data: list[Row], max_len: int=1000) -> list[dict[str, Any]]:
    """ Prepare tabular data to be sent to the simple-datatables as JSON.
    This both shortens overly-long strings (that the user doesn't care to see
    in the table and that will just waste bandwidth) and converts into a
    format that simple-datatables accepts.
    """
    if not data:
        return []

    def truncate(val: Any) -> Any:
        if isinstance(val, str) and len(val) > max_len:
            return f"{val[:max_len]} ..."
        else:
            return val
    headings = data[0].keys()
    return [{key: truncate(row[key]) for key in headings} for row in data]
    #return SimpleDatatablesObject(
        #headings=headings,
        #data=[[truncate(row[key]) for key in headings] for row in data]
    #)


@dataclass(frozen=True)
class Col:
    name: str
    kind: str | None = None
    hidden: bool = False
    align: Literal[None, 'left', 'right', 'center'] = None


@dataclass(frozen=True)
class NumCol(Col):
    align: Final = 'right'
    kind: Final = 'num'


@dataclass(frozen=True, kw_only=True)
class BoolCol(Col):
    url: str | None = None
    reload: bool | None = None
    align: Final = 'center'
    kind: Final = 'bool'


@dataclass(frozen=True)
class UserCol(Col):
    kind: Final = 'user'


@dataclass(frozen=True)
class TimeCol(Col):
    kind: Final = 'time'


@dataclass(frozen=True)
class DateCol(Col):
    kind: Final = 'date'


@dataclass(kw_only=True)
class DataTable:
    name: str
    columns: list[Col]
    link_col: int | None = None
    link_template: str | None = None
    extra_links: list[dict[str, str]] | None = None
    create_endpoint: str | None = None
    csv_link: str | None = None
    ajax_url: str | None = None
    data: list[Row] | None = None

    def hide(self, col_name: str) -> None:
        self.columns = [
            replace(col, hidden=True) if col.name == col_name else col
            for col in self.columns
        ]

    @property
    def num_hidden(self) -> int:
        return sum(1 for col in self.columns if col.hidden)

    @property
    def table_data(self) -> list[dict[str, Any]]:
        return table_prep(self.data or [])
