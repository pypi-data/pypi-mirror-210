from typing import List, Tuple
import mysqlsb.exceptions as exc
from mysqlsb.statements import Sort


def exclude_cols(column_list: List[str], exclude_list: List[str]):
    """
    Takes a list of strings, and excludes all entries in the exlclude list.
    Returns a copy of the list, but without the excluded entries.
    Does not change the inserted list.
    :return:
    """
    column_list_copy = column_list[:]

    for exclude_col in exclude_list:
        if exclude_col in column_list:
            column_list_copy.remove(exclude_col)
        else:
            raise ValueError("Excluded column could not be found in column list.")

    return column_list_copy


def validate_order_request(target_value: str, allowed_columns: List[str], direction: str) -> Tuple[str, Sort]:
    """
    Convenience function to validate sql ordering requests
    Throws OrderValueException if validation fails.
    :param target_value: The column which you want to order by
    :param allowed_columns: The allowed columns
    :param direction: The direction of the ordering
    :return:
    """
    if target_value not in allowed_columns:
        raise exc.OrderValueException('Bad sorting value. Allowed columns: ' + ', '.join(allowed_columns))

    if direction == 'desc':
        order = Sort.DESCENDING
    elif direction == 'asc':
        order = Sort.ASCENDING
    else:
        raise exc.OrderValueException('Bad sorting direction. Allowed values: desc, asc')

    return target_value, order
