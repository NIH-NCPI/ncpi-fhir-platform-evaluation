import pytest
import pdb


test_id = f"{'2.3.3':<10} - Profile Snapshot"

test_weight = 10

def test_profile_snapshot(host):
    # This point was added anonymously, and I don't understand it:
    """Does the profile support inheritance of snapshot when creating a custom profile off of a 
       base profile (e.g. some FHIR products don’t grab “snapshot” of parent profiles and render 
       only differentials)?"""
    assert 0 == 1, "TODO - Write Test"


