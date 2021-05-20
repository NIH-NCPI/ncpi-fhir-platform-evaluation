import pytest
import pdb
from fhireval.test_suite.concept_map import reset_testdata
from fhirwood.parameters import ConceptMapParameter
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.8.2':<10} - ConceptMap Translate"

test_weight = 2

def test_codemap_create(host, prep_server):
    reset_testdata(host, prep_server)
    example_code_system_source = prep_server['CMG']['ConceptMap'][0]
    result = host.post('ConceptMap', example_code_system_source, validate_only=False)
    assert result['status_code'] == 201
    cm_id = result['response']['id']

    # While we have a concept map in place, let's do a few checks
    translate_result = host.get(f"ConceptMap/$translate?system=http://hl7.org/fhir/administrative-gender&code=male", rec_count=-1).entries[0]
    match_result = ConceptMapParameter(translate_result)
    assert match_result.match_count > 0, "Make sure we have at least one result"
    assert match_result.result, "Make sure the first match is a postive"
    assert match_result.match.concept == "M", "Transpose actuall worked"
    delete_result = host.delete_by_record_id('ConceptMap', cm_id)
    assert delete_result['status_code'] == 200
