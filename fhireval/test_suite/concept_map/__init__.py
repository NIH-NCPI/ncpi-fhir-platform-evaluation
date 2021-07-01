import pdb
# The bullet points associated with this set of tests in the evaluation document
test_set_id = "2.04"

# User friendly name of the tests
test_set_name = "ConceptMap"

# Probably best for tests to log to this one so that they will all have the same entry
import logging
logger = logging.getLogger(__name__)

from fhir_walk.model import unwrap_bundle

from fhireval.test_suite.crud import prep_server
# The Map that made it's way into the test set was taken from the link below:
# https://www.hl7.org/fhir/cm-administrative-gender-v2.json.html
# These two code systems and valuesets do appear to be present in SMILES. May
# have to fall back to uploading them on other platforms, though

def reset_testdata(host, prep_server):

    example_code_system_source = prep_server['CMG']['ConceptMap'][0]
    for entry in host.get(f"ConceptMap?name={example_code_system_source['name']}").entries:
        # Possibly there is a bundle
        if 'resourceType' in entry and entry['resourceType'] == 'Bundle':
            entry = unwrap_bundle(entry)
        elif 'resource' in entry:
            entry = [entry]

        for part in entry:
            print(part['resource']['id'])
            host.delete_by_record_id('ConceptMap', part['resource']['id'])
