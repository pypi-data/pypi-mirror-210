from edat_utils.schema import EdatFilter, EdatPagination, EdatOrder
import re
from typing import List
import numbers

AND = ' AND '
COMMA_SEPARARATOR = ', '

class EdatQueryBuilder:

    @staticmethod
    def build_query(table: str, filter: EdatFilter, fields: List[str], pagination: EdatPagination, orders: List[EdatOrder], grouped: bool):
        
        select = []
        where = []
        group = []
        pagination = ''
        orderBy = []

        for key in filter:
            value = filter[key]
            if isinstance(value, dict):
                key_dict = list(value.keys())[0]
                value_dict = EdatQueryBuilder.__get_value(value[key_dict])

                match key:
                    case 'eq':
                        where.append(key_dict + ' = ' + value_dict)
                    case 'ne':
                        where.append(key_dict + ' != ' + value_dict)
                    case 'like':
                        where.append(key_dict + ' LIKE "' + value_dict + '"')
                    case 'isNull':
                        where.append(key_dict + ' IS NULL ')
                    case 'notNull':
                        where.append(key_dict + ' IS NOT NULL ')
                    case 'in':
                        where.append(key_dict + ' IN ' + value_dict)
                    case 'notIn':
                        where.append(key_dict + ' NOT IN ' + value_dict)
                    case 'lt':
                        where.append(key_dict + ' < ' + value_dict)
                    case 'lte':
                        where.append(key_dict + ' <= ' + value_dict)
                    case 'gt':
                        where.append(key_dict + ' > ' + value_dict)
                    case 'gte':
                        where.append(key_dict + ' >= ' + value_dict)
                    case _:
                        where.append(key_dict + ' = ' + value_dict)
            else:
                where.append(key + ' = ' + str(value))

        if grouped:
            select.append("SUM(contador)")
            for field in fields:
                underline_field = re.sub(
                    r'(?<!^)(?=[A-Z])', '_', field).lower()
                select.append(underline_field)
                group.append(underline_field)
        else:
            for field in fields:
                underline_field = re.sub(
                    r'(?<!^)(?=[A-Z])', '_', field).lower()
                select.append(underline_field)

        if pagination:
            if pagination.limit and pagination.limit != 0:
                pagination = pagination + ' LIMIT ' + str(pagination.limit)
            if pagination.limit and pagination.offset != 0:
                pagination = pagination + ' OFFSET ' + str(pagination.offset)

        if orders:
            for order in orders:
                orderBy.append(order.field + ' ' + order.type.value)


        query = 'SELECT '
        query = query + COMMA_SEPARARATOR.join(select)
        query = query + ' FROM ' + table
        if where:
            query = query + ' WHERE '+ AND.join(where)
        if group:
            query = query + ' GROUP BY '+ COMMA_SEPARARATOR.join(group)
        if orderBy:
            query = query + ' ORDER BY ' + COMMA_SEPARARATOR.join(orderBy)
        query = query + pagination
       
        return query

    @staticmethod
    def __get_value(value):
        if isinstance(value, numbers.Number):
            return str(value)
        elif isinstance(value, str):
            return "'" + value + "'"
        elif isinstance(value, list) or isinstance(value, dict):
            if isinstance(value[0], str):
                return "('" + "', '".join(value) + "')"
            else:
                return "(" + ", ".join(map(str, value)) + ")"
        else: 
            return value
