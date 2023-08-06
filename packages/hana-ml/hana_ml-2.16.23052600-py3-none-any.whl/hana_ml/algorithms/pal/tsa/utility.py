"""
This module contains pal.tsa's utility functions.
"""
#pylint: disable=broad-except

import warnings
import logging
from hana_ml.algorithms.pal.pal_base import (
    arg,
    ListOfStrings
)

logger = logging.getLogger(__name__) #pylint: disable=invalid-name

def _col_index_check(col, para_name, index_value, cols_name):
    # col: the name of a column
    # para_name: key, group_key
    # index_value: single only one, massive has tow columns
    # cols_name: all column names
    if col is None:
        if not isinstance(index_value, str):
            col = cols_name[0]
            warn_msg = "The index of data is not a single column and '{0}' is None, so the first column of data is used as '{0}'!".format(para_name)
            warnings.warn(message=warn_msg)
        else:
            col = index_value
    else:
        if col != index_value:
            warn_msg = "Discrepancy between the designated {} column '{}' ".format(para_name, col) +\
            "and the designated index {} column which is '{}'.".format(para_name, index_value)
            warnings.warn(message=warn_msg)
    return col

def _categorical_variable_update(input_cate_var):
    if isinstance(input_cate_var, str):
        input_cate_var = [input_cate_var]
    input_cate_var = arg('categorical_variable', input_cate_var, ListOfStrings)
    return input_cate_var

def _convert_index_from_timestamp_to_int(data, key=None, keep_index=False):
    if key is None:
        if data.index is None:
            key = data.columns[0]
        else:
            key = data.index
    if not keep_index:
        return data.add_id(key + '(INT)', ref_col=key).deselect(key)
    else:
        return data.add_id(key + '(INT)', ref_col=key)

def _is_index_int(data, key=None):
    if key is None:
        if data.index is None:
            key = data.columns[0]
        else:
            key = data.index
    try:
        if not 'INT' in data.get_table_structure()[key].upper():
            return False
    except Exception as err:
        logger.warning(err)
        pass
    return True

def _get_forecast_starttime_and_timedelta(data, key=None, is_index_int=True):
    if key is None:
        if data.index is None:
            key = data.columns[0]
        else:
            key = data.index
    max_ = data.select(key).max()
    min_ = data.select(key).min()
    delta = (max_ - min_) / (data.count() - 1)
    if is_index_int:
        return max_ + delta, delta
    return max_ + delta, delta.total_seconds()

def _delete_none_key_in_dict(input_dict):
    for key in list(input_dict.keys()) :
        if input_dict[key] is None:
            del input_dict[key]
    return input_dict

def _validate_og(key, endog, exog, cols):
    if key is not None and key not in cols:
        msg = "Please select key from {}!".format(cols)
        logger.error(msg)
        raise ValueError(msg)
    cols.remove(key)
    if endog is not None:
        if endog not in cols:
            msg = "Please select endog from {}!".format(cols)
            logger.error(msg)
            raise ValueError(msg)
    else:
        endog = cols[0]
    cols.remove(endog)
    if exog is not None:
        if set(exog).issubset(set(cols)) is False:
            msg = "Please select exog from {}!".format(cols)
            logger.error(msg)
            raise ValueError(msg)
    else:
        exog = []
    return endog, exog
