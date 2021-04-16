import pytest
import pdb

#from fhir_walk.model.organization import organization

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.5.10':<10} - CRUD PractionerRole"

test_weight = 2

# Cache the ID to simplify calls made after crate
example_practitioner_id = None
example_practitioner_role_id = None
example_organization_id = None


def test_create_research_practitioner_role(host, prep_server):
    global example_practitioner_id, example_practitioner_role_id, example_organization_id

    example_organization = prep_server['Common-Examples']['Organization'][0]
    example_practitioner = prep_server['Common-Examples']['Practitioner'][0]
    example_practitioner_role = prep_server['Common-Examples'][
        'PractitionerRole'][0]

    response = host.post('Practitioner',
                         example_practitioner,
                         validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_practitioner_id = response['response']['id']

    response = host.post('Organization',
                         example_organization,
                         validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_organization_id = response['response']['id']

    # We have to do some tweaking to the references used by Practitioner_role
    example_practitioner_role['practitioner'][
        'reference'] = f"Practitioner/{example_practitioner_id}"
    example_practitioner_role['organization'][
        'reference'] = f"Organization/{example_organization_id}"

    response = host.post('PractitionerRole',
                         example_practitioner_role,
                         validate_only=False)
    assert response['status_code'] == 201, 'PractitionerRole CREATE success'
    example_practitioner_role_id = response['response']['id']


def test_read_research_practitioner_role(host, prep_server):
    global example_practitioner_id, example_practitioner_role_id, example_organization_id

    example_practitioner_role = prep_server['Common-Examples'][
        'PractitionerRole'][0]
    practitioner_query = host.get(
        f"PractitionerRole/{example_practitioner_role_id}").entries
    assert len(practitioner_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_practitioner_role['code'][0]['coding'][0][
        'display'] == practitioner_query[0]['code'][0]['coding'][0][
            'display'], 'Verify Code matches'
    assert example_practitioner_role[
        'active'], "Make sure that active is true so we can patch-change it"


def test_update_research_practitioner_role(host, prep_server):
    global example_practitioner_id, example_practitioner_role_id, example_organization_id

    example_practitioner_role = prep_server['Common-Examples'][
        'PractitionerRole'][0]

    altered_practitioner_role = example_practitioner_role.copy()
    altered_practitioner_role['code'][0]['coding'][0][
        'display'] = 'Research Investigator Person'
    altered_practitioner_role['id'] = example_practitioner_role_id
    result = host.update('PractitionerRole', example_practitioner_role_id,
                         altered_practitioner_role)
    assert result['status_code'] == 200

    practitioner_qry = host.get(
        f"PractitionerRole/{example_practitioner_role_id}").entries
    assert len(practitioner_qry) == 1, "READ success and only one was found"
    assert practitioner_qry[0]['code'][0]['coding'][0][
        'display'] == 'Research Investigator Person'


def test_patch_research_practitioner_role(host, prep_server):
    global example_practitioner_id, example_practitioner_role_id, example_organization_id

    patch_ops = [{"op": "replace", "path": "/active", "value": False}]
    result = host.patch('PractitionerRole', example_practitioner_role_id,
                        patch_ops)
    assert result['status_code'] == 200
    practitioner_qry = result['response']
    assert not practitioner_qry['active']


def test_delete_research_practitioner_role(host, prep_server):
    global example_practitioner_id, example_practitioner_role_id, example_organization_id

    delete_result = host.delete_by_record_id('PractitionerRole',
                                             example_practitioner_role_id)
    assert delete_result['status_code'] == 200

    delete_result = host.delete_by_record_id('Practitioner',
                                             example_practitioner_id)
    assert delete_result['status_code'] == 200

    delete_result = host.delete_by_record_id('Organization',
                                             example_organization_id)
    assert delete_result['status_code'] == 200
