from unittest.mock import MagicMock
import logging

from satosa.micro_services.base import MicroService
from satosa.response import Redirect
from satosacontrib.perun.micro_services.is_banned_microservice import (
    IsBanned,
)
from tests.test_microservice_loader import Loader, TestContext, TestData

CONFIG = {
    "user_id_attr_name": "user_id",
    "redirect_url": "https://example.org/banned.html",
    "mongo_db": {
        "connection_string": "connection_string",
        "database_name": "database_name",
        "collection_name": "bans",
    },
}

BAN = {
    "description": None,
    "facilityId": "4514",
    "id": 6,
    "userId": "1",
    "validityTo": "1680134400000",
}

MICROSERVICE = Loader(CONFIG, IsBanned.__name__).create_mocked_instance()


def test_banned_user_is_redirected(caplog):
    data = {"user_id": 1}
    expected_header = (
        "Location",
        CONFIG["redirect_url"],
    )
    ban_found_message = "Ban found for user 1, redirecting to banned URL."

    IsBanned.find_ban = MagicMock(return_value=BAN)
    MicroService.process = MagicMock(return_value=None)

    with caplog.at_level(logging.INFO):
        result = MICROSERVICE.process(TestContext(), TestData({}, data))

        assert isinstance(result, Redirect)
        assert expected_header in result.headers
        assert ban_found_message in caplog.text


def test_banned_user_ok(caplog):
    data = {"user_id": 1}
    ban_not_found_log_message = "Ban not found for user 1."

    IsBanned.find_ban = MagicMock(return_value=None)
    MicroService.process = MagicMock(return_value=None)

    with caplog.at_level(logging.DEBUG):
        MICROSERVICE.process(TestContext(), TestData({}, data))

        assert ban_not_found_log_message in caplog.text
        MicroService.process.assert_called()
