import pytest
import pdb

from fhireval.test_suite.concept_map import example_code_system_source, reset_testdata

test_id = f"{'2.8.1':<10} - Create ConceptMap"

test_weight = 2

def test_codemap_create(host):
    reset_testdata(host)
    result = host.post('ConceptMap', example_code_system_source, validate_only=False)
    assert result['status_code'] == 201
    cm_id = result['response']['id']
    delete_result = host.delete_by_record_id('ConceptMap', cm_id)
    assert delete_result['status_code'] == 200




