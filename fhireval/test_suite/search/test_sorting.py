import pytest
import pdb

from collections import defaultdict
from fhireval.data import prep_server


test_id = f"{'2.10.1.9.1':<10} - Sorting"

test_weight = 3

def test_sorting(host, prep_server):
    # how many males/females/other we actually have
    #pdb.set_trace()
    expected_counts = defaultdict(int)
    # Let's get an idea of the number of males and females in our dataset
    for patient in prep_server['_ALL']['Patient']:
        if 'gender' in patient:
            expected_counts[patient['gender']] += 1   
        else:
            expected_counts['missing'] += 1

    # how many we found before we encounter a new gender
    live_counts = defaultdict(int)
    qry_response = host.get(f"Patient?_sort=gender").entries
    # If we sort by gender, the first few should be female, since 'f' sorts before 'm'

    cur = qry_response[0]['resource']['gender']
    assert cur == 'female'

    for patient in qry_response:
        newgen = 'missing'
        if 'gender' in patient['resource']:
            newgen = patient['resource']['gender']
        if newgen == cur:
            live_counts[newgen] += 1
        else:
            assert live_counts[cur] == expected_counts[cur], f"Counts for {cur} {live_counts[cur]} == {expected_counts[cur]}"
            break
    
# Now, check reverse
def test_reverse_sorting(host, prep_server):
    # how many males/females/other we actually have
    expected_counts = defaultdict(int)
    # Let's get an idea of the number of males and females in our dataset
    for patient in prep_server['_ALL']['Patient']:
        if 'gender' in patient:
            expected_counts[patient['gender']] += 1   
        else:
            expected_counts['missing'] += 1

    # how many we found before we encounter a new gender
    live_counts = defaultdict(int)
    qry_response = host.get(f"Patient?_sort=-gender").entries
    # If we sort by reverse gender, the first few should be male

    cur = qry_response[0]['resource']['gender']
    assert cur == 'male'

    for patient in qry_response:
        newgen = 'missing'
        if 'gender' in patient['resource']:
            newgen = patient['resource']['gender']
        
        if newgen == cur:
            live_counts[newgen] += 1
        else:
            assert live_counts[cur] == expected_counts[cur], f"Counts for {cur} {live_counts[cur]} == {expected_counts[cur]}"
            break