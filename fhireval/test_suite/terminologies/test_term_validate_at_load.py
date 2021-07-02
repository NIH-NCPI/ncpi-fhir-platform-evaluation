import pytest
import pdb

from copy import deepcopy
from pprint import pformat

from fhireval.data import prep_server
test_id = f"{'2.7.1':<10} - Validate Terms at Load"

test_weight = 2

# We do this already elsewhere, but it may be worthwhile to do it explicitly here
# Use an invalid code in a Phenotype which should fail. Test again with 
# a valid code and assert success
def test_validate_term_with_invalid_code(host, prep_server):
    profiles = prep_server['NCPI-Model']['StructureDefinition']
    phenotype = None
    for profile in profiles:
        if profile['name'] == 'Phenotype':
            phenotype = profile
            break

    assert phenotype is not None, "Make sure there is a Phenotype profile to test"
    profile_url = phenotype['url']

    example_phenotype = None
    for condition in prep_server['_ALL']['Condition']:
        if 'meta' in condition and condition['meta']['profile'][0] == profile_url:
            example_phenotype = deepcopy(condition)

    # So, to throw the validation off, we just need to alter the value for code which 
    # is bound as required
    example_phenotype['code']['coding'][0] = {
        'system': "https://myown.omim-version.io",
        'code': 'HPO:00123456789',
        'display': 'Nonesene code'
    }
    
    response = host.post('Condition', example_phenotype, validate_only=True)
    assert response['status_code'] == 422, "Verify that the profile's constraints blocked validation as expected"

def test_validate_term_with_valid_code(host, prep_server):
    profiles = prep_server['NCPI-Model']['StructureDefinition']
    phenotype = None
    for profile in profiles:
        print(profile['name'])
        if profile['name'] == 'Phenotype':
            phenotype = profile
            break

    assert phenotype is not None, "Make sure there is a Phenotype profile to test"
    profile_url = phenotype['url']

    example_phenotype = None
    for condition in prep_server['_ALL']['Condition']:
        if 'meta' in condition and condition['meta']['profile'][0] == profile_url:
            example_phenotype = deepcopy(condition)

    response = host.post('Condition', example_phenotype, validate_only=True)
    assert response['status_code'] == 200, "Verify that the properly coded version did pass validation"

