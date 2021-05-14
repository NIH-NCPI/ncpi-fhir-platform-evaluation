import pytest
import pdb
from fhir_walk.model.patient import Patient

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.2.13':<10} - CRUD Group"

test_weight = 2

# Cache the ID to simplify calls made after crate
example_group_id = None


def test_create_group(host, prep_server):
    global example_group_id

    example_group = prep_server['Common-Examples']['Group'][0]
    response = host.post('Group', example_group, validate_only=False)

    assert response['status_code'] == 201, 'CREATE success'
    example_group_id = response['response']['id']


def test_read_group(host, prep_server):
    global example_group_id

    example_group = prep_server['Common-Examples']['Group'][0]
    study_query = host.get(f"Group/{example_group_id}").entries
    assert len(study_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_group['identifier'][0]['value'] == study_query[0][
        'identifier'][0]['value'], 'Verify Identifier matches'
    assert example_group['code']['text'] == study_query[0]['code']['text']


def test_update_group(host, prep_server):
    global example_group_id

    example_group = prep_server['Common-Examples']['Group'][0]
    altered_study = example_group.copy()

    altered_study['type'] = 'device'
    altered_study['id'] = example_group_id
    result = host.update('Group', example_group_id, altered_study)
    assert result['status_code'] == 200

    study_qry = host.get(f"Group/{example_group_id}").entries
    assert len(study_qry) == 1, "READ success and only one was found"
    assert study_qry[0]['type'] == 'device'


def test_patch_group(host, prep_server):
    global example_group_id

    patch_ops = [{"op": "replace", "path": "/name", "value": "YANN"}]
    result = host.patch('Group', example_group_id, patch_ops)
    assert result['status_code'] == 200
    study_qry = result['response']
    assert study_qry['name'] == 'YANN'


def test_delete_group(host, prep_server):
    global example_group_id

    example_group = prep_server['Common-Examples']['Group'][0]
    example_identifier = example_group['identifier'][0]

    delete_result = host.delete_by_record_id('Group', example_group_id)
    assert delete_result['status_code'] == 200
    response = host.get(f"Group?identifier={example_identifier}").response
    del_query = unwrap_bundle(response)
    assert len(del_query) == 0, "Verify that the delete really worked"
