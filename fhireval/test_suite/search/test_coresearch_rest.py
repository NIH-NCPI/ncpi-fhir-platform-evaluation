import pytest
import pdb

from fhir_walk.model.patient import Patient
from fhireval.data import prep_server, id_list

from pprint import pformat

test_id = f"{'2.10.1.1':<10} - Core FHIR Search"

test_weight = 15

# TODO Get IDs for data to be qureied
# Profiles to be queried
#   'ResearchStudy', 'ResearchSubject', 'Organization', 'Specimen', 'Observation', 'DiagnosticReport','Condition', 'DocumentReference', 'Task', 'Group'

# When comparing search results, ignore certain columns that will definitely be 
# different in the value returned from fhir
_params_to_ignore = ['meta', 'id']
# Simple tests for identity
@pytest.mark.parametrize("resource", ["Patient", "Observation", "Condition", "ResearchSubject", "ResearchStudy"])
def test_search_by_identifier(host, prep_server, resource):
    example_resource = prep_server['_ALL'][resource][0]
    example_system = example_resource['identifier'][0]['system']
    example_identity = example_resource['identifier'][0]['value']

    # Simple query based on the value
    # This only works if there isn't a "|" in the identifier, otherwise, that first part will 
    # be compared to the system. 
    if "|" not in example_identity:
        qry_response = host.get(f"{resource}?identifier={example_identity}").entries
        assert len(qry_response) == 1, f"Only one record returned (got {len(qry_response)}"
        fhir_record = qry_response[0]
        
        for key in example_resource.keys():
            if key not in _params_to_ignore:
                if 'resource' not in fhir_record:
                    pdb.set_trace()
                assert example_resource[key] == fhir_record['resource'][key], f"Testing for attribute {key}"

    # Simple query based on system|value
    qry_response = host.get(f"{resource}?identifier={example_system}|{example_identity}").entries
    assert len(qry_response) == 1, "Only one record returned"

    fhir_record = qry_response[0]
    for key in example_resource.keys():
        if key not in _params_to_ignore:
            assert example_resource[key] == fhir_record['resource'][key]

search_transforms = {
    "verificationStatus": "verification-status",
    'groupIdentifier': "group-identifier",
    "birthDate": "birthdate",
    'onsetAge': 'onset-age'
}

def search_parameter(parameter):
    if parameter in search_transforms:
        return search_transforms[parameter]
    return parameter

"""# We don't have any coded tasks at this time
                            ('Task', ('code',)
"""
@pytest.mark.parametrize("resource, params", [
                            ('PractitionerRole', ('code|role',)), 
                            ('Observation', ('code',)), 
                            ('Condition', ('code', 'category', 'verificationStatus'))
                        ])
def test_search_by_coding(host, prep_server, resource, params):
    example_resource = prep_server['_ALL'][resource][0]
    
    for param in params:
        if "|" in param:
            param, qry_param = param.split("|")
        else:
            qry_param = param

        example_resource = None
        for item in prep_server['_ALL'][resource]:
            if param in item:
                example_resource = item
                break
        
        assert example_resource is not None, f"Find a suitable {resource} with parameter, {param}"

        param_content = example_resource[param]

        # Some of these parameters point to x..1 some to ..*  We just care about testing one
        # of the codes
        if type(param_content) is list:
            param_content = param_content[0]

        if 'coding' not in param_content:
            pdb.set_trace()
        example_code = param_content['coding'][0]['code']

        qry_response = host.get(f"{resource}?{search_parameter(qry_param)}={example_code}").entries
        assert len(qry_response) > 0, "One or more records returned"

        found_match = False
        for response in qry_response:
            found_match = found_match or example_resource['identifier'][0] == response['resource']['identifier'][0]

        assert found_match, "Valid match was found"

@pytest.mark.parametrize("resource, params", [
                                ('PractitionerRole', ('practitioner', 'organization')),
                                ('Observation', ('subject',)),
                                ('DocumentReference', ('subject',)),
                                ('Condition', ('subject',)),
                                ('Specimen', ('subject',))
                            ])
def test_search_by_reference(host, prep_server, resource, params):
    example_resource = prep_server['_ALL'][resource][0]
    
    for param in params:
        example_resource = None

        for item in prep_server['_ALL'][resource]:
            if param in item:
                example_resource =item
                break
        
        assert example_resource is not None, f"Find a suitable {resource} with parameter, {param}"
        assert param in example_resource, f"Make sure that {resource} has {param}"
        if 'reference' not in example_resource[param]:
            pdb.set_trace()
        example_reference = example_resource[param]['reference']

        qry_response = host.get(f"{resource}?{search_parameter(param)}={example_reference}").entries
        assert len(qry_response) > 0, "One or more records returned"

        found_match = False
        for response in qry_response:
            found_match = found_match or example_resource['identifier'][0] == response['resource']['identifier'][0]

        assert found_match, "Valid match was found"

