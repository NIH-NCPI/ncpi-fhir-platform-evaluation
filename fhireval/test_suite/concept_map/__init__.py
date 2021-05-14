
# The bullet points associated with this set of tests in the evaluation document
test_set_id = "2.8"

# User friendly name of the tests
test_set_name = "ConceptMap"

# Probably best for tests to log to this one so that they will all have the same entry
import logging
logger = logging.getLogger(__name__)

from fhir_walk.model import unwrap_bundle

# Stolen from https://www.hl7.org/fhir/cm-administrative-gender-v2.json.html
# These two code systems and valuesets do appear to be present in SMILES. May
# have to fall back to uploading them on other platforms, though
example_code_system_source = {
  "resourceType" : "ConceptMap",
  "id" : "cm-administrative-gender-v2",
  "url" : "http://hl7.org/fhir/ConceptMap/cm-administrative-gender-v2",
  "version" : "4.0.1",
  "name" : "cm-administrative-gender-v2",
  "title" : "v2 map for AdministrativeGender",
  "status" : "draft",
  "date" : "2019-11-01T09:29:23+11:00",
  "publisher" : "HL7 (FHIR Project)",
  "sourceCanonical" : "http://hl7.org/fhir/ValueSet/administrative-gender",
  "targetCanonical" : "http://terminology.hl7.org/ValueSet/v2-0001",
  "group" : [{
    "source" : "http://hl7.org/fhir/administrative-gender",
    "target" : "http://terminology.hl7.org/CodeSystem/v2-0001",
    "element" : [{
      "code" : "male",
      "target" : [{
        "code" : "M",
        "equivalence" : "equal"
      }]
    },
    {
      "code" : "female",
      "target" : [{
        "code" : "F",
        "equivalence" : "equal"
      }]
    },
    {
      "code" : "other",
      "target" : [{
        "code" : "A",
        "equivalence" : "wider"
      },
      {
        "code" : "O",
        "equivalence" : "wider"
      }]
    },
    {
      "code" : "unknown",
      "target" : [{
        "code" : "U",
        "equivalence" : "equal"
      }]
    }]
  }]
}

def reset_testdata(host):
    for entry in host.get(f"ConceptMap?name={example_code_system_source['name']}").entries:
        # Possibly there is a bundle
        if 'resourceType' in entry and entry['resourceType'] == 'Bundle':
            entry = unwrap_bundle(entry)
        elif 'resource' in entry:
            entry = [entry]


        for part in entry:
            print(part['resource']['id'])
            host.delete_by_record_id('ConceptMap', part['resource']['id'])
