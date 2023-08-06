import importlib
import importlib.machinery
import importlib.util
from inspect import stack
from logging import Logger, getLogger
from types import ModuleType

from numpy import where, nan
from pandas import DataFrame, to_datetime, to_numeric

from com.enovation.toolbox.data_handler.data_modifier import data_modification_feature__add_eval_column__lambdas


class DataModificationFeatureFactory:
    """
    TODO: comment

    IDEAS:
    - replace value by
    - replace nan by
    """

    # Instance properties (decorated with @property)
    @property
    def dict_feature_getters(self) -> dict[str, callable]:
        return self._dict_feature_getters

    # Constants
    const__type_columns__str: str = "str"
    const__type_columns__date: str = "date"
    const__type_columns__float: str = "float"
    const__type_columns__int: str = "int"

    const__feature_getter_function_prefix: str = "get_data_modification_feature__"

    # Class properties
    _logger: Logger = getLogger(__name__)

    def __init__(self):
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We initialize the catalog of feature getter by introspecting the class and searching for all function
        # that starts with "get_data_modification_feature__"
        self._dict_feature_getters: dict[str, callable] = {
            i_fn_label[len(self.const__feature_getter_function_prefix):]:
                getattr(DataModificationFeatureFactory, i_fn_label)
            for i_fn_label in dir(DataModificationFeatureFactory)
            if (
                    callable(getattr(DataModificationFeatureFactory, i_fn_label))
                    and i_fn_label.startswith(self.const__feature_getter_function_prefix)
            )
        }
        self._logger.debug(f"DataModificationFeatureFactory initialized with '{len(self.dict_feature_getters)}' "
                           f"feature getters: '{', '.join(self.dict_feature_getters)}'.")

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def get_modification_feature(
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

    def get_modifications_features_labels(self) -> list[str]:
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        _lst_the_return: list[str] = list(self.dict_feature_getters.keys())

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return _lst_the_return

    def get_data_modification_feature__type_columns(
            self,
            dict_columns: dict[str, str],
            b_copy: bool = False
    ):
        """
        Illustration:
        - Sample 1:
            With dict_column = {
                "Jsg - ID": "str",
                "Jsg - Snapshot": "str"
            }
            Will type
            - Column labelled "Jsg - ID" into "string"
            - Column labelled "Jsg - Snapshot" into "string"

        :param dict_columns: type by column
        :param b_copy: whether dataframe is to be copied before modified
        :return: modified dataframe
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__type_columns(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            for str_col, str_type in dict_columns.items():

                if str_col in df_data_extract.columns:

                    if str_type == self.const__type_columns__str:

                        # df_the_return[str_col].replace(numpy.nan, "", inplace=True)
                        try:
                            df_the_return[str_col] = df_the_return[str_col].astype(str)
                        except Exception as an_exception:
                            raise Exception(f"Exception when typing column '{str_col}' to '{str_type}'.") \
                                from an_exception

                    elif str_type == self.const__type_columns__date:
                        try:
                            df_the_return[str_col] = to_datetime(
                                df_the_return[str_col],
                                infer_datetime_format=True
                            ).dt.normalize()
                        except Exception as an_exception:
                            raise Exception(f"Exception when typing column '{str_col}' to '{str_type}'.") \
                                from an_exception

                    elif str_type == self.const__type_columns__float:
                        try:
                            df_the_return[str_col] = to_numeric(
                                arg=df_the_return[str_col],
                                # errors="coerce",
                                downcast="float"
                            )  # .fillna(0)
                        except Exception as an_exception:
                            raise Exception(f"Exception when typing column '{str_col}' to '{str_type}'.") \
                                from an_exception

                    elif str_type == self.const__type_columns__int:
                        try:
                            df_the_return[str_col] = to_numeric(
                                arg=df_the_return[str_col],
                                # errors="coerce",
                                downcast="integer"
                            )  # .fillna(0)
                        except Exception as an_exception:
                            raise Exception(f"Exception when typing column '{str_col}' to '{str_type}'.") \
                                from an_exception
                    else:
                        raise Exception(
                            f"When transcoding the date extract, we did not know what to do with column '{str_col}' "
                            f"as we don't know the target type '{str_type}'...")

                else:
                    self._logger.warning(f"Column '{str_col}' is to be typed as '{str_type}', but it does not exist "
                                         f"in the data extract.")

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__type_columns

    def get_data_modification_feature__replace_values(
            self,
            dict_columns: dict[str, dict],
            b_copy: bool = False
    ):
        """
        Illustration:
        - Sample 1:
            With dict_column = {
                "Jsg - ID": {
                    "-": 0,
                    "True": 1
                    "False": 0
                }
            }
            Will replace
            - In column labelled "Jsg - ID":
                - Value "-" into 0
                - Value "True" into 1
                - Value "False" into 0

        :param dict_columns: by column, the values to be replaced
        :param b_copy: whether dataframe is to be copied before modified
        :return: modified dataframe
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__replace_values(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            # We loop through each and every column to process
            for str_col, dict_transco in dict_columns.items():

                # If the column exist in the dataframe
                if str_col in df_data_extract.columns:

                    # We loop through each and every transco
                    for k_from, v_to in dict_transco.items():
                        df_the_return[str_col].replace(k_from, v_to, inplace=True)

                else:
                    self._logger.warning(f"Column '{str_col}' is to be modified, with values to be transcoded, but it "
                                         f"does not exist in the data extract.")

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__replace_values

    def get_data_modification_feature__replace_missing_values(
            self,
            dict_columns: dict,
            b_copy: bool = False
    ):
        """
        Illustration:
        - Sample 1:
            With dict_column = {
                "Jsg - ID": 0,
                "Jsg - Snapshot": "one"
            }
            Will replace missing values (aka NaN)
            - By 0 in column labelled "Jsg - ID"
            - By "one" in column labelled "Jsg - Snapshot"

        :param dict_columns: by column, the value to replace missing values
        :param b_copy: whether dataframe is to be copied before modified
        :return: modified dataframe
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__replace_missing_values(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            # We loop through each and every column to process
            for str_col, v_value in dict_columns.items():

                # If the column exist in the dataframe
                if str_col in df_data_extract.columns:

                    df_the_return[str_col].fillna(value=v_value, inplace=True)

                else:
                    self._logger.warning(f"Column '{str_col}' is to be modified, with missing values to be set to "
                                         f"'{v_value}', but it does not exist in the data extract.")

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__replace_missing_values

    def get_data_modification_feature__add_eval_columns(
            self,
            str_expressions: list[str] | str,
            local_dict: dict = None,
            lst_dependencies: list[str] = None,
            b_copy: bool = False
    ):
        """
        Illustration:
        - Sample 1:
            With str_expressions=f" " "
                DQ_01=StatusA+StatusB=={[
                    "OpenOpen",
                    "OpenInactive",
                    "InactiveOpen",
                    "InactiveInactive",
                    "ClosedClosed"
                ]}
                DQ_02=StatusA=='Open'
                " " "
            We add 2 columns:
                - DQ_01 equal to True in case concatenation Status A + B is among the ones in the list (authorized)
                - DQ_02 equal to True if Status A is "Open"

        :param lst_dependencies:
        :param local_dict:
        :param str_expressions: the expression to add new columns through eval
        :param b_copy: whether dataframe is to be copied before modified
        :return: modified dataframe
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        if isinstance(str_expressions, list):
            str_expressions = "\n".join(str_expressions)

        # We enrich the dictionary of lambdas
        if local_dict is None:
            local_dict = {}

        local_dict.update(
            {
                i_fn_label[1:]: getattr(data_modification_feature__add_eval_column__lambdas, i_fn_label)
                for i_fn_label in dir(data_modification_feature__add_eval_column__lambdas)
                if (
                    callable(getattr(data_modification_feature__add_eval_column__lambdas, i_fn_label))
                    and i_fn_label.startswith("_")
                )
            }
        )

        if lst_dependencies is None:
            lst_dependencies = []

        for i_str_dependency in lst_dependencies:
            if "." not in i_str_dependency:
                raise Exception(
                    f"The dependency '{i_str_dependency}' does not contain any '.', so it cannot be imported... "
                    f"Dependencies should be in the form 'name.of.a.module.followed.by.function_name")

            else:
                i_lst_dependency: list[str] = i_str_dependency.rsplit(".", 1)

                i_str_module_name: str = i_lst_dependency[0]
                i_str_function_name: str = i_lst_dependency[1]

                i_mdl_module: ModuleType = importlib.import_module(i_str_module_name)
                i_fn_function: callable = getattr(i_mdl_module, i_str_function_name)

                local_dict[i_str_function_name] = i_fn_function

        def fn__add_eval_column(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            df_the_return.eval(str_expressions, inplace=True, local_dict=local_dict)

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__add_eval_column

    def get_data_modification_feature__filter(
            self,
            str_expressions: str,
            b_copy: bool = False
    ):
        """
        Illustration:
        - Sample 1:
            With str_expressions=f" " "
                StatusA+StatusB=={[
                    "OpenOpen",
                    "OpenInactive",
                    "InactiveOpen",
                    "InactiveInactive",
                    "ClosedClosed"
                ]}
                " " "
            We filter rows where :
                - DQ_01 equal to True in case concatenation Status A + B is among the ones in the list (authorized)
                - DQ_02 equal to True if Status A is "Open"

        :param str_expressions: the expression to add new columns through eval
        :param b_copy: whether dataframe is to be copied before modified
        :return: modified dataframe
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__filter(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            df_the_return.query(str_expressions, inplace=True)

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__filter

    def get_data_modification_feature__drop_columns(
            self,
            lst_columns_to_drop: list[str],
            b_copy: bool = False
    ):
        """
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__drop_columns(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            # We check the columns to drop are effectively in the dataframe
            _lst_the_missing_columns: list[str] = [
                i_col
                for i_col in lst_columns_to_drop
                if i_col not in df_data_extract.columns
            ]
            if len(_lst_the_missing_columns) > 0:
                self._logger.error(
                    f"Function '{stack()[0].filename} - {stack()[0].function}' - "
                    f"The following columns are to be dropped, but they could not be found in the dataframe:"
                    f"\n\t- missing columns: {', '.join(_lst_the_missing_columns)}"
                    f"\n\t- dataframe columns: {', '.join(df_data_extract.columns)}")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            df_the_return.drop(
                columns=[
                    i_col
                    for i_col in lst_columns_to_drop
                    if i_col in df_data_extract.columns
                ],
                inplace=True
            )

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__drop_columns

    def get_data_modification_feature__audit_column__changed(
            self,
            s_column_to_audit: str,
            s_column_audit: str,
            lst_key_columns: list[str] = None,
            b_first_as_changed: bool = False,
            b_copy: bool = False
    ):
        """
        Function to add an audit column that tracks whether the audited column changed from one row to the next.
        In case the parameter lst_key_columns is set, the dataframe is grouped accordingly before tracking changes
        across rows.

        The column audit is "True" if value changed, "False" otherwise.
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__audit_column__changed(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            # We check the column to audit is effectively in the dataframe
            if s_column_to_audit not in df_data_extract.columns:
                raise Exception(f"The column to audit '{s_column_to_audit}' does not exist in the dataframe, which "
                                f"contains the following columns: '{', '.join(df_data_extract.columns)}'.")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            if lst_key_columns:

                # We list the key columns which effectively exist in the dataframe
                _lst_the_key_columns: list[str] = [
                    i_col
                    for i_col in lst_key_columns
                    if i_col in df_data_extract.columns
                ]

                # In case we are missing some key columns, we log an error
                if len(_lst_the_key_columns) != len(lst_key_columns):
                    _lst_the_missing_col: list[str] = [
                        i_col
                        for i_col in lst_key_columns
                        if i_col not in df_data_extract.columns
                    ]

                    self._logger.error(
                        f"Function '{stack()[0].filename} - {stack()[0].function}' - "
                        f"The following columns, to group by the dataframe, do not exist. They will be ignored..."
                        f"\n\t- missing columns: {', '.join(_lst_the_missing_col)}"
                        f"\n\t- dataframe columns: {', '.join(df_data_extract.columns)}")

                if b_first_as_changed:
                    df_the_return[s_column_audit] = (
                                                        df_the_return[s_column_to_audit].ne(
                                                            df_the_return.groupby(by=_lst_the_key_columns)[
                                                                s_column_to_audit].shift())
                                                    ) | (
                                                        df_the_return.groupby(by=_lst_the_key_columns)[
                                                            s_column_to_audit].shift().isna()
                                                    )
                else:
                    df_the_return[s_column_audit] = (
                                                        df_the_return[s_column_to_audit].ne(
                                                            df_the_return.groupby(by=_lst_the_key_columns)[
                                                                s_column_to_audit].shift())
                                                    ) & (
                                                        ~df_the_return.groupby(by=_lst_the_key_columns)[
                                                            s_column_to_audit].shift().isna()
                                                    )

            else:
                raise Exception(f"Not implemented yet.")

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__audit_column__changed

    def get_data_modification_feature__audit_column__stamped(
            self,
            s_column_to_audit: str,
            s_column_audit: str,
            s_column_to_stamp: str,
            lst_key_columns: list[str] = None,
            b_copy: bool = False
    ):
        """
        Function to add an audit column that stamp rows with the audited column not changing using the value in the
        "column to stamp" at the time the audited value was set first.
        In case the parameter lst_key_columns is set, the dataframe is grouped accordingly before tracking changes
        across rows.

        The column audit is set to the value from the "column to stamp" when the audited value changed.
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__audit_column__stamped(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            # We check the column to audit is effectively in the dataframe
            if s_column_to_audit not in df_data_extract.columns:
                raise Exception(f"The column to audit '{s_column_to_audit}' does not exist in the dataframe, which "
                                f"contains the following columns: '{', '.join(df_data_extract.columns)}'.")
            if s_column_to_stamp not in df_data_extract.columns:
                raise Exception(f"The column to stamp '{s_column_to_stamp}' does not exist in the dataframe, which "
                                f"contains the following columns: '{', '.join(df_data_extract.columns)}'.")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            if lst_key_columns is None:
                _lst_the_key_columns: list[str] = []

            else:

                # We list the key columns which effectively exist in the dataframe
                _lst_the_key_columns: list[str] = [
                    i_col
                    for i_col in lst_key_columns
                    if i_col in df_data_extract.columns
                ]

                # In case we are missing some key columns, we log an error
                if len(_lst_the_key_columns) != len(lst_key_columns):
                    _lst_the_missing_col: list[str] = [
                        i_col
                        for i_col in lst_key_columns
                        if i_col not in df_data_extract.columns
                    ]

                    self._logger.error(
                        f"Function '{stack()[0].filename} - {stack()[0].function}' - "
                        f"The following columns, to group by the dataframe, do not exist. They will be ignored..."
                        f"\n\t- missing columns: {', '.join(_lst_the_missing_col)}"
                        f"\n\t- dataframe columns: {', '.join(df_data_extract.columns)}")

            # First, we audit the column to spot when value changed: we get true/ false in the audit column
            df_the_return = self.get_data_modification_feature__audit_column__changed(
                s_column_to_audit=s_column_to_audit,
                s_column_audit=s_column_audit,
                lst_key_columns=_lst_the_key_columns,
                b_first_as_changed=True,
                b_copy=False
            )(df_the_return)

            # Whenever the audit changed is True, we set the stamp value in the audit column
            df_the_return[s_column_audit] = where(
                df_the_return[s_column_audit],
                df_the_return[s_column_to_stamp],
                nan
            )

            df_the_return[s_column_audit] =\
                df_the_return.groupby(by=_lst_the_key_columns)[s_column_audit].ffill()

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__audit_column__stamped

    def get_data_modification_feature__sort(
            self,
            by: str | list[str],
            axis: int = 0,
            ascending: bool | list[bool] = True,
            inplace: bool = False,
            kind: str = "quicksort",
            na_position: str = "last",
            ignore_index: bool = False,
            b_copy: bool = False
    ):
        """
        Function to sort the dataframe. Parameters are documented in the official pandas.DataFrame.sort_values.
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__sort(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            # We check the columns to sort is effectively in the dataframe
            if isinstance(by, str):
                _lst_by: list[str] = [by]
            elif isinstance(by, list):
                _lst_by: list[str] = by
            else:
                raise Exception(f"Parameter by is of type '{type(by)}', which is not expected.")

            _lst_missing_by: list[str] = [i_col for i_col in _lst_by if i_col not in df_data_extract.columns]
            if len(_lst_missing_by) > 0:
                self._logger.error(f"Columns to sort dataframe by are missing: '{', '.join(_lst_missing_by)}'.")
                _lst_by = [i_col for i_col in _lst_by if i_col not in _lst_missing_by]
                if len(_lst_by) == 0:
                    raise Exception(f"Among the columns to sort, none exist in the DataFrame, which is not expected.")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            df_the_return = df_the_return.sort_values(
                by=by,
                axis=axis,
                inplace=inplace,
                ascending=ascending,
                kind=kind,
                na_position=na_position,
                ignore_index=ignore_index
            )

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__sort

    def get_data_modification_feature__repeat_last(
            self,
            s_column_to_repeat: str,
            s_column_repeat: str,
            lst_key_columns: list[str] = None,
            b_copy: bool = False
    ):
        """
        Function that add a column that repeats the last value.

        Eg:
            - Function called with parameters:
                - s_column_to_repeat: Measure
                - s_column_repeat: Last Measure
                - lst_key_columns: Key
            - test data and results below
                |-------------------------------------|   |---------------|
                | Key     | Date          | Measure   |   | Last Measure  |
                |-------------------------------------|   |---------------|
                | JSG     | 01-Jan-2023   | 44 years  |   | 44 years      |
                | BCH     | 01-Jan-2023   | 44 years  |   | 44 years      |
                | JSG     | 21-May-2023   | 45 years  |   | 44 years      |
                | BCH     | 21-May-2023   | 44 years  |   | 44 years      |
                | JSG     | 24-Jul-2023   | 45 years  |   | 45 years      |
                | BCH     | 24-Jul-2023   | 45 years  |   | 44 years      |
                | JSG     | 10-Nov-2023   | 45 years  |   | 45 years      |
                | BCH     | 10-Nov-2023   | 45 years  |   | 45 years      |
                | JSG     | 31-Dec-2023   | 45 years  |   | 45 years      |
                | BCH     | 31-Dec-2023   | 45 years  |   | 45 years      |
                |-------------------------------------|   |---------------|
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        def fn__repeat_last(
                df_data_extract: DataFrame,
        ) -> DataFrame:
            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

            # We check the column to repeat is effectively in the dataframe
            if s_column_to_repeat not in df_data_extract.columns:
                raise Exception(f"The column to repeat '{s_column_to_repeat}' does not exist in the dataframe, which "
                                f"contains the following columns: '{', '.join(df_data_extract.columns)}'.")

            # We check the repeat column is not in the dataframe
            if s_column_repeat in df_data_extract.columns:
                raise Exception(f"The repeat column '{s_column_repeat}' does exist in the dataframe, which is not "
                                f"expected.")

            if b_copy:
                df_the_return: DataFrame = df_data_extract.copy()
            else:
                df_the_return: DataFrame = df_data_extract

            if lst_key_columns is None:
                _lst_the_key_columns: list[str] = []

            else:

                # We list the key columns which effectively exist in the dataframe
                _lst_the_key_columns: list[str] = [
                    i_col
                    for i_col in lst_key_columns
                    if i_col in df_data_extract.columns
                ]

                # In case we are missing some key columns, we log an error
                if len(_lst_the_key_columns) != len(lst_key_columns):
                    _lst_the_missing_col: list[str] = [
                        i_col
                        for i_col in lst_key_columns
                        if i_col not in df_data_extract.columns
                    ]

                    self._logger.error(
                        f"Function '{stack()[0].filename} - {stack()[0].function}' - "
                        f"The following columns, to group by the dataframe, do not exist. They will be ignored..."
                        f"\n\t- missing columns: {', '.join(_lst_the_missing_col)}"
                        f"\n\t- dataframe columns: {', '.join(df_data_extract.columns)}")

            # First, we audit the column to spot when value changed: we get true/ false in the audit column
            df_the_return = self.get_data_modification_feature__audit_column__changed(
                s_column_to_audit=s_column_to_repeat,
                s_column_audit=s_column_repeat,
                lst_key_columns=_lst_the_key_columns,
                b_first_as_changed=False,
                b_copy=False
            )(df_the_return)

            # Whenever the audit changed is False, we set the repeated value as the current value
            df_the_return[s_column_repeat] = where(
                df_the_return[s_column_repeat],
                nan,
                df_the_return[s_column_to_repeat]
            )

            df_the_return[s_column_repeat] =\
                df_the_return.groupby(by=_lst_the_key_columns)[s_column_repeat].ffill()

            self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

            return df_the_return

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return fn__repeat_last
