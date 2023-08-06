import logging

from satosa.micro_services.base import ResponseMicroService

logger = logging.getLogger(__name__)


class ContextAttributes(ResponseMicroService):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("ContextAttributes is active")
        self.__federations = config.get("federations", [])
        self.__federation_backends = config.get("federation_backends", [])
        self.__allowed_requesters = config.get("allowed_requesters", None)
        self.__target_backend_attribute = config.get(
            "target_backend_attribute", "targetbackend"
        )
        self.__target_issuer_attributes = config.get(
            "target_issuer_attributes", ["targetissuer"]
        )

    def process(self, context, data):
        """
        Add target IdP data to attributes.
        :param context: request context
        :param data: the internal request
        """
        logger.info("context attributes is active")
        if (
            self.__allowed_requesters is None
            or data.requester in self.__allowed_requesters
        ):
            logger.info("Generating backend attributes for {}".format(data.requester))
            idp = data.auth_info.issuer
            if not data.to_dict().get("metadata", None):
                logger.error("No metadata attribute found")
                return super().process(context, data)
            if not data.to_dict().get("metadata").get(idp, None):
                logger.error("No metadata found for {}".format(idp))
                return super().process(context, data)
            idp_md = data.metadata[idp]
            data.attributes[self.__target_backend_attribute] = {
                "display_name": idp_md.get("display_names", None),
                "logo": idp_md.get("logo", None),
            }
            for target_issuer_attribute in self.__target_issuer_attributes:
                data.attributes[target_issuer_attribute] = data["auth_info"]["issuer"]
        else:
            logger.info("Skipping backend attributes for {}".format(data.requester))

        return super().process(context, data)
