import pytest
import pdb

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.2.04':<10} - CRUD Organization "

test_weight = 2

# Cache the ID to simplify calls made after crate
example_organization_id = None


def test_create_research_study(host, prep_server):
    global example_organization_id

    example_org = prep_server['CMG-Examples']['Organization'][0]
    response = host.post('Organization', example_org, validate_only=False)

    assert response['status_code'] == 201, 'CREATE success'
    example_organization_id = response['response']['id']


def test_read_research_study(host, prep_server):
    global example_organization_id

    example_org = prep_server['CMG-Examples']['Organization'][0]
    study_query = host.get(f"Organization/{example_organization_id}").entries
    assert len(study_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_org['name'] == study_query[0]['name'], 'Verify Name matches'


def test_update_research_study(host, prep_server):
    global example_organization_id

    example_org = prep_server['CMG-Examples']['Organization'][0]
    altered_study = example_org.copy()

    altered_study['name'] = 'New_Name'
    altered_study['id'] = example_organization_id
    result = host.update('Organization', example_organization_id,
                         altered_study)
    assert result['status_code'] == 200

    study_qry = host.get(f"Organization/{example_organization_id}").entries
    assert len(study_qry) == 1, "READ success and only one was found"
    assert study_qry[0]['name'] == 'New_Name'


def test_patch_research_study(host, prep_server):
    global example_organization_id

    patch_ops = [{
        "op": "replace",
        "path": "/name",
        "value": "YANN - Yet Another New Name"
    }]
    result = host.patch('Organization', example_organization_id, patch_ops)
    assert result['status_code'] == 200
    study_qry = result['response']
    assert study_qry['name'] == 'YANN - Yet Another New Name'


def test_delete_research_study(host, prep_server):
    global example_organization_id

    example_org = prep_server['CMG-Examples']['Organization'][0]
    example_identifier = example_org['identifier'][0]

    delete_result = host.delete_by_record_id('Organization',
                                             example_organization_id)
    assert delete_result['status_code'] == 200
    response = host.get(
        f"Organization?identifier={example_identifier}").response
    del_query = unwrap_bundle(response)
    assert len(del_query) == 0, "Verify that the delete really worked"
