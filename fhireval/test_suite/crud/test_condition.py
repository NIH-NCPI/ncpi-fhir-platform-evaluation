import pytest
import pdb

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server
import urllib.parse

test_id = f"{'2.2.08':10} - CRUD Condition"

test_weight = 2

example_patient_id = None
example_condition_id = None


def test_create_condition(host, prep_server):
    global example_patient_id, example_condition_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_condition = prep_server['CMG-Examples']['Condition'][0]
    response = host.post('Patient', example_patient, validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_patient_id = response['response']['id']

    # Gotta update the reference to make sense
    example_condition['subject']['reference'] = f"Patient/{example_patient_id}"
    response = host.post('Condition', example_condition, validate_only=False)

    assert response['status_code'] == 201, 'CREATE success'
    example_condition_id = response['response']['id']


def test_read_condition(host, prep_server):
    global example_patient_id, example_condition_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_condition = prep_server['CMG-Examples']['Condition'][0]

    study_query = host.get(f"Condition/{example_condition_id}").entries
    assert len(study_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_condition['identifier'][0]['value'] == study_query[0][
        'identifier'][0]['value'], 'Verify Identifier matches'


def test_update_condition(host, prep_server):
    global example_patient_id, example_condition_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_condition = prep_server['CMG-Examples']['Condition'][0]

    altered_condition = example_condition.copy()
    altered_condition['id'] = example_condition_id
    altered_condition['verificationStatus']['text'] = 'Probably Affected'
    result = host.update('Condition', example_condition_id, altered_condition)
    assert result['status_code'] == 200

    study_qry = host.get(f"Condition/{example_condition_id}").entries
    assert len(study_qry) == 1, "READ success and only one was found"
    assert study_qry[0]['verificationStatus']['text'] == 'Probably Affected'


def test_patch_condition(host, prep_server):
    global example_patient_id, example_condition_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]

    patch_ops = [{
        "op": "replace",
        "path": "/verificationStatus/text",
        "value": "Really Affected"
    }]

    result = host.patch('Condition', example_condition_id, patch_ops)
    assert result['status_code'] == 200
    study_qry = result['response']
    assert study_qry['verificationStatus']['text'] == 'Really Affected'


def test_delete_condition(host, prep_server):
    global example_patient_id, example_condition_id

    example_condition = prep_server['CMG-Examples']['Condition'][0]
    example_identifier = example_condition['identifier'][0]

    # So, for now, on google, get below fails because we have "|" in our identifiers. 
    # I don't think that changing anything here makes sense. Instead, we need to change how 
    # the identifiers are built 
    example_identifier = urllib.parse.quote(example_identifier['system'] + "|" + example_identifier['value'])

    delete_result = host.delete_by_record_id('Condition', example_condition_id)
    assert delete_result['status_code'] == 200
    response = host.get(f"Condition?identifier={example_identifier}").response
    del_query = unwrap_bundle(response)
    assert len(del_query) == 0, "Verify that the delete really worked"

    delete_result = host.delete_by_record_id('Patient', example_patient_id)
    assert delete_result['status_code'] == 200
