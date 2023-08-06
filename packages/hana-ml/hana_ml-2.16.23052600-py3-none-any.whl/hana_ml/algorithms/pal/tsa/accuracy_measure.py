"""
This module contains Python wrapper for PAL accuracy measure algorithm.

The following function is available:

    * :func:`accuracy_measure`
"""

#pylint: disable=too-many-lines, line-too-long, relative-beyond-top-level
import logging
import uuid
try:
    import pyodbc
except ImportError as error:
    pass
from hdbcli import dbapi
from ..pal_base import (
    ParameterTable,
    arg,
    try_drop,
    ListOfStrings,
    require_pal_usable,
    call_pal_auto_with_hint
)
#pylint: disable=invalid-name
logger = logging.getLogger(__name__)

def accuracy_measure(data, evaluation_metric,
                     ignore_zero=None,
                     alpha1=None,
                     alpha2=None):
    """
    Measures are used to check the accuracy of the forecast made by PAL algorithms.

    Parameters
    ----------

    data : DataFrame

        Input data, should have two or three columns:

        - If ``data`` contains 2 columns, then the first column is actual data while the second one
          is forecasted data.
        - If ``data`` contains 3 columns, then the 1st column must be the ID column, 2nd column be
          the actual data, while the 3rd column be the forecasted data.

    evaluation_metric : str or a list of str
        Specifies the accuracy measure name(s), with valid options listed as follows:

        - 'mpe': mean percentage error(MPE)
        - 'mse': mean square error(MSE)
        - 'rmse': root mean square error(RMSE)
        - 'et': error total(ET)
        - 'mad': mean absolute deviation(MAD)
        - 'mase': out-of-sample mean absolute scaled error(MASE)
        - 'wmape': weighted mean absolute percentage error(WMAPE)
        - 'smape': symmetric mean absolute percentage error(SMAPE)
        - 'mape': mean absolute percentage error(MAPE)
        - 'spec': stock-keeping-oriented prediction error costs(SPEC)

        .. note::

          If ``evaluation_metric`` is specified as 'spec' or contains 'spec' as one of its element, then
          ``data`` must have 3 columns (i.e. contain an ID column).

    ignore_zero : bool, optional
        Specifies whether or not to ignore zero values in ``data`` when calculating
        MPE or MAPE.


        Valid only when 'mpe' or 'mape' is specified/included in ``evaluation_metric``.

        Defaults to False, i.e. use the zero values in ``data`` when calculating MPE or MAPE.

    alpha1 : float, optional
        Specifies unit opportunity cost parameter in SPEC measure,
        should be no less than 0.

        Valid only when 'spec' is specified/included in ``evaluation_metric``.

        Defaults to 0.5.

    alpha2 : float, optional
        Specifies the unit stock-keeping cost parameter in SPEC measure,
        should be no less than 0.

        Valid only when 'spec' is specified/included in ``evaluation_metric``.

        Defaults to 0.5.

    Returns
    -------
    DataFrame
        Result of the forecast accuracy measurement, structured as follows:

        - STAT_NAME: Name of accuracy measures.
        - STAT_VALUE: Value of accuracy measures.

    Examples
    --------
    Input data df:

    >>> df.collect()
        ACTUAL  FORECAST
    0   1130.0    1270.0
    1   2410.0    2340.0
    2   2210.0    2310.0
    3   2500.0    2340.0
    4   2432.0    2348.0
    5   1980.0    1890.0
    6   2045.0    2100.0
    7   2340.0    2231.0
    8   2460.0    2401.0
    9   2350.0    2310.0
    10  2345.0    2340.0
    11  2650.0    2560.0

    Perform accuracy measurement:

    >>> res = accuracy_measure(data=df,
                               evaluation_metric=['mse', 'rmse', 'mpe', 'et',
                                                  'mad', 'mase', 'wmape', 'smape',
                                                  'mape'])
    >>> res.collect()
      STAT_NAME   STAT_VALUE
    0        ET   412.000000
    1       MAD    83.500000
    2      MAPE     0.041063
    3      MASE     0.287931
    4       MPE     0.008390
    5       MSE  8614.000000
    6      RMSE    92.811637
    7     SMAPE     0.040876
    8     WMAPE     0.037316

    """
    conn = data.connection_context
    require_pal_usable(conn)
    metric_map = {'mpe': 'MPE', 'mse': 'MSE', 'rmse': 'RMSE',
                  'et': 'ET', 'mad': 'MAD', 'mase': 'MASE',
                  'wmape': 'WMAPE', 'smape': 'SMAPE', 'mape': 'MAPE',
                  'spec': 'SPEC'}
    if isinstance(evaluation_metric, str):
        evaluation_metric = [evaluation_metric]
    try:
        evaluation_metric = arg('evaluation_metric', evaluation_metric, ListOfStrings)
    except Exception as err:
        msg = ("`evaluation_metric` must be list of string or string.")
        logger.error(msg)
        raise TypeError(msg) from err
    if not all(m in metric_map for m in evaluation_metric):
        msg = ("Some input in `evaluation_metric` is invalid.")
        logger.error(msg)
        raise ValueError(msg)
    if 'spec' in evaluation_metric and len(data.columns) == 2:
        msg = 'If \'spec\' is specified in evaluation_metric, then ' +\
        'the input data must have 3 columns.'
        logger.error(msg)
        raise ValueError(msg)
    ignore_zero = arg('ignore_zero', ignore_zero, bool)
    alpha1 = arg('alpha1', alpha1, float)
    alpha2 = arg('alpha2', alpha2, float)
    unique_id = str(uuid.uuid1()).replace('-', '_').upper()
    result_tbl = "#ACCURACY_MEASURE_RESULT_{}".format(unique_id)
    param_rows = []
    param_rows.extend([('MEASURE_NAME', None, None, metric_map[m]) for m in evaluation_metric])
    param_rows.extend([('IGNORE_ZERO', ignore_zero, None, None),
                       ('ALPHA1', None, alpha1, None),
                       ('ALPHA2', None, alpha2, None)])
    try:
        call_pal_auto_with_hint(conn,
                                None,
                                'PAL_ACCURACY_MEASURES',
                                data,
                                ParameterTable().with_data(param_rows),
                                result_tbl)
        return conn.table(result_tbl)
    except dbapi.Error as db_err:
        logger.exception(str(db_err))
        try_drop(conn, result_tbl)
        raise
    except pyodbc.Error as db_err:
        logger.exception(str(db_err.args[1]))
        try_drop(conn, result_tbl)
        raise
