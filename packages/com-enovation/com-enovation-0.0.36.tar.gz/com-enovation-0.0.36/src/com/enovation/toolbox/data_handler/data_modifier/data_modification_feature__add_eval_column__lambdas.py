import datetime
import re
from datetime import timedelta

from numpy import nan
from pandas import DataFrame, Series


def _enov_timedelta(
        s_column: Series,
        f_delta_days: float
) -> Series:
    """
    Function that can be called through function "pandas.DataFrame.eval":
    `col target label`=@enov_timedelta(`col source label`, 15)

    Exceptions are thrown: FutureWarning: In a future version, object-dtype columns with all-bool values
    will not be included in reductions with bool_only=True. Explicitly cast to bool dtype instead.

    f_delta_days does not work with negative value as of 9-Apr-2023, as python cannot parse the function call... and
    raise an AttributeError xception with message 'UnaryOp object has no attribute value'.
    """
    return s_column + timedelta(days=f_delta_days)


def _enov_concatenate_boolean_tags(
        s_column: list[Series],
        s_labels: list[str]
):
    """
    TODO: check s_column has at least one series
    TODO: check all series have the same number of records
    TODO: check the s label length is equal to the s column length
    TODO: check the index is equal across columns
    """
    s_the_return: Series = Series([""] * len(s_column[0]), index=s_column[0].index)
    # We replace True/ False values by the labels

    for i_col in range(len(s_column)):
        # s_the_return = s_the_return.str.cat(s_column[i_col].replace(
        #     True, s_labels[i_col]+"|").replace(False, ""))

        s_the_return = s_the_return + s_column[i_col].replace(
            True, "|" + s_labels[i_col]).replace(False, "")

    # In case several tags were concatenated, we just remove the very first '|'
    s_the_return = s_the_return.str.slice(start=1)

    return s_the_return


def _enov_regex(
        s_column: Series,
        str_regex: str
):
    s_the_return: Series = s_column.str.findall(pat=str_regex, flags=re.MULTILINE)
    return s_the_return


def _enov_list_to_dates(
        s_column: Series,
        pattern: str
):
    s_the_return: Series = s_column.apply(
        func=lambda a_list: [datetime.datetime.strptime(date, pattern).date() for date in a_list]
    )
    return s_the_return


def _enov_list_max(
        s_column: Series
):
    s_the_return: Series = s_column.apply(
        func=lambda a_list: max(a_list) if len(a_list) > 0 else nan
    )
    return s_the_return


def _enov_lambda(
        columns: list[Series] | Series,
        s_lambda: str
) -> Series:

    if isinstance(columns, Series):
        columns = [columns]

    _df: DataFrame = DataFrame({
        i_col.name: i_col for i_col in columns
    })

    _s_the_return: Series = _df.apply(func=lambda x: eval(s_lambda))
    return _s_the_return


def _enov_get_record_at_index_from_tuple(
        s_series_of_tuples: Series,
        i_index: int
) -> Series:

    # In case we have null values in the serie, we replace with empty tuple...
    #s_series_of_tuples.fillna(())

    _s_the_return: Series = s_series_of_tuples.apply(
        func=lambda i_rec: nan if (i_rec is None) else (i_rec[i_index] if (len(i_rec) >= i_index) else nan)
    )

    return _s_the_return