"""# We don't have any data with this and will need to identify a way to run this test"""
def test_search_by_param_value(host, prep_server):
    assert 0 == 1, "Create some data to test with"
"""
@pytest.mark.parametrize("resource, params", [
                                ('Task', ('groupIdentifier',))
                            ])
def test_search_by_param_value(host, prep_server, resource, params):
    for param in params:
        example_resource = None

        for item in prep_server['_ALL'][resource]:
            if param in item:
                example_resource = item
                break
        assert example_resource is not None, f"Make sure we have a {resource} with {param}"
        example_reference = example_resource[param]['value']

        qry_response = host.get(f"{resource}?{search_parameter(param)}={example_reference}").entries
        assert len(qry_response) > 0, "One or more records returned"

        found_match = False
        for response in qry_response:
            found_match = found_match or example_resource['identifier'][0] == response['resource']['identifier'][0]

        assert found_match, "Valid match was found"
"""

# TODO - There are some parameters that sound like good choices, but some are a bit 
#        questionable ATM. Also, we should make sure that our test data covers 
#        all of them adequately, which may require some way to mark certain items
#        better suited for this sort of test than others
#
#        Observation.focus -- This is marked as TU
#        DocumentReference.??  -- My example is pretty light on contents, so we may want 
#                                 to add some parameters to them to enable searching
#                              -- contenttype is searchable, but I'm not sure we are currently
#                                 using that. It could be helpful if we wanted to take advantage
#                                 for certain types of usecases (if such a thing exists)
@pytest.mark.parametrize("resource, params", [
                            ('Patient', ('birthDate', 'gender')),
                            ('Practitioner', ('gender',)),
                            ('Condition', ('onsetAge',)),
                            ('Task', ('intent',))])
def test_search_by_misc(host, prep_server, resource, params):


    for param in params:
        example_resource = None
        # Make sure this one has the parameter of interest:
        for item in prep_server['_ALL'][resource]:
            if param in item:
                example_resource = item
                break

        assert example_resource is not None, "Make sure we have something to test with {param}"

        example_value = example_resource[param]
        if type(example_value) is dict:
            example_value = example_value['value']
        qry_response = host.get(f"{resource}?{search_parameter(param)}={example_value}").entries
        assert len(qry_response)> 0, f"At least one record returned for {resource} ? {example_value}"
        fhir_record = qry_response[0]

        found_match = False
        for response in qry_response:
            found_match = found_match or example_resource['identifier'][0] == response['resource']['identifier'][0]

        assert found_match, "Valid match was found"


# This is a specialized test where there is a singular criteria that can be applied
# to different resources which have the same bit of information (the relevant patient)
# but under a different parameter. 
@pytest.mark.parametrize("resource, param, qry", [
                        ('Task', 'for', 'subject'),
                        ('DocumentReference', 'subject', 'patient'),
                        ('Specimen', 'subject', 'patient'),
                        ('ResearchSubject', 'individual', 'patient')
])
def test_search_by_patient(host, prep_server, resource, param, qry):
    example_resource = prep_server['_ALL'][resource][0]
    example_system = example_resource['identifier'][0]['system']
    example_identity = example_resource['identifier'][0]['value']
    example_patient_ref = example_resource[param]['reference']

    qry_response = host.get(f"{resource}?{qry}={example_patient_ref}").entries
    assert len(qry_response) > 0, f"At least one record should have been found for {resource}?patient={example_patient_ref}"
    fhir_record = qry_response[0]


def test_search_by_profile(host, prep_server):
    # Just do family members. 
    fammemb_count = 0

    for obs in prep_server['_ALL']['Observation']:
        #print(pformat(obs))
        if 'meta' in obs and obs['meta']['profile'][0] == "https://ncpi-fhir.github.io/ncpi-fhir-ig/StructureDefinition/family-relationship":
            fammemb_count += 1

    assert fammemb_count > 0, "Make sure our 'Family-Relationship' profile is spelled correctly"
    response = host.get("Observation?_profile:below=https://ncpi-fhir.github.io/ncpi-fhir-ig/StructureDefinition/family-relationship&_total=accurate").response

    assert response['total'] == fammemb_count
