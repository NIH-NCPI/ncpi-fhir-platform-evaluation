import pytest
import pdb

from fhireval.test_suite.crud import prep_server

test_id = f"{'2.2.11':<10} - CRUD Document Reference"

test_weight = 2

# Cache the ID to simplify calls made after crate
example_document_ref_id = None


def test_create_research_document_ref(host, prep_server):
    global example_document_ref_id

    # pdb.set_trace()
    example_patient = prep_server['CMG']['Patient'][0]
    response = host.post('Patient', example_patient, validate_only=False)
    example_patient_id = response['response']['id']

    example_org = prep_server['CMG']['Organization'][0]
    response = host.post('Organization', example_org, validate_only=False)

    assert response['status_code'] == 201, 'CREATE success'
    example_organization_id = response['response']['id']

    example_document_ref = prep_server['CMG']['DocumentReference'][0]
    example_document_ref['subject'][
        'reference'] = f"Patient/{example_patient_id}"
    example_document_ref['author'][0]['reference'] = f"Organization/{example_organization_id}"
    response = host.post('DocumentReference', example_document_ref, validate_only=False)

    assert response['status_code'] == 201, 'CREATE success'
    example_document_ref_id = response['response']['id']


def test_read_research_document_ref(host, prep_server):
    global example_document_ref_id

    example_document_ref = prep_server['CMG']['DocumentReference'][0]

    document_ref_query = host.get(f"DocumentReference/{example_document_ref_id}").entries
    assert len(document_ref_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_document_ref['status'] == document_ref_query[0]['status'], 'Verify Identifier matches'
    #pdb.set_trace()
    assert example_document_ref['content'][0]['attachment']['title'] == document_ref_query[0]['content'][0]['attachment'][
        'title']


def test_update_research_document_ref(host, prep_server):
    global example_document_ref_id

    example_document_ref = prep_server['CMG']['DocumentReference'][0]
    altered_document_ref = example_document_ref.copy()

    altered_document_ref['content'][0]['attachment']['url'] = 'drs:example.com/12/23/45'
    altered_document_ref['id'] = example_document_ref_id
    result = host.update('DocumentReference', example_document_ref_id, altered_document_ref)
    assert result['status_code'] == 200

    document_ref_qry = host.get(f"DocumentReference/{example_document_ref_id}").entries
    assert len(document_ref_qry) == 1, "READ success and only one was found"
    assert document_ref_qry[0]['content'][0]['attachment']['url'] == 'drs:example.com/12/23/45'


def test_patch_research_document_ref(host, prep_server):
    global example_document_ref_id
    example_document_ref = prep_server['CMG']['DocumentReference'][0]

    patch_ops = [{"op": "replace", "path": "/status", "value": "superseded"}]
    result = host.patch('DocumentReference', example_document_ref_id, patch_ops)
    assert result['status_code'] == 200
    document_ref_qry = result['response']
    assert document_ref_qry['status'] == 'superseded'


def test_delete_research_document_ref(host, prep_server):
    global example_document_ref_id

    example_document_ref = prep_server['CMG']['DocumentReference'][0]

    delete_result = host.delete_by_record_id('DocumentReference', example_document_ref_id)
    assert delete_result['status_code'] == 200
