import pytest
import pdb

from fhir_walk.model.patient import Patient

test_id = f"{'2.2.1.1':<10} - Core FHIR Search"

test_weight = 15

# TODO Get IDs for data to be qureied
# Profiles to be queried
#   'ResearchStudy', 'ResearchSubject', 'Organization', 'Specimen', 'Observation', 'DiagnosticReport','Condition', 'DocumentReference', 'Task', 'Group'

# This is just data I've been using as fake data. The official dataset will likely
# look very different
def test_basic_patient_queries(host):
    # This tests Patient?identifier='fd-sub1'
    patient = Patient.PatientBySubjectID(None, 'fd-sub1', host) 
    assert patient is not None
    assert patient.sex == 'male'

