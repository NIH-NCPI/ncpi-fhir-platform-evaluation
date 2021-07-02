import pytest
import pdb


test_id = f"{'2.10.1.7':<10} - Composite Search"

test_weight = 9

def test_composite(host):
    record_count = 0

    # Let's get BMI > 33
    response = host.get("Observation?code-value-quantity=39156-5$gt33")
    assert response.status_code == 200

    for record in response.entries:
        if 'resource' in record:
            record = record['resource']        
        
        assert record['code']['coding'][0]['code'] == "39156-5"
        assert record['valueQuantity']['value'] > 33, "Make sure we did get what we asked for"
        assert record['valueQuantity']['unit'] == 'kg/m2', "Sanity check the units"
        record_count += 1
    
    assert record_count > 0, "We should have gotten at least one record"
