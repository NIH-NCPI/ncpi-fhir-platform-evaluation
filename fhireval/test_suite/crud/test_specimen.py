import pytest
import pdb

from fhireval.test_suite.crud import prep_server
from fhir_walk.model import unwrap_bundle

test_id = f"{'2.5.05':10} - CRUD Specimen"

test_weight = 2

example_patient_id = None
example_specimen_id = None


def test_create_specimen(host, prep_server):
    global example_patient_id, example_specimen_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_specimen = prep_server['CMG-Examples']['Specimen'][0]
    response = host.post('Patient', example_patient, validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_patient_id = response['response']['id']

    # Gotta update the reference to make sense
    example_specimen['subject']['reference'] = f"Patient/{example_patient_id}"
    response = host.post('Specimen', example_specimen, validate_only=False)

    assert response['status_code'] == 201, 'CREATE success'
    example_specimen_id = response['response']['id']


def test_read_specimen(host, prep_server):
    global example_patient_id, example_specimen_id

    example_specimen = prep_server['CMG-Examples']['Specimen'][0]

    study_query = host.get(f"Specimen/{example_specimen_id}").entries
    assert len(study_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_specimen['identifier'][0]['value'] == study_query[0][
        'identifier'][0]['value'], 'Verify Identifier matches'


def test_update_specimen(host, prep_server):
    global example_patient_id, example_specimen_id

    example_specimen = prep_server['CMG-Examples']['Specimen'][0]

    altered_specimen = example_specimen.copy()
    altered_specimen['identifier'][1]['value'] = 'new-identifier'
    altered_specimen['id'] = example_specimen_id
    result = host.update('Specimen', example_specimen_id, altered_specimen)
    assert result['status_code'] == 200

    study_qry = host.get(f"Specimen/{example_specimen_id}").entries
    assert len(study_qry) == 1, "READ success and only one was found"
    assert study_qry[0]['identifier'][1]['value'] == 'new-identifier'


def test_patch_specimen(host, prep_server):
    global example_patient_id, example_specimen_id

    patch_ops = [{"op": "add", "path": "/status", "value": "entered-in-error"}]

    result = host.patch('Specimen', example_specimen_id, patch_ops)
    assert result['status_code'] == 200
    study_qry = result['response']
    assert study_qry['status'] == 'entered-in-error'


def test_delete_specimen(host, prep_server):
    global example_patient_id, example_specimen_id

    example_specimen = prep_server['CMG-Examples']['Specimen'][0]
    example_identifier = example_specimen['identifier'][0]

    delete_result = host.delete_by_record_id('Specimen', example_specimen_id)
    assert delete_result['status_code'] == 200
    response = host.get(f"Specimen?identifier={example_identifier}").response
    del_query = unwrap_bundle(response)
    assert len(del_query) == 0, "Verify that the delete really worked"

    delete_result = host.delete_by_record_id('Patient', example_patient_id)
    assert delete_result['status_code'] == 200
