from masoniteorm.models import Model
from masoniteorm.query import QueryBuilder
from schema import EdatFilter, EdatPagination, EdatOrder
import re
from strawberry.types import Info
from typing import List


class EdatQueryBuilder:

    def create_builder(self, model: Model, filter: EdatFilter, info: Info, pagination: EdatPagination = None, orders: List[EdatOrder] = None, grouped: bool = False):      
        builder = QueryBuilder(model=model).table(model.get_table_name())
        return self.build_query(builder, filter, info, pagination, orders, grouped)

    def build_query(self, builder: QueryBuilder, filter: EdatFilter, info: Info, pagination: EdatPagination, orders: List[EdatOrder], grouped: bool):
        selected_fields = {item.name for field in info.selected_fields
                           for selection in field.selections for item in selection.selections}
        for key in filter:
            value = filter[key]
            if isinstance(value, dict):
                key_dict = list(value.keys())[0]
                value_dict = value[key_dict]

                match key:
                    case 'eq':
                        builder.where(key_dict, value_dict)
                    case 'ne':
                        builder.where(key_dict, '!=', value_dict)
                    case 'like':
                        builder.where_like(key_dict, value_dict)
                    case 'isNull':
                        builder.where_null(key_dict)
                    case 'notNull':
                        builder.where_not_null(key_dict)
                    case 'in':
                        builder.where_in(key_dict, value_dict)
                    case 'notIn':
                        builder.where_not_in(key_dict, value_dict)
                    case 'lt':
                        builder.where(key_dict, '<', value_dict)
                    case 'lte':
                        builder.where(key_dict, '<=', value_dict)
                    case 'gt':
                        builder.where(key_dict, '>', value_dict)
                    case 'gte':
                        builder.where(key_dict, '>=', value_dict)
                    case _:
                        builder.where(key_dict, value_dict)
            else:
                builder.where(key, value)

        if grouped:
            builder.sum('contador')
            for field in selected_fields:
                underline_field = re.sub(
                    r'(?<!^)(?=[A-Z])', '_', field).lower()
                builder.select(underline_field)
                builder.group_by(underline_field)
        else:
            for field in selected_fields:
                underline_field = re.sub(
                    r'(?<!^)(?=[A-Z])', '_', field).lower()
                builder.select(underline_field)

        if pagination:
            if pagination.limit and pagination.limit != 0:
                builder.limit(pagination.limit)
            if pagination.limit and pagination.offset != 0:
                builder.offset(pagination.offset)

        if orders:
            for order in orders:
                builder.order_by(order.field, order.type.value)
        return builder
