import pytest

from fhir_walk.config import DataConfig
from fhir_walk.fhir_host import FhirHost

@pytest.fixture
def config():
    return DataConfig.config()

@pytest.fixture
def host(config):
    return config.get_host()