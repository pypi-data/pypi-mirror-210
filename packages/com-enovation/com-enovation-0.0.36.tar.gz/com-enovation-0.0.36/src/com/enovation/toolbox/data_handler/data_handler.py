from copy import deepcopy
from inspect import stack

from logging import Logger, getLogger

from pandas import DataFrame

from com.enovation.toolbox.data_handler.data_checker.data_check_feature_factory import DataCheckFeatureFactory
from com.enovation.toolbox.data_handler.data_modifier.data_modification_feature_factory import DataModificationFeatureFactory


class DataHandler:
    """
    Capabilities to easily handle data through configuration (rather than coding):
    - Enrich: modify the data set
    - Check: check the data set without altering it.

    Configuration is of the kind:
        {
            "A label for the sequence that can be run in isolation": {
                "description": "A description of the sequence, useful to monitor and debug the execution",
                "steps": [
                    {
                        "description": "Description of the step 1 that is executed while calling the sequence",
                        "feature": "The name of the feature that is called",
                        "param": {
                            ... Depending on the feature, parameters are different ...,
                            "b_copy":false  # or true in case we need to copy the dataframe before it is modified
                                            # only valable for "modification" features, not relevant for "checks"
                        }
                    }
                ]
            }
        }
    """

    # Instance properties (decorated with @property)
    @property
    def dict_configuration(self) -> dict:
        return self._dict_configuration

    @property
    def dict_callable_sequence(self) -> dict:
        return self._dict_callable_sequence

    # Constants
    const_str__config_tag__description__as_str: str = "description"
    const_str__config_tag__steps__as_list: str = "steps"
    const_str__config_tag__feature__as_str: str = "feature"
    const_str__config_tag__param__as_str: str = "param"

    const_str__config_tag__callable__as_callable: str = "callable"
    const_str__config_tag__callable__type__as_str: str = "type"
    const_str__config_tag__callable__type__check__as_str: str = "check"
    const_str__config_tag__callable__type__modification__as_str: str = "modification"

    # Class properties
    _logger: Logger = getLogger(__name__)

    def __init__(
            self,
            dict_config: dict
    ):
        """
        Initialize a data handler instance using its configuration.
        Once initialized, sequences can be called using the function handle_data
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        self._dict_configuration: dict = \
            self._check_dict_config(dict_config=dict_config)

        self._dict_callable_sequence: dict = \
            self._instantiate_callable_sequence(dict_config=dict_config)

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

    def handle_data(
            self,
            df_data: DataFrame,
            sequence_alias: str | list[str] = None
    ) -> DataFrame:
        """
        Execute a sequence or a list of sequences.

        In case:
        - No sequence is provided, all the sequences are executed
        - A sequence to execute is not configured, an exception is raised.
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        if sequence_alias is None:
            _lst_the_sequence_alias: list[str] = [i_seq for i_seq in self.dict_configuration]
        elif isinstance(sequence_alias, str):
            _lst_the_sequence_alias: list[str] = [sequence_alias]
        else:
            _lst_the_sequence_alias: list[str] = sequence_alias

        # We set the return value as the input dataframe
        _df_the_return: DataFrame = df_data

        # We run each sequence one by one
        for i_sequence in _lst_the_sequence_alias:

            # We check the sequence we call is effectively configured
            if i_sequence not in self.dict_configuration:
                raise Exception(f"The sequence '{i_sequence}' is not defined in the configuration, which contains "
                                f"the following sequences: '{', '.join(self.dict_configuration)}'.")

            # We get the sequence configuration
            _dict_the_sequence_config: dict = self.dict_callable_sequence[i_sequence]

            self._logger.info(f"Sequence '{i_sequence}' is starting.")

            # We loop through each and every steps
            for i_dict_step_configuration in _dict_the_sequence_config[self.const_str__config_tag__steps__as_list]:

                _fn: callable = i_dict_step_configuration[self.const_str__config_tag__callable__as_callable]

                if i_dict_step_configuration[self.const_str__config_tag__callable__type__as_str] == \
                        self.const_str__config_tag__callable__type__modification__as_str:

                    _df_the_return = _fn(_df_the_return)
                    self._logger.info(
                        f"\tStep '{i_dict_step_configuration[self.const_str__config_tag__feature__as_str]} - "
                        f"{i_dict_step_configuration[self.const_str__config_tag__description__as_str]}' returned.")

                else:
                    _s_the_return = _fn(_df_the_return)

                    if _s_the_return is None:
                        self._logger.info(
                            f"\tStep '{i_dict_step_configuration[self.const_str__config_tag__feature__as_str]} - "
                            f"{i_dict_step_configuration[self.const_str__config_tag__description__as_str]}' returned "
                            f"None.")

                    else:
                        _s_the_unexpected_values: str = ""
                        for k, v in _s_the_return.items():
                            _s_the_unexpected_values += "\n\t- "+str(k)+": "+str(v)
                        raise Exception(
                            f"-----------------\n"
                            f"Step '{i_dict_step_configuration[self.const_str__config_tag__feature__as_str]} - "
                            f"{i_dict_step_configuration[self.const_str__config_tag__description__as_str]}' returned "
                            f"the following: {_s_the_unexpected_values}"
                            f"\n-----------------")

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")

        return _df_the_return

    def _check_dict_config(self, dict_config: dict) -> dict:
        """
        TODO: Implement the json schema to check the configuration
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")
        self._logger.error(f"TODO: the configuration json schema is not yet implemented.")
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
        return dict_config

    def _instantiate_callable_sequence(self, dict_config: dict) -> dict:
        """
        We enrich the data handler configuration with callable instances of the features configured, that can then be
        easily called within "handle_data".
        We return a duplicated (deep copied) instance of dict_config, not to alter the original object.
        """
        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is called")

        # We instantiate the feature factories
        _the_modification_features_factory: DataModificationFeatureFactory = DataModificationFeatureFactory()
        _the_check_features_factory: DataCheckFeatureFactory = DataCheckFeatureFactory()

        # We copy the sequence configuration, so we keep all the details in the callable sequence...
        _dict_the_return: dict = deepcopy(dict_config)

        # We then enrich sequence by sequence
        for i_sequence_label, i_sequence_config in _dict_the_return.items():

            # We then enrich step by step
            for i_step in i_sequence_config[self.const_str__config_tag__steps__as_list]:

                _modif_fn: callable = _the_modification_features_factory.get_modification_feature(
                    str_feature_label=i_step[self.const_str__config_tag__feature__as_str],
                    **i_step[self.const_str__config_tag__param__as_str]
                )

                _check_fn: callable = _the_check_features_factory.get_check_feature(
                    str_feature_label=i_step[self.const_str__config_tag__feature__as_str],
                    **i_step[self.const_str__config_tag__param__as_str]
                )

                if (_modif_fn is None) & (_check_fn is None):
                    raise Exception(
                        f"No feature labelled '{i_step[self.const_str__config_tag__feature__as_str]}' could be "
                        f"found. Be aware that only the following features exist:"
                        f"\nMODIFICATION FEATURES: "
                        f"{', '.join(_the_modification_features_factory.get_modifications_features_labels())}"
                        f"\nCHECK FEATURES: {', '.join(_the_check_features_factory.get_check_features_labels())}")

                if (_modif_fn is not None) & (_check_fn is not None):
                    self._logger.error(
                        f"Feature labelled '{i_step[self.const_str__config_tag__feature__as_str]}' is ambiguous "
                        f"as it is defined both as a CHECK and a MODIFICATION feature. It will arbitrarily be "
                        f"considered as a MODIFICATION feature. To fix this issue, you need to rename the CHECK "
                        f"feature '{i_step[self.const_str__config_tag__feature__as_str]}'.")

                if _modif_fn:
                    i_step[self.const_str__config_tag__callable__as_callable] = _modif_fn
                    i_step[self.const_str__config_tag__callable__type__as_str] = \
                        self.const_str__config_tag__callable__type__modification__as_str

                else:
                    i_step[self.const_str__config_tag__callable__as_callable] = _check_fn
                    i_step[self.const_str__config_tag__callable__type__as_str] = \
                        self.const_str__config_tag__callable__type__check__as_str

        self._logger.debug(f"Function '{stack()[0].filename} - {stack()[0].function}' is returning")
        return _dict_the_return
