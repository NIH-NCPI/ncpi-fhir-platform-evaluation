import pytest
import pdb

from fhireval.data import prep_server

test_id = f"{'2.10.1.2':<10} - Search Modifiers and Prefix"

test_weight = 15

def test_search_by_date(host, prep_server):
    # Find patients born after 1950
    birthdate_cutoff = 1950
    patient_count = 0
    for patient in prep_server['_ALL']['Patient']:
        if 'birthDate' in patient and int(patient['birthDate']) > birthdate_cutoff:
            patient_count += 1
    
    response = host.get(f"Patient?birthdate=gt{birthdate_cutoff}&_total=accurate").response
    assert response['total'] == patient_count
    
def test_search_by_number(host, prep_server):
    vq = None

    for obs in prep_server['_ALL']['Observation']:
        if 'valueQuantity' in obs:
            vq = obs['valueQuantity']
            break
        
    assert vq is not None, "Make sure we have something to test"
    response = host.get(f"Observation?value-quantity={vq['value']}&_total=accurate").response
    assert response['total'] > 0
    
    for obs in response['entry']:
        #pdb.set_trace()
        assert obs['resource']['valueQuantity']['value'] == vq['value'], "Make sure all of our matches really do match"


def test_search_by_approximation(host, prep_server):
    vq = None

    for obs in prep_server['_ALL']['Observation']:
        if 'valueQuantity' in obs:
            vq = obs['valueQuantity']
            break
        
    assert vq is not None, "Make sure we have something to test"
    response = host.get(f"Observation?value-quantity=ap{vq['value']}&_total=accurate").response
    assert response['total'] > 0
    match_count = response['total']

    # approximate uses 10%
    min_value = vq['value'] * 0.90
    max_value = vq['value'] * 1.10

    for obs in response['entry']:
        obs_value = obs['resource']['valueQuantity']['value']

        assert min_value <= obs_value and max_value >= obs_value, f"Is {obs_value} within the range ({min_value}, {max_value})"


def test_search_by_quantity(host, prep_server):
    weight_cutoff = 80
    observation_count = 0

    for obs in prep_server['_ALL']['Observation']:
        if 'valueQuantity' in obs:
            vq = obs['valueQuantity']
            if vq['unit'] == 'kg' and vq['value'] > weight_cutoff:
                observation_count += 1
    response = host.get(f"Observation?value-quantity=gt{weight_cutoff}||kg").response
    assert response['total'] == observation_count, f"Verify that our {response['total']} equals the expected {observation_count}"

def test_search_by_token(host, prep_server):
    bmi_count = 0
    for obs in prep_server['_ALL']['Observation']:
        if obs['code']['coding'][0]['code'] == '39156-5':
            bmi_count += 1
    
    response = host.get(f"Observation?code=39156-5").response
    assert response['total'] == bmi_count, f"Verify that BMI count, {response['total']} matches expected {bmi_count}"


