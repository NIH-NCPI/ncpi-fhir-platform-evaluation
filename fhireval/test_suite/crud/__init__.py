# The bullet points associated with this set of tests in the evaluation document
test_set_id = "2.5"

# User friendly name of the tests
test_set_name = "CRUD"

import pytest
from fhir_walk.model import unwrap_bundle

# This is the function that we'll use to grab the JSON files
from fhireval.data import load_test_data, delete_content_for_resource

import pdb

# Probably best for tests to log to this one so that they will all have the same entry
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def prep_server(host):
    # For the CRUD, we just need to make sure we delete any leftover data from
    # failed tests and then, in the teardown, we do it once again

    test_data = load_test_data()
    # We'll just walk through the _ALL for each resource type

    for resource, record in test_data["_ALL"].items():
        delete_content_for_resource(host, resource, record)

    yield test_data

    # And once again to clean up after this module completes
    for resource, record in test_data["_ALL"].items():
        delete_content_for_resource(host, resource, record)
