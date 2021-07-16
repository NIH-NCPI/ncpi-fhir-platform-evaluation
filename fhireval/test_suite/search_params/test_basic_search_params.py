import pytest
import pdb

from pprint import pformat
import collections
from fhireval.data import prep_server

test_id = f"{'2.08.1':<10} - Basic Search Params"

test_weight = 3

custom_search = {
	"resourceType": "SearchParameter",
    "url": "http://hl7.org/fhir/us/core/SearchParameter/us-core-race",
	"name": "Race",
    "description": "Search patient by race",
	"base": [ "Patient" ],
	"status": "active",
	"code": "race",
	"type": "token",
	"expression": "Patient.extension('http://hl7.org/fhir/us/core/StructureDefinition/us-core-race').extension.value.code",
    "xpath": "f:Patient/f:extension[@url='http://hl7.org/fhir/us/core/StructureDefinition/us-core-race']/f:extension/f:valueCoding/f:code/@value",
	"xpathUsage": "normal"
}

def test_search_params(host, prep_server):
    global custom_search
    result = host.load("SearchParameter", custom_search, skip_insert_if_present=False)
    assert result['status_code'] == 201, "Success loading the search parameter"

    # 2028-9 Asian
    # 2054-5 Black
    # 2106-3 White
    races = collections.defaultdict(int)
    patients = host.get(f"Patient").entries
    patient_total = 0
    for patient in patients:
        patient = patient['resource']
        for ext in patient['extension']:
            if ext['url'] == "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race":
                patient_total += 1
                races[ext['extension'][0]['valueCoding']['code']] += 1
    
    assert patient_total > 0, "Make sure we had one or more Patients with a specified race"
    entries = host.get(f"Patient?race=2028-9").entries
    assert len(entries) == races['2028-9'], f"Correct number of Asian Patients? {len(entries)} == {len(races['2028-9'])}"
    entries = host.get(f"Patient?race=2054-5").entries
    assert len(entries) == races['2054-5'], f"Correct number of Black Patients? {len(entries)} == {len(races['2054-5'])}"
    entries = host.get(f"Patient?race=2106-3").entries
    assert len(entries) == races['2106-3'], f"Correct number of White Patients? {len(entries)} == {len(races['2106-3'])}"




