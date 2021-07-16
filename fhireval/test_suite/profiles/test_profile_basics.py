import pytest
from time import sleep
import pdb

from fhireval.test_suite.crud import prep_server
from copy import deepcopy
from pprint import pformat
test_id = f"{'2.3.1':<10} - Profile Creation"

test_weight = 25

def test_user_defined_profile_creation(host, prep_server):
    example_patient = prep_server["CMG"]["Patient"][0]
    
    response = host.post("Patient", example_patient, validate_only=False)
    assert response["status_code"] == 201, "Just make sure Patient didn't fail for some reason"
    example_patient_id = response['response']['id']

    # Make up a condition with a meaningless profile
    example_condition =       {
        "resourceType": "Condition",
        "identifier": [
          {
            "system": "urn:ncpi-test:unique-string",
            "value": "CMG-phenotype-1"
          },
          {
            "system": "urn:ncpi-test:phenotype",
            "value": "CMG.1"
          }
        ],
        "verificationStatus": {
          "coding": [
            {
              "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
              "code": "confirmed",
              "display": "Confirmed"
            }
          ],
          "text": "Phenotype Present"
        },
        "category": [
          {
            "coding": [
              {
                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                "code": "encounter-diagnosis",
                "display": "Encounter Diagnosis"
              }
            ]
          }
        ],
        "code": {
          "coding": [
            {
              "system": "http://purl.obolibrary.org/obo/hp.owl",
              "code": "HP:0001578",
              "display": "Increased circulating cortisol level"
            }
          ],
          "text": "Present: Increased circulating cortisol level"
        },
        "subject": {
          "reference": f"Patient/{example_patient_id}"
        },
        "meta": {
          "profile": [
            "https://ncpi-fhir.github.io/ncpi-fhir-ig/StructureDefinition/invalid-phenotype"
          ]
        }
      }

    response = host.post('Condition', example_condition, validate_only=False)
    if response['status_code'] != 422:
        pdb.set_trace()
    #print(pformat(response))
    assert response['status_code'] == 422, "Load Condition when the structure def doesn't exist"

    profiles = prep_server['NCPI-Model']['StructureDefinition']
    phenotype = None
    for profile in profiles:
        if profile['name'] == 'Phenotype':
            phenotype = deepcopy(profile)
            break

    phenotype['url'] = "https://ncpi-fhir.github.io/ncpi-fhir-ig/StructureDefinition/valid-phenotype"
    phenotype['name'] = 'valid-phenotype'
    phenotype['title'] = 'A Valid Phenotype'
    example_condition["meta"] = {
          "profile": [
            "https://ncpi-fhir.github.io/ncpi-fhir-ig/StructureDefinition/valid-phenotype"
          ]
        }
    assert phenotype is not None, "Make sure there is a Phenotype profile to test"

    profile_url = phenotype['url']
    print(f"Profile URL: {profile_url}")
    result = host.load("StructureDefinition", phenotype, skip_insert_if_present=True)
    assert result['status_code'] == 201, "Success loading profile"

    # Now, we wait until it actually shows up...woohoo!
    response = host.sleep_until(f"StructureDefinition?url={profile_url}", 1)

    assert response.status_code == 200
    assert len(response.entries) > 0
    # now that we have the proper profile in place, let's try adding that 
    # phenotype object in

    # Try once again. It should now work just fine
    response = host.post('Condition', example_condition, validate_only=False)
    if response['status_code'] != 201:
        pdb.set_trace()
        print(pformat(response['response']))

        response = host.post('Condition', example_condition, validate_only=True)
        print(pformat(response['response']))
        response = host.post('Condition', example_condition, validate_only=False)
        
        print(pformat(response['response']))

    assert response['status_code'] == 201, f"Profiled condition successfully submitted {response['status_code']} == 201"

