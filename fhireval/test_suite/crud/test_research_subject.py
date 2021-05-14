import pytest
import pdb

#from fhir_walk.model.patient import Patient

from fhir_walk.model import unwrap_bundle
from fhireval.test_suite.crud import prep_server

test_id = f"{'2.2.03':<10} - CRUD Research Subject"

test_weight = 2

# Cache the ID to simplify calls made after crate
example_study_id = None
example_subject_id = None
example_patient_id = None


def test_create_research_subject(host, prep_server):
    global example_study_id, example_subject_id, example_patient_id

    example_patient = prep_server['CMG-Examples']['Patient'][0]
    example_study = prep_server['CMG-Examples']['ResearchStudy'][0]
    example_subject = prep_server['CMG-Examples']['ResearchSubject'][0]

    response = host.post('ResearchStudy', example_study, validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_study_id = response['response']['id']

    response = host.post('Patient', example_patient, validate_only=False)
    assert response['status_code'] == 201, 'CREATE success'
    example_patient_id = response['response']['id']

    # We have to do some tweaking to the references used by ResearchSubject
    example_subject['study']['reference'] = f"ResearchStudy/{example_study_id}"
    example_subject['individual'][
        'reference'] = f"Patient/{example_patient_id}"

    response = host.post('ResearchSubject',
                         example_subject,
                         validate_only=False)
    assert response['status_code'] == 201, 'Subject CREATE success'
    example_subject_id = response['response']['id']


def test_read_research_subject(host, prep_server):
    global example_study_id, example_subject_id, example_patient_id

    example_subject = prep_server['CMG-Examples']['ResearchSubject'][0]
    study_query = host.get(f"ResearchSubject/{example_subject_id}").entries
    assert len(study_query) == 1, "READ Success and only one was found"

    # Just make sure we got what we expected
    assert example_subject['identifier'][0]['value'] == study_query[0][
        'identifier'][0]['value'], 'Verify Identifier matches'


def test_update_research_subject(host, prep_server):
    global example_study_id, example_subject_id, example_patient_id

    example_subject = prep_server['CMG-Examples']['ResearchSubject'][0]

    altered_subject = example_subject.copy()
    altered_subject['identifier'][1]['value'] = 'new-identifier-nine'
    altered_subject['id'] = example_subject_id
    result = host.update('ResearchSubject', example_subject_id,
                         altered_subject)
    assert result['status_code'] == 200

    study_qry = host.get(f"ResearchSubject/{example_subject_id}").entries
    assert len(study_qry) == 1, "READ success and only one was found"
    assert study_qry[0]['identifier'][1]['value'] == 'new-identifier-nine'


def test_patch_research_subject(host, prep_server):
    global example_study_id, example_subject_id, example_patient_id

    patch_ops = [{"op": "replace", "path": "/status", "value": "off-study"}]
    result = host.patch('ResearchSubject', example_subject_id, patch_ops)
    assert result['status_code'] == 200
    study_qry = result['response']
    assert study_qry['status'] == 'off-study'


def test_delete_research_subject(host, prep_server):
    global example_study_id, example_subject_id, example_patient_id

    example_subject = prep_server['CMG-Examples']['ResearchSubject'][0]
    example_identifier = example_subject['identifier'][0]

    example_study = prep_server['CMG-Examples']['ResearchStudy'][0]
    example_identifier = example_study['identifier'][0]

    delete_result = host.delete_by_record_id('ResearchSubject',
                                             example_subject_id)
    assert delete_result['status_code'] == 200

    delete_result = host.delete_by_record_id('Patient', example_patient_id)
    assert delete_result['status_code'] == 200

    delete_result = host.delete_by_record_id('ResearchStudy', example_study_id)
    assert delete_result['status_code'] == 200

    response = host.get(
        f"ResearchSubject?identifier={example_identifier}").response
    del_query = unwrap_bundle(response)
    assert len(del_query) == 0, "Verify that the delete really worked"
