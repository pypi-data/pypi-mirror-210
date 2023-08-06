import logging
from inspect import stack

import click
from click import BadParameter
from com.enovation.helper.click.python_literal_argument_and_option import PythonLiteralArgument
from pandas import DataFrame

from com.enovation.toolbox.data_handler.data_handler import DataHandler

_logger: logging.Logger = logging.getLogger(__name__)


@click.command('dh-sequence')
@click.pass_context
@click.argument('alias-in-data-extract', type=str)
@click.argument('alias-in-config', type=str)
@click.argument('sequence', type=str)
@click.argument('alias-out-data-handled', type=str)
def dh_sequence(ctx_context, alias_in_data_extract, alias_in_config, sequence, alias_out_data_handled):
    """
    Handle a data frame
    - Load dataframe labelled ALIAS_IN_DATA_EXTRACT in context
    - Execute the SEQUENCE that is configured in a dictionary labelled ALIAS_IN_CONFIG in context
    - Persist the output into context as a dataframe labelled ALIAS_OUT_DATA_HANDLED.

    Note: this command only executes one sequence. In case you need to execute a list of sequences, use the equivalent
    command dh-sequences (with an 's')
    """
    _logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

    # ##################################################################################################################
    # ##################################################################################################################
    # WE CHECK ARGUMENTS
    # ##################################################################################################################
    # ##################################################################################################################

    # ##################################################################################################################
    # 1. ALIAS IN CONFIG
    if alias_in_config not in ctx_context.obj:
        raise BadParameter(
            message=f"Cannot find argument '{alias_in_config}' in context, as the dictionary configuration with the "
                    f"logic to handle your data.",
            param_hint=f"Ensure you effectively load in the context a dictionary configuration with the logic to "
                       f"handle your data.",
            ctx=ctx_context
        )

    if not isinstance(ctx_context.obj[alias_in_config], dict):
        raise BadParameter(
            message=f"Argument '{alias_in_config}' is of type '{type(ctx_context.obj[alias_in_config])}' while "
                    f"'dict' is expected.",
            param_hint=f"Ensure you effectively provide an argument '{alias_in_config}' of type 'dict'.",
            ctx=ctx_context
        )

    # ##################################################################################################################
    # 2. ALIAS IN DATA EXTRACT
    if alias_in_data_extract not in ctx_context.obj:
        raise BadParameter(
            message=f"Cannot find argument '{alias_in_data_extract}' in context, as the data extraction to handle.",
            param_hint=f"Ensure you effectively load in the context a dataframe with the data extraction to handle.",
            ctx=ctx_context
        )

    if not isinstance(ctx_context.obj[alias_in_data_extract], DataFrame):
        raise BadParameter(
            message=f"Argument '{alias_in_data_extract}' is of type '{type(ctx_context.obj[alias_in_data_extract])}' "
                    f"while 'DataFrame' is expected.",
            param_hint=f"Ensure you effectively provide an argument '{alias_in_data_extract}' of type 'DataFrame'.",
            ctx=ctx_context
        )

    # ##################################################################################################################
    # 3. ALIAS OUT DATA HANDLED
    if alias_out_data_handled in ctx_context.obj:
        _logger.warning(f"Argument '{alias_out_data_handled}' exists in context, of type "
                        f"'{type(ctx_context[alias_out_data_handled])}'. It will be overriden.")

    # ##################################################################################################################
    # ##################################################################################################################
    # WE EXECUTE THE LOGIC
    # ##################################################################################################################
    # ##################################################################################################################

    try:
        _the_data_handler: DataHandler = DataHandler(
            dict_config=ctx_context.obj[alias_in_config]
        )
    except Exception as e_exception:
        _logger.fatal(f"An exception was raised when instantiating the DataHandler...", exc_info=e_exception)
        raise e_exception

    try:
        _df_the_enriched_data: DataFrame = _the_data_handler.handle_data(
            df_data=ctx_context.obj[alias_in_data_extract],
            sequence_alias=sequence
        )
    except Exception as e_exception:
        _logger.fatal(f"An exception was raised when running sequence '{sequence}...", exc_info=e_exception)
        raise e_exception

    ctx_context.obj[alias_out_data_handled] = _df_the_enriched_data
    ctx_context.obj["_" + alias_out_data_handled] = {"src": "dh-sequence"}

    _logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")


