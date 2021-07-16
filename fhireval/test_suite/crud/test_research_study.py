import pytest
import pdb
from fhir_walk.model.patient import Patient

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.2.01':<10} - CRUD Research Study "

test_weight = 2

# Cache the ID to simplify calls made after crate
example_study_id = None


def test_create_research_study(host, prep_server):
    global example_study_id

    example_study = prep_server['CMG']['ResearchStudy'][0]
    response = host.post('ResearchStudy', example_study, validate_only=False)

    assert response['status_code'] == 201, 'CREATE success'
    example_study_id = response['response']['id']


def test_read_research_study(host, prep_server):
    global example_study_id

    example_study = prep_server['CMG']['ResearchStudy'][0]
    study_query = host.get(f"ResearchStudy/{example_study_id}").entries
    assert len(study_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_study['identifier'][0]['value'] == study_query[0][
        'identifier'][0]['value'], 'Verify Identifier matches'
    assert example_study['title'] == study_query[0]['title']


def test_update_research_study(host, prep_server):
    global example_study_id

    example_study = prep_server['CMG']['ResearchStudy'][0]
    altered_study = example_study.copy()

    altered_study['title'] = 'New-Title'
    altered_study['id'] = example_study_id
    result = host.update('ResearchStudy', example_study_id, altered_study)
    assert result['status_code'] == 200

    study_qry = host.get(f"ResearchStudy/{example_study_id}").entries
    assert len(study_qry) == 1, "READ success and only one was found"
    assert study_qry[0]['title'] == 'New-Title'


def test_patch_research_study(host, prep_server):
    global example_study_id

    patch_ops = [{
        "op": "replace",
        "path": "/title",
        "value": "YANT - Yet Another New Title"
    }]
    result = host.patch('ResearchStudy', example_study_id, patch_ops)
    assert result['status_code'] == 200
    study_qry = result['response']
    assert study_qry['title'] == 'YANT - Yet Another New Title'


def test_delete_research_study(host, prep_server):
    global example_study_id

    example_study = prep_server['CMG']['ResearchStudy'][0]
    example_identifier = example_study['identifier'][0]

    delete_result = host.delete_by_record_id('ResearchStudy', example_study_id)
    assert delete_result['status_code'] == 200
    response = host.get(
        f"ResearchStudy?identifier={example_identifier}").response
    del_query = unwrap_bundle(response)
    assert len(del_query) == 0, "Verify that the delete really worked"
