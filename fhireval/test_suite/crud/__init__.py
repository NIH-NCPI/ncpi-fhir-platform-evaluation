
# The bullet points associated with this set of tests in the evaluation document
test_set_id = "2.5"

# User friendly name of the tests
test_set_name = "CRUD"

# Probably best for tests to log to this one so that they will all have the same entry
import logging
logger = logging.getLogger(__name__)

# This will be set by the create test
example_patient_id = None
example_patient = {
  "resourceType": "Patient",
  "meta": {
    "profile": [
      "http://hl7.org/fhir/StructureDefinition/Patient"
    ]
  },
  "identifier": [
    {
      "system": "https://ncpi-api-dataservice.kidsfirstdrc.org/participants?study_id=FAKE-CMG&external_id=",
      "value": "ctpatient01"
    },
    {
      "system": "urn:ncpi:unique-string",
      "value": "CRUDTEST|ctpatient01"
    }
  ],
  "extension": [
    {
      "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity",
      "extension": [
        {
          "url": "ombCategory",
          "valueCoding": {
            "system": "urn:oid:2.16.840.1.113883.6.238",
            "code": "2135-2",
            "display": "Hispanic or Latino"
          }
        },
        {
          "url": "text",
          "valueString": "Reported Unknown:Italian"
        }
      ]
    },
    {
      "url": "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race",
      "extension": [
        {
          "url": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor",
          "valueCoding": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor",
            "code": "UNK",
            "display": "Unknown"
          }
        },
        {
          "url": "text",
          "valueString": "Reported Unknown:Italian"
        }
      ]
    },
    {
      "url": "http://fhir.ncpi-project-forge.io/StructureDefinition/age-at-event",
      "valueAge": {
        "value": 31.0,
        "unit": "a",
        "system": "http://unitsofmeasure.org",
        "code": "years"
      }
    }
  ],
  "gender": "male"
}

def create_patient(host):
    return host.post('Patient', example_patient, validate_only=False)

def reset_crud_test_data(host):
  pass