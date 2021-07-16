import pytest
import pdb
from time import sleep
from fhireval.data import prep_server
from fhirwood.codeable_concept import CodeableConcept

test_id = f"{'2.10.1.3':<10} - Hierarchical Search"

test_weight = 15

# Maybe we have some parents that are gendered and we can get all of them 
# using parent

# Observation?value-concept:_below=PRN
def test_code_system(host):
    # We'll seach for all parents, despite (hopefully) having no one marked as PRN
    response = host.get(f"Observation?value-concept=PRN&_total=accurate").response
    assert response['total'] == 0, "Make sure we don't have anyone marked with a family relationship as PRN (parent)"

    parent_count = 0
    response = host.get(f"Observation?code=FAMMEMB&_total=accurate").response
    for entry in response['entry']:
        #pdb.set_trace()
        code = CodeableConcept(block=entry['resource']['valueCodeableConcept'])

        # Right now, all of our data is either MTH or FTH
        if code == 'FTH' or code == 'MTH':
            parent_count += 1

    assert parent_count > 0, "Make sure we have non-zero parent count"
    response = host.get("Observation?value-concept:below=http://terminology.hl7.org/CodeSystem/v3-RoleCode|PRN&_total=accurate").response
    assert response['total'] == parent_count, f"Do our counts agree? ({parent_count} == {response['total']})"
