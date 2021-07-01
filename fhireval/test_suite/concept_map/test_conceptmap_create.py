import pytest
import pdb

from fhireval.test_suite.crud import prep_server
from copy import deepcopy

test_id = f"{'2.4.1':<10} - Create ConceptMap"

test_weight = 2

def test_conceptmap_create(host, prep_server):
    example_code_system_source = prep_server['CMG']['ConceptMap'][0]
    result = host.post('ConceptMap', example_code_system_source, validate_only=False)
    assert result['status_code'] == 201
    cm_id = result['response']['id']
    delete_result = host.delete_by_record_id('ConceptMap', cm_id)
    assert delete_result['status_code'] == 200




