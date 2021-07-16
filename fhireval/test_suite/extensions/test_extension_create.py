from fhireval.data import delete_from_response
from pprint import pformat
import pytest
import pdb
from fhireval.test_suite.crud import prep_server
test_id = f"{'2.5.1':<10} - Extension Creation"

test_weight = 2

_profile_url = None
_patient_id = None
_observation_id = None

def cleanup(host, prep_server):
    example_patient = prep_server['BasicTest']['Patient'][0]
    example_observation = prep_server['BasicTest']['Observation'][0]

    response = host.get(f"Observation?identifier={example_observation['identifier'][0]['value']}").entries
    for record in response:
        delete_from_response(host, 'Observation', record, sleep_til_gone=False)
    
    response = host.get(f"Patient?identifier={example_patient['identifier'][0]['value']}").entries
    for record in response:
        delete_from_response(host, 'Patient', record, sleep_til_gone=False)
    
    visit_extension = prep_server['BasicTest']['Extension'][0]
    response = host.get(f"StructureDefinition?url={visit_extension['url']}").entries

    for record in response:
        delete_from_response(host, 'StructureDefinition', record, sleep_til_gone=False)

    host.sleep_until(f"Patient?identifier={example_patient['identifier'][0]['value']}", 0)
    host.sleep_until(f"Observation?identifier={example_observation['identifier'][0]['value']}", 0)
    host.sleep_until(f"StructureDefinition?url={visit_extension['url']}", 0)


def test_extension_create(host, prep_server):
    global _profile_url
    visit_extension = prep_server['BasicTest']['Extension'][0]
    cleanup(host, prep_server)

    _profile_url = visit_extension['url']

    response = host.load("StructureDefinition", visit_extension)
    print(response['status_code'])
    print(pformat(response))

    assert(response['status_code']) == 201, f"Success create? {response['status_code']}"
    host.sleep_until(f"StructureDefinition?url={_profile_url}", 1)

def test_extension_validation(host, prep_server):
    global _patient_id, _observation_id
    example_patient = prep_server['BasicTest']['Patient'][0]
    example_observation = prep_server['BasicTest']['Observation'][0]

    response = host.post("Patient", example_patient)
    assert response['status_code'] == 201, "Patient create was successful"
    _patient_id = response['response']['id']
    example_observation['subject'][
        'reference'] = f"Patient/{_patient_id}"

    response = host.post("Observation", example_observation)
    assert response['status_code'] == 201, "Observation create was successful"
    _observation_id = response['response']['id']

def test_querying_for_extension(host, prep_server):
    global _profile_url
    entries = host.get(f"StructureDefinition?url={_profile_url}").entries
    assert len(entries) == 1, "Should be one extension"

