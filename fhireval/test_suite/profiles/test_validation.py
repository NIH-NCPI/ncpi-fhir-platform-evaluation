import pytest

from pprint import pformat
import pdb
import copy

from fhireval.test_suite.crud import prep_server
test_id = f"{'2.3.1':<10} - Profile Validation"

test_weight = 25

def test_validation_against(host, prep_server):
    # Our profile should still exist, so we are going to try to submit something
    # that should fail (meaningless terminology for a phenotype should work)
    """
    for term in prep_server['NCPI-Model']['CodeSystem']:
        host.load('CodeSystem', term)
    for term in prep_server['NCPI-Model']['ValueSet']:
        host.load('ValueSet', term)
    """
    profiles = prep_server['NCPI-Model']['StructureDefinition']
    phenotype = None
    for profile in profiles:
        print(profile['name'])
        if profile['name'] == 'Phenotype':
            phenotype = profile
            break

    assert phenotype is not None, "Make sure there is a Phenotype profile to test"
    profile_url = phenotype['url']
    print(f"Profile URL: {profile_url}")
    result = host.load("StructureDefinition", phenotype)
    example_patient = prep_server["CMG"]["Patient"][0]
    response = host.post("Patient", example_patient, validate_only=False)
    assert response["status_code"] == 201, "Just make sure Patient didn't fail for some reason"
    example_patient_id = response['response']['id']

    example_condition = copy.deepcopy(prep_server['CMG']['Condition'][0])
    # Gotta update the reference to make sense
    example_condition['subject']['reference'] = f"Patient/{example_patient_id}"
    #condition_profile = example_condition['meta']['profile'][0]

    # So, to throw the validation off, we just need to alter the value for code which 
    # is bound as required
    example_condition['code']['coding'][0] = {
        'system': "https://myown.omim-version.io",
        'code': 'HPO:00123456789',
        'display': 'Nonesene code'
    }

    response = host.post('Condition', example_condition, validate_only=False)
    if response['status_code'] != 422:
        pdb.set_trace()
        print(response['status_code'])
    assert response['status_code'] == 422, "Verify that the profile's constraints blocked validation as expected"

