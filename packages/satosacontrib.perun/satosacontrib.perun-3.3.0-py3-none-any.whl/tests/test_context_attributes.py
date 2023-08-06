import logging
from unittest.mock import MagicMock

from satosa.context import Context
from satosa.internal import InternalData
from satosa.micro_services.base import MicroService

from tests.test_microservice_loader import Loader

MICROSERVICE_CONFIG = {
    "global_cfg_filepath": "example_path",
    "federations": ["federation1", "federation2"],
    "federation_backends": ["federation_backend1", "federation_backend2"],
    "allowed_requesters": ["allowed_requester1", "allowed_requester2"],
    "target_backend_attribute": "targetbackend",
    "target_issuer_attributes": ["targetissuer"],
}

MICROSERVICE = Loader(MICROSERVICE_CONFIG, "ContextAttributes").create_mocked_instance()


def test_process_requester_not_allowed(caplog):
    data_with_disallowed_requester = InternalData()
    data_with_disallowed_requester.requester = "not_allowed_req"
    skipping_attributes_message = "Skipping backend attributes for not_allowed_req"
    MicroService.process = MagicMock(return_value=None)
    with caplog.at_level(logging.INFO):
        MICROSERVICE.process(Context(), data_with_disallowed_requester)
        assert skipping_attributes_message in caplog.text
        MicroService.process.assert_called()


def test_missing_metadata_attr(caplog):
    data = InternalData()
    data.requester = "allowed_requester1"
    data.auth_info.issuer = "example_issuer"
    missing_metadata_message = "No metadata attribute found"
    MicroService.process = MagicMock(return_value=None)
    with caplog.at_level(logging.ERROR):
        MICROSERVICE.process(Context(), data)
        assert missing_metadata_message in caplog.text
        MicroService.process.assert_called()


def test_missing_idp_metadata(caplog):
    data = InternalData()
    data.requester = "allowed_requester1"
    data.auth_info.issuer = "not_in_md_issuer"
    data.metadata = {
        "example_issuer": {
            "display_name": "Example idp",
            "logo": "https://logo.com/logo.png",
        }
    }
    missing_metadata_message = "No metadata found for not_in_md_issuer"
    MicroService.process = MagicMock(return_value=None)
    with caplog.at_level(logging.ERROR):
        MICROSERVICE.process(Context(), data)
        assert missing_metadata_message in caplog.text
        MicroService.process.assert_called()


def test_collect_context_attributes(caplog):
    data = InternalData()
    data.requester = "allowed_requester1"
    data.auth_info.issuer = "example_issuer"
    data.metadata = {
        "example_issuer": {
            "display_name": "Example idp",
            "display_names": [{"text": "Google", "lang": "en"}],
            "logo": "https://logo.com/logo.png",
        }
    }
    context = Context()
    context.target_backend = "federation_backend1"
    generating_attributes_message = (
        "Generating backend attributes for allowed_requester1"
    )
    MicroService.process = MagicMock(return_value=None)
    with caplog.at_level(logging.INFO):
        MICROSERVICE.process(context, data)
        assert generating_attributes_message in caplog.text
        assert data.attributes["targetbackend"].get("display_name") == data.metadata[
            "example_issuer"
        ].get("display_names")
        assert data.attributes["targetbackend"].get("logo") == data.metadata[
            "example_issuer"
        ].get("logo")
        assert data.attributes["targetissuer"] == data.auth_info.issuer
        MicroService.process.assert_called()
