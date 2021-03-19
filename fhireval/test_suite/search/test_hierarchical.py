import pytest
import pdb

from fhir_walk.model.patient import Patient

test_id = f"{'2.2.1.3':<10} - Hierarchical Search"

test_weight = 15

# Maybe we have some parents that are gendered and we can get all of them 
# using parent
def test_code_system(host):
    assert 0 == 1, "TODO - Write Test"

# Was an example at hl7, may not apply so we may need something else
def test_procedure_location(host):
    assert 0 == 1, "TODO - Write Test"

