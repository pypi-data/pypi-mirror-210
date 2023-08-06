"""
This module contains Python wrapper for PAL ROCKET algorithm.

The following class are available:

    * :class:`ROCKET`
"""
#pylint: disable=too-many-lines, line-too-long, too-many-locals, too-many-arguments, too-many-branches
#pylint: disable=c-extension-no-member, super-with-arguments, too-many-statements, invalid-name
#pylint: disable=duplicate-string-formatting-argument, too-many-instance-attributes, too-few-public-methods
#pylint: disable=too-many-arguments, too-many-branches, too-many-statements, attribute-defined-outside-init
import logging
import uuid
try:
    import pyodbc
except ImportError as error:
    pass
from hdbcli import dbapi
from hana_ml.ml_exceptions import FitIncompleteError
from hana_ml.algorithms.pal.utility import check_pal_function_exist
from hana_ml.algorithms.pal.tsa.utility import _col_index_check
from hana_ml.algorithms.pal.pal_base import (
    PALBase,
    ParameterTable,
    pal_param_register,
    try_drop,
    require_pal_usable
)
from hana_ml.algorithms.pal.sqlgen import trace_sql

logger = logging.getLogger(__name__)

class ROCKET(PALBase):
    r"""
    RandOm Convolutional KErnel Transform (ROCKET) is an exceptionally efficient algorithm for time series classification. Unlike other proposed time series classification algorithms which attain excellent accuracy, ROCKET maintains its performance with a fraction of the computational expense by transforming input time series using random convolutional kernels.

    Parameters
    ----------
    method : str, optional
        The options are "MiniRocket" and "MultiRocket".

        Defaults to "MiniRocket".

    num_features : int, optional
        Number of transformed features for each time series.

        Defaults to 9996 when ``method`` = "MiniRocket", 49728 when ``method`` = "MultiRocket".

    data_dim : int, optional
        Dimensionality of the multivariate time series.

        1 means univariate time series and others for multivariate. Cannot be smaller than 1.

        Defaults to 1.

    random_seed : int, optional
        0 indicates using machine time as seed.

        Defaults to 0.

    Attributes
    ----------
    model\_ : DataFrame

        Trained model content.

    Examples
    --------

    Example 1: Univariate time series fitted and transformed by MiniRocket
    Input dataframe is df:

    >>> df.collect()
        RECORD_ID  VAL_1  VAL_2  VAL_3  VAL_4  VAL_5  VAL_6  ...  VAL_10  VAL_11  VAL_12  VAL_13  VAL_14  VAL_15  VAL_16
    0           0  1.598  1.599  1.571  1.550  1.507  1.434  ...   1.117   1.024   0.926   0.828   0.739   0.643   0.556
    1           1  1.701  1.671  1.619  1.547  1.475  1.391  ...   1.070   0.985   0.899   0.816   0.733   0.658   0.581
    2           2  1.722  1.695  1.657  1.606  1.512  1.414  ...   1.015   0.920   0.828   0.740   0.658   0.586   0.501
    3           3  1.726  1.660  1.573  1.496  1.409  1.332  ...   0.987   0.901   0.815   0.730   0.644   0.558   0.484
    4           4  1.779  1.761  1.703  1.611  1.492  1.369  ...   0.900   0.786   0.679   0.580   0.502   0.415   0.333
    5           5  1.800  1.743  1.686  1.633  1.532  1.423  ...   0.979   0.872   0.767   0.664   0.561   0.453   0.355
    6           6  1.749  1.727  1.659  1.560  1.457  1.355  ...   0.961   0.864   0.771   0.682   0.595   0.513   0.427
    7           7  1.348  1.237  1.129  1.022  0.939  0.847  ...   0.474   0.388   0.306   0.218   0.133   0.061   0.009
    8           8  1.696  1.634  1.596  1.507  1.414  1.323  ...   1.048   0.966   0.890   0.805   0.719   0.632   0.553
    9           9  1.723  1.713  1.665  1.587  1.495  1.404  ...   1.041   0.955   0.870   0.787   0.706   0.622   0.547
    10         10  1.614  1.574  1.557  1.521  1.460  1.406  ...   1.045   0.957   0.862   0.771   0.681   0.587   0.497
    11         11  1.652  1.665  1.656  1.623  1.571  1.499  ...   1.155   1.058   0.973   0.877   0.797   0.704   0.609

    Create an instance of ROCKET:

    >>> ro = ROCKET(method="MiniRocket", random_seed=1)

    Performing fit() on the given dataframe:

    >>> ro.fit(data=df)

    Model:

    >>> ro.model_.collect()
        ID                                      MODEL_CONTENT
    0   -1                                         MiniRocket
    1    0  {"SERIES_LENGTH":16,"NUM_CHANNELS":1,"BIAS_SIZ...
    2    1  843045766098464,1.0396523357230486,2.005001093...
    3    2  67794124874738,1.3764943031483486,1.1499780774...
    4    3  44031,0.8485649487700363,-4.853621348269184,0....
    5    4  69780774072532,1.5195149626729508,-0.397262332...
    ......

    Make a transformation:

    >>> result = ro.transform(data=df)
    >>> result.collect()
          ID                                     STRING_CONTENT
    0      0  {"NUM_FEATURES_PER_DATA":9996,"FEATURES":[{"DA...
    1      1  ,0.375,0.875,0.125,0.5,1.0,0.25,0.75,1.0,0.375...
    2      2  .625,1.0,0.375,0.875,0.125,0.5,1.0,0.125,0.875...
    3      3  0.5625,0.0625,0.25,0.75,0.1875,0.3125,0.875,0....
    4      4  25,0.4375,0.6875,0.875,0.4375,0.8125,0.375,0.5...
    ......

    Example 2: Multivariate time series (with dimensionality 8) fitted and transformed by MultiRocket
    Input dataframe is df:

    >>> df.collect()
        RECORD_ID  VAL_1  VAL_2  VAL_3  VAL_4  VAL_5  VAL_6  ...  VAL_10  VAL_11  VAL_12  VAL_13  VAL_14  VAL_15  VAL_16
    0           0  1.645  1.646  1.621  1.585  1.540  1.470  ...   1.161   1.070   0.980   0.893   0.798   0.705   0.620
    1           1  1.704  1.705  1.706  1.680  1.632  1.560  ...   1.186   1.090   0.994   0.895   0.799   0.702   0.605
    2           2  1.699  1.666  1.621  1.538  1.454  1.357  ...   0.979   0.885   0.793   0.706   0.623   0.541   0.460
    3           3  1.709  1.663  1.580  1.497  1.413  1.330  ...   0.997   0.913   0.831   0.748   0.665   0.582   0.509
    4           4  1.687  1.688  1.674  1.619  1.531  1.439  ...   1.069   0.977   0.900   0.810   0.722   0.644   0.557
    ......
    27         27  1.697  1.665  1.590  1.508  1.424  1.341  ...   1.009   0.926   0.844   0.760   0.678   0.595   0.513
    28         28  1.406  1.320  1.234  1.148  1.063  0.978  ...   0.642   0.558   0.477   0.396   0.314   0.234   0.153
    29         29  1.592  1.593  1.571  1.551  1.527  1.475  ...   1.160   1.058   0.956   0.859   0.763   0.668   0.574
    30         30  1.688  1.648  1.570  1.490  1.408  1.327  ...   1.011   0.930   0.849   0.768   0.687   0.606   0.524
    31         31  1.708  1.663  1.595  1.504  1.411  1.318  ...   0.951   0.861   0.794   0.704   0.614   0.529   0.446

    Create an instance of ROCKET:

    >>> ro = ROCKET(method="multirocket", data_dim=8, random_seed=1)

    Performing fit() on the given dataframe:

    >>> ro.fit(data=df)

    Model:

    >>> ro.model_.collect()
        ID                                      MODEL_CONTENT
    0   -1                                        MultiRocket
    1    0  {"SERIES_LENGTH":16,"NUM_CHANNELS":8,"BIAS_SIZ...
    2    1  HANNELS":[6]},{"ID":77,"CHANNELS":[1,4,7,6,5]}...
    3    2  340878522815215,7.959895076819708,5.8147048859...
    ......

    Make a transformation:

    >>> result = ro.transform(data=df)
    >>> result.collect()
          ID                                     STRING_CONTENT
    0      0  {"NUM_FEATURES_PER_DATA":49728,"FEATURES":[{"D...
    1      1  .5625,0.8125,0.125,0.6875,0.9375,0.5,0.6875,0....
    2      2  5,0.5,0.8125,0.4375,0.5625,0.9375,0.5,0.75,0.1...
    3      3  0.0,1.0,0.0,1.0,1.0,0.0,1.0,1.0,0.75,1.0,0.0,1...
    4      4  25,0.0625,0.3125,0.375,0.1875,0.3125,0.9375,0....
    ......

    """

    def __init__(self,
                 method=None,
                 num_features=None,
                 data_dim=None,
                 random_seed=None):

        setattr(self, 'hanaml_parameters', pal_param_register())
        super(ROCKET, self).__init__()
        method_map = {"minirocket":0, "multirocket":1}
        self.method       = self._arg('method',       method,       method_map)
        self.num_features = self._arg('num_features', num_features, int)
        self.data_dim     = self._arg('data_dim',     data_dim,     int)
        self.random_seed  = self._arg('random_seed',  random_seed,  int)

        self.model_ = None

    @trace_sql
    def fit(self, data, key=None):
        r"""
        Generates a ROCKET model with given init parameters.

        Parameters
        ----------
        data : DataFrame
            Input data.
            For univariate time series, each row represents one time series, while for multivariate time series, a fixed number of consecutive rows forms one time series, and that number is designated by the parameter ``data_dim`` when initialize a ROCKET instance.

        key : str, optional
            The ID column.

            Defaults to the first column of data if the index column of data is not provided.
            Otherwise, defaults to the index column of data.

        """
        setattr(self, 'hanaml_fit_params', pal_param_register())

        index = data.index
        cols  = data.columns

        key = self._arg('key', key, str)
        index = data.index
        if index is not None:
            key = _col_index_check(key, 'key', index, cols)
        else:
            if key is None:
                key = cols[0]

        if key is not None and key not in cols:
            msg = f"Please select key from {cols}!"
            logger.error(msg)
            raise ValueError(msg)
        cols.remove(key)

        ts    = cols
        data_ = data[[key] + ts]

        conn = data.connection_context
        require_pal_usable(conn)

        unique_id = str(uuid.uuid1()).replace('-', '_').upper()
        model_tbl = f'#PAL_ROCKET_MODEL_TBL_{self.id}_{unique_id}'
        outputs = [model_tbl]
        param_rows = [
            ('METHOD',       self.method,       None, None),
            ('NUM_FEATURES', self.num_features, None, None),
            ('DATA_DIM',     self.data_dim,     None, None),
            ('RANDOM_SEED',  self.random_seed,  None, None)
            ]

        try:
            if check_pal_function_exist(conn, '%ROCKET%', like=True) or self._disable_hana_execution:
                self._call_pal_auto(conn,
                                    'PAL_ROCKET_FIT',
                                    data_,
                                    ParameterTable().with_data(param_rows),
                                    *outputs)
            else:
                msg = 'The version of your SAP HANA does not support ROCKET!'
                logger.error(msg)
                raise ValueError(msg)
        except dbapi.Error as db_err:
            msg = str(conn.hana_version())
            logger.exception("HANA version: %s. %s", msg, str(db_err))
            try_drop(conn, outputs)
            raise
        except pyodbc.Error as db_err:
            msg = str(conn.hana_version())
            logger.exception("HANA version: %s. %s", msg, str(db_err.args[1]))
            try_drop(conn, outputs)
            raise

        self.model_ = conn.table(model_tbl)
        return self

    @trace_sql
    def transform(self, data, key=None, thread_ratio=None):
        r"""
        Transform time series based on a given ROCKET model fitted by fit(). Hence, The data should be in the exact same format as that in fit(), especially the length and dimensionality of time series. The model\_ used in transform comes from fit() as well.

        Parameters
        ----------

        data : DataFrame
            Input data.
            For univariate time series, each row represents one time series, while for multivariate time series, a fixed number of consecutive rows forms one time series, and that number is designated by the parameter ``data_dim`` when initialize a ROCKET instance.

        key : str, optional
            The ID column.

            Defaults to the first column of data if the index column of data is not provided.
            Otherwise, defaults to the index column of data.

        thread_ratio : float, optional
            Controls the proportion of available threads to use.
            The ratio of available threads.

            - 0: single thread.
            - 0~1: percentage.
            - Others: heuristically determined.

            Defaults to 1.0.

        Returns
        -------

        DataFrame
            Features, structured as follows:

              - ID, type INTEGER, ROW_INDEX, indicates the ID of current row.
              - STRING_CONTENT, type NVARCHAR, transformed features in JSON format.

        """
        if getattr(self, 'model_', None) is None:
            msg = 'Model not initialized. Perform a fit first.'
            logger.error(msg)
            raise FitIncompleteError(msg)

        thread_ratio = self._arg('thread_ratio', thread_ratio, float)

        index = data.index
        cols = data.columns

        key = self._arg('key', key, str)
        index = data.index
        if index is not None:
            key = _col_index_check(key, 'key', index, cols)
        else:
            if key is None:
                key = cols[0]

        if key is not None and key not in cols:
            msg = f"Please select key from {cols}!"
            logger.error(msg)
            raise ValueError(msg)
        cols.remove(key)

        ts    = cols
        data_ = data[[key] + ts]

        conn = data.connection_context
        param_rows = [('THREAD_RATIO', None, thread_ratio, None)]

        unique_id = str(uuid.uuid1()).replace('-', '_').upper()
        result_tbl = f"#PAL_ROCKET_TRANSFORM_RESULT_TBL_{self.id}_{unique_id}"

        try:
            if check_pal_function_exist(conn, '%ROCKET%', like=True) or self._disable_hana_execution:
                self._call_pal_auto(conn,
                                    'PAL_ROCKET_TRANSFORM',
                                    data_,
                                    self.model_,
                                    ParameterTable().with_data(param_rows),
                                    result_tbl)
            else:
                msg = 'The version of your SAP HANA does not support ROCKET!'
                logger.error(msg)
                raise ValueError(msg)
        except dbapi.Error as db_err:
            logger.exception(str(db_err))
            try_drop(conn, result_tbl)
            raise
        except pyodbc.Error as db_err:
            logger.exception(str(db_err.args[1]))
            try_drop(conn, result_tbl)
            raise

        return conn.table(result_tbl)
