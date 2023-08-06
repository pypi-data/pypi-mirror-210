import logging
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from satosa.context import Context
from satosa.exception import SATOSAError
from satosa.internal import InternalData
from satosa.micro_services.base import ResponseMicroService
from pymongo import MongoClient
from satosa.response import Redirect

logger = logging.getLogger(__name__)


class IsBanned(ResponseMicroService):
    """
    This Satosa microservice checks, if user is banned.
    Banned users are redirected to configured URL.
    Requires perun user id to be already filled in the internal data.
    """

    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("IsBanned is active")

        self.user_id_attr = config["user_id_attr_name"]
        self.redirect_url = config["redirect_url"]
        self.connection_string = config["mongo_db"]["connection_string"]
        self.database_name = config["mongo_db"]["database_name"]
        self.collection_name = config["mongo_db"]["collection_name"]

    def process(self, context: Context, data: InternalData):
        """
        Redirects banned users to configured URL.

        @param context: request context
        @param data: the internal request
        """
        user_id = data.attributes.get(self.user_id_attr)
        if not user_id:
            raise SATOSAError(
                self.__class__.__name__ + f"Missing mandatory attribute "
                f"'{self.user_id_attr}' "
                f"in data.attributes. Hint: Did you "
                f"configured PerunUser microservice "
                f"before this microservice?"
            )

        if self.find_ban(str(user_id)) is not None:
            logger.info(f"Ban found for user {user_id}, redirecting to banned URL.")
            return Redirect(self.redirect_url)

        logger.debug(f"Ban not found for user {user_id}.")
        return super().process(context, data)

    def find_ban(self, user_id: str):
        """
        Searches for a ban in the database that is set for the user with given id.
        Returns ban if found, otherwise returns None.
        """
        try:
            client = MongoClient(self.connection_string)
            collection = client[self.database_name][self.collection_name]
            return collection.find_one({"userId": user_id})
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Ban database not reachable: {e}")
            raise SATOSAError("Failed to connect to the database.")
