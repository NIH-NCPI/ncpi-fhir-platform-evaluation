import pytest
import pdb

from fhireval.data import prep_server, id_list

test_id = f"{'2.10.1.4':<10} - Chaining"

test_weight = 8

def test_chaining(host, prep_server):
    # Let's find all specimens for female patients
    record_count = 0

    response = host.get("Specimen?subject.gender=female")
    assert response.status_code==200
    for record in response.entries:
        if 'resource' in record:
            record = record['resource']
        patient = host.get(record['subject']['reference']).response
        assert patient['gender'] == 'female', "Make sure the search returned only females"
        record_count += 1

    # Just in case we don't have any females...
    if record_count == 0:
        response = host.get("Specimen?subject.gender=male")
        assert response.status_code==200
        for record in response.entries:
            if 'resource' in record:
                record = record['resource']
            patient = host.get(record['subject']['reference']).response
            assert patient['gender'] == 'male', "Make sure the search returned only males"
            record_count += 1

    assert record_count > 0, "Make sure our chained query returned at least 1 record"

