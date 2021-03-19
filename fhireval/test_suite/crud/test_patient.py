import pytest
import pdb

from fhir_walk.model.patient import Patient

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import create_patient, reset_crud_test_data, example_patient
test_id = f"{'2.5.2':<10} - CRUD Patient"

test_weight = 2

# Just an id cache to more easily recall the record we are working with across tests
example_patient_id = None

def test_patient_create(host):
    # Test CREATE
    # Capture the id in case this test runs first
    global example_patient_id
    # We'll make sure that any possible left-overs from previous tests 
    # don't make it look like our tests are passing when they did not
    reset_crud_test_data(host)

    # Create the patient and verify that the return code marked a success
    patient_create = create_patient(host)
    assert patient_create['status_code'] == 201, "CREATE Success"
    example_patient_id = patient_create['response']['id']

def test_patient_read(host):
    # Test READ
    patient_query = host.get(f"Patient/{example_patient_id}").entries
    assert len(patient_query) == 1, "READ Success and only one was found"
    patient = Patient(host, patient_query[0])

    # I'm just testing a couple of values from the patient object based on 
    # the patient in crud.example_patient. These values will probably change
    # once we settle on some simulated data
    assert patient.subject_id == 'ctpatient01', "READ Verify Subject ID"
    assert patient.eth == 'Hispanic or Latino', "READ Verify Ethnicity"
    assert patient.sex == 'male'

def test_patient_update(host):
    # Test UPDATE
    altered_patient = example_patient.copy()
    altered_patient['id'] = example_patient_id
    altered_patient['gender'] = 'female'

    for extnsn in altered_patient['extension']:
        if 'valueAge' in extnsn:
            extnsn['valueAge']['value'] = 50.0

    result = host.update('Patient', example_patient_id,altered_patient)
    assert result['status_code'] == 200

    patient_query = host.get(f"Patient/{example_patient_id}").entries
    assert len(patient_query) == 1, "READ Success and only one was found"
    patient = Patient(host, patient_query[0])

    assert patient.sex == 'female'

def test_patient_patch(host):
    # Super simple for purposes of example. Let's set the sex back to female
    patch_ops = [{
        "op": "add",
        "path": "/gender",
        "value": "male"
        }]
    result = host.patch('Patient', example_patient_id, patch_ops)
    assert result['status_code'] == 200
    patient_query = result['response']
    patient = Patient(host, patient_query)
    assert patient.sex == 'male'

def test_patient_delete(host):
    # Test Delete
    delete_result = host.delete_by_record_id('Patient', example_patient_id)
    assert delete_result['status_code'] == 200
    response = host.get(f"Patient?identifier={example_patient_id}").response
    patient_query = unwrap_bundle(response)
    assert len(patient_query) == 0, "Verify that delete really deleted the record"






