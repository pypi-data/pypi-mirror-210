from inspect import stack

from numpy import int64
from pandas import DataFrame, Series, Index
from logging import Logger, getLogger


class DataCheckFeatureFactory:
    """
    TODO: comment

    IDEAS:
    - A feature to check regular expression
    - A feature to check types
    """

    # Instance properties (decorated with @property)
    @property
    def dict_feature_getters(self) -> dict[str, callable]:
        return self._dict_feature_getters

    # Constants
    const_fn_data_extract_checker__count: str = "count"
    const_fn_data_extract_checker__column_label: str = "column"

    const__feature_getter_function_prefix: str = "get_data_check_feature__"

    # Class properties
    _logger: Logger = getLogger(__name__)

    def __init__(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We initialize the catalog of feature getter by introspecting the class and searching for all function
        # that starts with "get_data_check_feature__"
        self._dict_feature_getters: dict[str, callable] = {
            i_fn_label[len(self.const__feature_getter_function_prefix):]:
                getattr(DataCheckFeatureFactory, i_fn_label)
            for i_fn_label in dir(DataCheckFeatureFactory)
            if (
                    callable(getattr(DataCheckFeatureFactory, i_fn_label))
                    and i_fn_label.startswith(self.const__feature_getter_function_prefix)
            )
        }
        self._logger.debug(f"DataCheckFeatureFactory initialized with '{len(self.dict_feature_getters)}' "
                           f"feature getters: '{', '.join(self.dict_feature_getters)}'.")

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def get_check_feature(
            self,
            str_feature_label: str,
            **kwargs
    ) -> callable:
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        if str_feature_label not in self.dict_feature_getters:
            self._logger.debug(f"There is not getter for the feature labelled '{str_feature_label}'. Only the "
                               f"following are available: '{', '.join(self.dict_feature_getters)}")
            return None

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return self.dict_feature_getters[str_feature_label](self, **kwargs)

    def get_check_features_labels(self) -> list[str]:
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _lst_the_return: list[str] = list(self.dict_feature_getters.keys())

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return _lst_the_return

    def get_data_check_feature__check_duplicate(
            self,
            columns: list[str] | str
    ):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__check_duplicate(
                df_data_extract: DataFrame,
        ) -> Series | None:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            # We first verify that the columns to check are effectively present in the dataframe...
            if isinstance(columns, str):
                if columns not in df_data_extract.columns:
                    raise Exception(f"Column '{columns}' is missing from the data extract to check.")
            else:
                for i_col in columns:
                    if i_col not in df_data_extract.columns:
                        raise Exception(f"Column '{i_col}' is missing from the data extract to check.")

            # We select all the duplicated records
            the_duplicates: Series | DataFrame = df_data_extract[columns][
                df_data_extract.duplicated(subset=columns, keep=False)
            ]

            # If no duplicated records, we just return null
            if len(the_duplicates.index) == 0:
                s_the_return: None = None

            # If duplicated records are in a Series
            elif isinstance(the_duplicates, Series):
                # CHECK: we only check one column...
                if not isinstance(columns, str):
                    raise Exception(f"Unexpected case: duplicated returned as Series, while columns is of type "
                                    f"'{type(columns)}'.")

                # We count the number of occurrence by the parameter "columns"
                # The parameter "columns" is the index, and we label the number of occurrence "count"
                s_the_return: Series = the_duplicates.value_counts()

                # We label properly the index and the column
                s_the_return.name = self.const_fn_data_extract_checker__count
                s_the_return.index.name = columns

            # If duplicated records are in a DataFrame
            elif isinstance(the_duplicates, DataFrame):
                s_the_return: Series = the_duplicates.groupby(by=columns).size()

                # We label properly the index and the column
                s_the_return.name = self.const_fn_data_extract_checker__count
                # NOT NEEDED: s_the_return.index.name = columns

            # Else, exception...
            else:
                raise Exception(
                    f"The function df_data_extract[columns][df_data_extract.duplicated(subset=columns, keep=False)]"
                    f"returned an instance of type '{type(the_duplicates)}', while only Series or DataFrame was "
                    f"expected."
                )

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return s_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__check_duplicate

    def get_data_check_feature__check_null(
            self,
            columns: list[str] | str
    ):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__check_null(
                df_data_extract: DataFrame,
        ) -> Series | None:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            # We first verify that the columns to check are effectively present in the dataframe...
            if isinstance(columns, str):
                if columns not in df_data_extract.columns:
                    raise Exception(f"Column '{columns}' is missing from the data extract to check.")

                lst_columns: list[str] = [columns]
            else:
                for i_col in columns:
                    if i_col not in df_data_extract.columns:
                        raise Exception(f"Column '{i_col}' is missing from the data extract to check.")

                lst_columns: list[str] = columns

            # we instantiate the Series we will return with the columns containing null values
            s_the_return: Series = Series(
                data=[],
                index=Index(
                    data=[],
                    name=self.const_fn_data_extract_checker__column_label
                ),
                name=DataCheckFeatureFactory.const_fn_data_extract_checker__count,
                dtype=int64
            )

            # We loop through each and every column to check
            for i_col in lst_columns:
                int_the_null_count: int = df_data_extract[i_col].isna().sum()
                if int_the_null_count > 0:
                    s_the_return[i_col] = int_the_null_count

            # If no column contains null, we just return None
            if len(s_the_return.index) == 0:
                s_the_return: None = None

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return s_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__check_null

    def get_data_check_feature__check_isin(
            self,
            columns: list[str] | str,
            values: list
    ):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        if isinstance(columns, str):
            _lst_the_columns: list[str] = [columns]
        else:
            _lst_the_columns: list[str] = columns

        _set_the_authorized_values: set = set(values)

        def fn__check_isin(
                df_data_extract: DataFrame,
        ) -> Series | None:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            _s_the_return: Series | None = Series(dtype='object')

            # For each column to check
            for i_col in _lst_the_columns:

                # We verify that the column exists in the dataframe..
                if i_col not in df_data_extract.columns:
                    self._logger.error(f"Column '{i_col}' is missing from the data extract to check.")

                else:

                    # We get the unique values in the column
                    _set_the_unique_values: set = set(df_data_extract[i_col].unique())

                    _set_the_unauthorized_values: set = _set_the_unique_values - _set_the_authorized_values

                    if len(_set_the_unauthorized_values) > 0:
                        _s_the_return[i_col] = list(_set_the_unauthorized_values)

            if len(_s_the_return) == 0:
                _s_the_return = None

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return _s_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__check_isin
