import pytest
import pdb

from fhireval.data import prep_server, id_list

test_id = f"{'2.10.1.5':<10} - Reverse Chaining"

test_weight = 5

def test_reverse_chaining(host, prep_server):
    # Let's get a condition and find all patients with that code
    condition = prep_server['_ALL']['Condition'][0]
    code = condition['code']['coding'][0]['code']

    patient_refs = set()
    # Let's get all of those conditions to build up a set of patient references
    response = host.get(f"Condition?code={code}")
    assert response.status_code == 200

    for record in response.entries:
        if 'resource' in record:
            record = record['resource']
        
        patient_refs.add(record['subject']['reference'])

    assert len(patient_refs) > 0, "We should have at least one of these"
    # Now let's find all patients with that code
    record_count = 0

    response = host.get(f"Patient?_has:Condition:patient:code={code}")
    assert response.status_code==200
    for record in response.entries:
        if 'resource' in record:
            record = record['resource']

        assert f"Patient/{record['id']}" in patient_refs, f"Make sure this is one of the {len(patient_refs)} patients"
        record_count += 1

    assert record_count == len(patient_refs), "Did we get all of the matches?"
