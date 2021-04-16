import pytest
import pdb

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.5.06':10} - CRUD Observation"

test_weight = 2

example_observation_id = None
example_patient_id = None


def test_create_research_subject(host, prep_server):
    global example_observation_id, example_patient_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_observation = prep_server['eIII-Examples']['Observation'][0]

    response = host.post('Patient', example_patient, validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_patient_id = response['response']['id']

    example_observation['subject'][
        'reference'] = f"Patient/{example_patient_id}"
    response = host.post('Observation',
                         example_observation,
                         validate_only=False)
    assert response['status_code'] == 201, 'Observation CREATE success'
    example_observation_id = response['response']['id']


def test_read_research_subject(host, prep_server):
    global example_observation_id, example_patient_id
    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_observation = prep_server['eIII-Examples']['Observation'][0]

    obs_query = host.get(f"Observation/{example_observation_id}").entries
    assert len(obs_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_observation['valueQuantity']['value'] == obs_query[0][
        'valueQuantity']['value']


def test_update_research_subject(host, prep_server):
    global example_observation_id, example_patient_id
    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_observation = prep_server['eIII-Examples']['Observation'][0]

    altered_obs = example_observation.copy()
    altered_obs['valueQuantity']['value'] = 142
    altered_obs['id'] = example_observation_id
    result = host.update('Observation', example_observation_id, altered_obs)
    assert result['status_code'] == 200

    obs_qry = host.get(f"Observation/{example_observation_id}").entries
    assert len(obs_qry) == 1, "READ success and only one was found"
    assert obs_qry[0]['valueQuantity']['value'] == 142


def test_patch_research_subject(host, prep_server):
    global example_observation_id, example_patient_id

    patch_ops = [{
        "op": "replace",
        "path": "/valueQuantity/value",
        "value": 99
    }]
    result = host.patch('Observation', example_observation_id, patch_ops)
    assert result['status_code'] == 200
    obs_qry = result['response']
    assert obs_qry['valueQuantity']['value'] == 99


def test_delete_research_subject(host, prep_server):
    global example_observation_id, example_patient_id
    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_observation = prep_server['eIII-Examples']['Observation'][0]
    example_identifier = example_observation['identifier'][0]

    delete_result = host.delete_by_record_id('Observation',
                                             example_observation_id)
    assert delete_result['status_code'] == 200

    delete_result = host.delete_by_record_id('Patient', example_patient_id)
    assert delete_result['status_code'] == 200

    response = host.get(
        f"Observation?identifier={example_identifier}").response
    del_query = unwrap_bundle(response)
    assert len(del_query) == 0, "Verify that the delete really worked"
