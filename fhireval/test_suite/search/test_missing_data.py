import pytest
import pdb

from collections import defaultdict
from fhireval.data import prep_server

test_id = f"{'2.10.1.6':<10} - Missingness"

test_weight = 8

def test_missingness(host, prep_server):
    # Walk through patients and count the number of males and females and missing 
    counts = defaultdict(int)

    # In case some changes were made by prior tests, let's pull the patients from the server
    response = host.get(f"Patient").response
    if 'entry' not in response:        
        pdb.set_trace()
    for patient in response['entry']:
        patient = patient['resource']
        if 'gender' not in patient:
            counts['missing'] += 1
        else:
            counts['not-missing'] += 1
            counts[patient['gender']] += 1
    
    response = host.get(f"Patient?gender:missing=false&_total=accurate").response
    assert counts['not-missing'] == response['total'], \
        f"Did we find the right number of non-missing values? {counts['not-missing']} == {response['total']}"

    response = host.get(f"Patient?gender:missing=true&_total=accurate").response
    assert counts['missing'] == response['total'], \
        f"Did we find the right number of missing values? {counts['missing']} == {response['total']}"