@click.command('dh-sequences')
@click.pass_context
@click.argument('alias-in-data-extract', type=str)
@click.argument('alias-in-config', type=str)
@click.argument('sequences', cls=PythonLiteralArgument, type=list)
@click.argument('alias-out-data-handled', type=str)
def dh_sequences(ctx_context, alias_in_data_extract, alias_in_config, sequences, alias_out_data_handled):
    """
    Handle a data frame
    - Load dataframe labelled ALIAS_IN_DATA_EXTRACT in context
    - Execute each sequence from SEQUENCES that are configured in a dictionary labelled ALIAS_IN_CONFIG in context
    - Persist the output into context as a dataframe labelled ALIAS_OUT_DATA_HANDLED.

    Note: this command executes a list of sequences. In case you need to execute one single sequence, use the
    equivalent command dh-sequence (without any 's')
    """
    _logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

    # ##################################################################################################################
    # ##################################################################################################################
    # WE CHECK ARGUMENTS...
    # ##################################################################################################################
    # ##################################################################################################################

    # ##################################################################################################################
    # 1. ALIAS IN CONFIG
    if alias_in_config not in ctx_context.obj:
        raise BadParameter(
            message=f"Cannot find argument '{alias_in_config}' in context, as the dictionary configuration with the "
                    f"logic to handle your data.",
            param_hint=f"Ensure you effectively load in the context a dictionary configuration with the logic to "
                       f"handle your data.",
            ctx=ctx_context
        )

    if not isinstance(ctx_context.obj[alias_in_config], dict):
        raise BadParameter(
            message=f"Argument '{alias_in_config}' is of type '{type(ctx_context.obj[alias_in_config])}' while "
                    f"'dict' is expected.",
            param_hint=f"Ensure you effectively provide an argument '{alias_in_config}' of type 'dict'.",
            ctx=ctx_context
        )

    # ##################################################################################################################
    # 2. ALIAS IN DATA EXTRACT
    if alias_in_data_extract not in ctx_context.obj:
        raise BadParameter(
            message=f"Cannot find argument '{alias_in_data_extract}' in context, as the data extraction to handle.",
            param_hint=f"Ensure you effectively load in the context a dataframe with the data extraction to handle.",
            ctx=ctx_context
        )

    if not isinstance(ctx_context.obj[alias_in_data_extract], DataFrame):
        raise BadParameter(
            message=f"Argument '{alias_in_data_extract}' is of type '{type(ctx_context.obj[alias_in_data_extract])}' "
                    f"while 'DataFrame' is expected.",
            param_hint=f"Ensure you effectively provide an argument '{alias_in_data_extract}' of type 'DataFrame'.",
            ctx=ctx_context
        )

    # ##################################################################################################################
    # 3. ALIAS OUT DATA HANDLED
    if alias_out_data_handled in ctx_context.obj:
        _logger.warning(f"Argument '{alias_out_data_handled}' exists in context, of type "
                        f"'{type(ctx_context[alias_out_data_handled])}'. It will be overriden.")

    # ##################################################################################################################
    # ##################################################################################################################
    # WE EXECUTE THE LOGIC
    # ##################################################################################################################
    # ##################################################################################################################

    try:
        _the_data_handler: DataHandler = DataHandler(
            dict_config=ctx_context.obj[alias_in_config]
        )
    except Exception as e_exception:
        _logger.fatal(f"An exception was raised when instantiating the DataHandler...", exc_info=e_exception)
        raise e_exception

    _df_the_return: DataFrame = ctx_context.obj[alias_in_data_extract]

    try:
        _df_the_enriched_data: DataFrame = _the_data_handler.handle_data(
            df_data=ctx_context.obj[alias_in_data_extract],
            sequence_alias=sequences
        )
    except Exception as e_exception:
        _logger.fatal(f"An exception was raised when running one among the following sequences "
                      f"'{', '.join(sequences)}...", exc_info=e_exception)
        raise e_exception

    ctx_context.obj[alias_out_data_handled] = _df_the_enriched_data
    ctx_context.obj["_" + alias_out_data_handled] = {"src": "dh-sequence"}

    _logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
