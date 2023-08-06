from typing import Any, Generic, TypeVar, Type
from strawberry.types import Info
from edat_utils.utils import EdatUtils
from edat_utils.query_builder import EdatQueryBuilder
from edat_utils.query_runner import EdatQueriyRunner
from edat_utils.schema import EdatFilter, EdatPagination, EdatOrder, EdatPaginationWindow, EdatGrouped
from typing import List

T = TypeVar("T")


class GenericController(Generic[T]):

    def get(self, info:Info, filter: EdatFilter, pagination: EdatPagination = None, orders: List[EdatOrder] = None) -> EdatPaginationWindow[T]:             
        table = EdatUtils.get_table_name(info)
        grouped = True if isinstance(T, EdatGrouped) else False
        fields = EdatUtils.get_fields(info)
        user = EdatUtils.get_user(info)
        query = EdatQueryBuilder.build_query(table, filter, fields, pagination, orders, grouped)
        print(query)
        rows = EdatQueriyRunner.list(query, user)
        return EdatPaginationWindow(items=rows, total_items_count=len(rows))
    

    