import pytest
import pdb

from fhir_walk.model.patient import Patient

from fhir_walk.model import unwrap_bundle

from fhireval.test_suite.crud import prep_server
import fhireval.test_suite.crud

test_id = f"{'2.5.02':<10} - CRUD Patient"

test_weight = 2

# Just an id cache to more easily recall the record we are working with across tests
example_patient_id = None


def test_patient_create(host, prep_server):
    global example_patient_id
    # Test CREATE
    example_patient = prep_server["CMG-Examples"]["Patient"][0]
    response = host.post("Patient", example_patient, validate_only=False)

    # The Patient was created above so we just need to check the return code
    assert response["status_code"] == 201, "CREATE Success"
    example_patient_id = response["response"]["id"]


def test_patient_read(host, prep_server):
    global example_patient_id
    # Test READ
    example_patient = prep_server["CMG-Examples"]["Patient"][0]
    patient_query = host.get(f"Patient/{example_patient_id}").entries
    assert len(patient_query) == 1, "READ Success and only one was found"
    patient = Patient(host, patient_query[0])

    # I'm just testing a couple of values from the patient object based on
    # the patient in crud.example_patient. These values will probably change
    # once we settle on some simulated data
    assert (patient.subject_id == example_patient["identifier"][0]["value"]
            ), "READ Verify Subject ID"
    assert patient.eth == "Hispanic or Latino", "READ Verify Ethnicity"
    assert patient.sex == "male"


def test_patient_update(host, prep_server):
    global example_patient_id
    # Test UPDATE
    example_patient = prep_server["CMG-Examples"]["Patient"][0]

    altered_patient = example_patient.copy()
    altered_patient["id"] = example_patient_id
    altered_patient["gender"] = "female"

    for extnsn in altered_patient["extension"]:
        if "valueAge" in extnsn:
            extnsn["valueAge"]["value"] = 50.0

    result = host.update("Patient", example_patient_id, altered_patient)
    assert result["status_code"] == 200

    patient_query = host.get(f"Patient/{example_patient_id}").entries
    assert len(patient_query) == 1, "READ Success and only one was found"
    patient = Patient(host, patient_query[0])

    assert patient.sex == "female"


def test_patient_patch(host, prep_server):
    global example_patient_id
    # Test PATCH
    example_patient = prep_server["CMG-Examples"]["Patient"][0]

    # Super simple for purposes of example. Let's set the sex back to female
    patch_ops = [{"op": "add", "path": "/gender", "value": "male"}]
    result = host.patch("Patient", example_patient_id, patch_ops)
    assert result["status_code"] == 200
    patient_query = result["response"]
    patient = Patient(host, patient_query)
    assert patient.sex == "male"


def test_patient_delete(host, prep_server):
    global example_patient_id
    # Test Delete
    example_patient = prep_server["CMG-Examples"]["Patient"][0]
    example_identifier = example_patient["identifier"][0]

    delete_result = host.delete_by_record_id("Patient", example_patient_id)
    assert delete_result["status_code"] == 200
    response = host.get(f"Patient?identifier={example_identifier}").response
    patient_query = unwrap_bundle(response)
    assert len(
        patient_query) == 0, "Verify that delete really deleted the record"
