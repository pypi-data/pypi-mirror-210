from perun.connector.utils.Logger import Logger
from satosa.context import Context
from satosa.internal import InternalData
from satosa.micro_services.base import ResponseMicroService

import importlib


logger = Logger.get_logger(__name__)


class ComputeEligibility(ResponseMicroService):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("ComputeEligibility is active")
        self.__ELIGIBILITY_TIMESTAMPS_DICT_ATTRIBUTE = "internal_eligibility_attribute"
        self.__SUPPORTED_ELIGIBILITY_TYPES = "supported_eligibility_types"
        self.__eligibility_timestamps_dict_attribute = config.get(
            self.__ELIGIBILITY_TIMESTAMPS_DICT_ATTRIBUTE
        )
        self.__supported_eligibility_types = config.get(
            self.__SUPPORTED_ELIGIBILITY_TYPES
        )

    def process(self, context: Context, data: InternalData):
        """
        Obtains dict with format { eligiblility_type: <unix_timestamp> }
        from the internal data and runs a function configured for the
        given eligibility type. The function either returns a false or
        a new timestamp, in which case the time in the dictionary is
        updated. It strongly relies on PerunAttributes to fill the dict
        beforehand.

        @param context: object for sharing proxy data through the current
                        request
        @param data: data carried between frontend and backend,
                     namely dict of services and timestamps of the last
                     eligible accesses of user within said service
        """
        last_seen_eligible_timestamps_dict = data.attributes.get(
            self.__eligibility_timestamps_dict_attribute, {}
        )
        if not last_seen_eligible_timestamps_dict:
            logger.info(
                "No eligibility timestamps found. Skipping eligibility computation. "
                "Attribute {self.__eligibility_timestamps_dict_attribute} might"
                " be missing in provided data"
            )
        for (
            eligibility_type,
            function_path,
        ) in self.__supported_eligibility_types.items():
            provided_timestamp = last_seen_eligible_timestamps_dict.get(
                eligibility_type, None
            )
            if provided_timestamp:
                mod_name, func_name = function_path.rsplit(".", 1)
                mod = importlib.import_module(mod_name)
                function = getattr(mod, func_name, None)
                if function:
                    kwargs = {}
                    try:
                        new_timestamp = function(data, **kwargs)
                        logger.info(
                            f"Function {func_name} calculated new timestamp"
                            f" {new_timestamp}, "
                            f"provided timestamp is {provided_timestamp}."
                        )
                        if new_timestamp > provided_timestamp:
                            last_seen_eligible_timestamps_dict[
                                eligibility_type
                            ] = new_timestamp
                    except Exception as e:
                        logger.error(
                            f"Function {function} failed with an exception {e}."
                        )
                else:
                    logger.error("Function {} not found".format(function_path))
        return super().process(context, data)
