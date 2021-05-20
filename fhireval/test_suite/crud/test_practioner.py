import pytest
import pdb
from fhir_walk.model.patient import Patient

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.2.09':<10} - CRUD Research practitioner "

test_weight = 2

# Cache the ID to simplify calls made after crate
example_practitioner_id = None


def test_create_research_practitioner(host, prep_server):
    global example_practitioner_id

    print(prep_server['CMG']['Practitioner'])
    example_practitioner = prep_server['CMG']['Practitioner'][0]
    response = host.post('Practitioner',
                         example_practitioner,
                         validate_only=False)

    assert response['status_code'] == 201, 'CREATE success'
    example_practitioner_id = response['response']['id']


def test_read_research_practitioner(host, prep_server):
    global example_practitioner_id

    example_practitioner = prep_server['CMG']['Practitioner'][0]
    practitioner_query = host.get(
        f"Practitioner/{example_practitioner_id}").entries
    assert len(practitioner_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_practitioner['name'][0]['text'] == practitioner_query[0][
        'name'][0]['text'], 'Verify name matches'
    assert example_practitioner['gender'] == 'female'


def test_update_research_practitioner(host, prep_server):
    global example_practitioner_id

    example_practitioner = prep_server['CMG']['Practitioner'][0]
    altered_practitioner = example_practitioner.copy()

    altered_practitioner['telecom'][0]['value'] = '(123) 456-7890'
    altered_practitioner['id'] = example_practitioner_id
    result = host.update('Practitioner', example_practitioner_id,
                         altered_practitioner)
    assert result['status_code'] == 200

    practitioner_qry = host.get(
        f"Practitioner/{example_practitioner_id}").entries
    assert len(practitioner_qry) == 1, "READ success and only one was found"
    print(practitioner_qry)
    assert practitioner_qry[0]['telecom'][0]['value'] == '(123) 456-7890'


def test_patch_research_practitioner(host, prep_server):
    global example_practitioner_id

    patch_ops = [{"op": "replace", "path": "/gender", "value": "male"}]
    result = host.patch('Practitioner', example_practitioner_id, patch_ops)
    assert result['status_code'] == 200
    practitioner_qry = result['response']
    assert practitioner_qry['gender'] == 'male'


def test_delete_research_practitioner(host, prep_server):
    global example_practitioner_id

    example_practitioner = prep_server['CMG']['Practitioner'][0]
    example_identifier = example_practitioner['name'][0]['text']

    delete_result = host.delete_by_record_id('Practitioner',
                                             example_practitioner_id)
    assert delete_result['status_code'] == 200
    response = host.get(f"Practitioner?name={example_identifier}").response
    del_query = unwrap_bundle(response)
    assert len(del_query) == 0, "Verify that the delete really worked"
