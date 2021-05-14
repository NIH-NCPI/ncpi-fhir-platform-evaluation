import pytest
import pdb

#from fhir_walk.model.patient import Patient

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.2.12':<10} - CRUD Task"

test_weight = 2

# Cache the ID to simplify calls made after crate
example_task_id = None
example_subject_id = None
example_patient_id = None
example_organization_id = None


def test_create_task(host, prep_server):
    global example_task_id, example_subject_id, example_patient_id, example_organization_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_subject = prep_server['CMG-Examples']['Specimen'][0]
    example_task = prep_server['Common-Examples']['Task'][0]
    example_org = prep_server['Common-Examples']['Organization'][0]

    response = host.post('Organization', example_org, validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_organization_id = response['response']['id']

    response = host.post('Patient', example_patient, validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_patient_id = response['response']['id']

    # We have to do some tweaking to the references used by Task
    example_subject['subject']['reference'] = f"Patient/{example_patient_id}"
    response = host.post('Specimen', example_subject, validate_only=False)
    assert response['status_code'] == 201, 'Subject CREATE success'
    example_subject_id = response['response']['id']

    example_task['for']['reference'] = f"Patient/{example_patient_id}"
    example_task['requester'][
        'reference'] = f"Organization/{example_organization_id}"
    example_task['output'][0]['valueReference'][
        'reference'] = f"Specimen/{example_subject_id}"

    response = host.post('Task', example_task, validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_task_id = response['response']['id']


def test_read_task(host, prep_server):
    global example_task_id, example_subject_id, example_patient_id, example_organization_id
    example_task = prep_server['Common-Examples']['Task'][0]

    task_query = host.get(f"Task/{example_task_id}").entries
    assert len(task_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_task['identifier'][0]['value'] == task_query[0][
        'identifier'][0]['value'], 'Verify Identifier matches'
    assert example_task['status'] == task_query[0]['status']
    assert task_query[0]['status'] != 'requested'


def test_update_task(host, prep_server):
    global example_task_id, example_subject_id, example_patient_id, example_organization_id
    example_task = prep_server['Common-Examples']['Task'][0]

    altered_task = example_task.copy()
    altered_task['groupIdentifier']['value'] = 'new-identifier'
    altered_task['id'] = example_task_id
    result = host.update('Task', example_task_id, altered_task)
    assert result['status_code'] == 200

    task_qry = host.get(f"Task/{example_task_id}").entries
    assert len(task_qry) == 1, "READ success and only one was found"
    assert task_qry[0]['groupIdentifier']['value'] == 'new-identifier'


def test_patch_task(host, prep_server):
    global example_task_id, example_subject_id, example_patient_id, example_organization_id
    example_task = prep_server['Common-Examples']['Task'][0]

    patch_ops = [{"op": "replace", "path": "/status", "value": "requested"}]
    result = host.patch('Task', example_task_id, patch_ops)
    #pdb.set_trace()
    assert result['status_code'] == 200
    task_qry = result['response']
    assert task_qry['status'] == 'requested'


def test_delete_task(host, prep_server):
    global example_task_id, example_subject_id, example_patient_id, example_organization_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_subject = prep_server['CMG-Examples']['Specimen'][0]
    example_task = prep_server['Common-Examples']['Task'][0]
    example_org = prep_server['Common-Examples']['Organization'][0]

    delete_result = host.delete_by_record_id('Task', example_task_id)
    assert delete_result['status_code'] == 200

    delete_result = host.delete_by_record_id('Specimen', example_subject_id)
    assert delete_result['status_code'] == 200

    delete_result = host.delete_by_record_id('Organization',
                                             example_organization_id)
    assert delete_result['status_code'] == 200

    delete_result = host.delete_by_record_id('Patient', example_patient_id)
    assert delete_result['status_code'] == 200
