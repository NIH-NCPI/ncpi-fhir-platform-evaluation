import pytest
import pdb
from fhireval.data import prep_server, id_list
from collections import defaultdict
from time import sleep
from pprint import pformat
import json
from base64 import b64decode

test_id = f"{'2.9.1':<10} - Bulk Export "

test_weight = 2

def bulk_export(host, endpt = None, resources=None):
    # Request our data to be fhir+json separated by new lines
    if endpt is None or endpt == "":
        endpoint = "$export?_outputFormat=application/fhir%2Bndjson"
    else:
        endpoint = f"{endpt}/$export?_outputFormat=application/fhir%2Bndjson"

    # We need to specify our types as comma separated list
    if resources is not None and len(resources) > 0:
        endpoint = f"{endpoint}&_type={','.join(resources)}"

    reqargs = {'headers': {
        'Prefer': 'respond-async'
        }
    }
    print(f"Attempting to export in bulk: {endpoint} \n\tWith headers: {reqargs['headers']}")
    result = host.get(endpoint, reqargs=reqargs, raw_result=True)

    # The payload is embedded inside the header. The response from this will include
    # the final data or a recommended wait time
    content_location = result['response_headers']['Content-Location']
    retry_after = 120

    # For each profile requested, there will be one or more links containing the 
    # actual data. 
    data_sources = defaultdict(list)

    while retry_after > 0:

        result = host.get(content_location, raw_result=True)
        if 'Retry-After' in result['response_headers']:
            retry_after = int(result['response_headers']['Retry-After'])
            print(f"Sleeping as requested: {retry_after}")
            sleep(retry_after)
        else:
            for chunk in result['response']['output']:
                data_sources[chunk['type']].append(chunk['url'])
            retry_after = 0

    total_rows_seen = 0
    data = defaultdict(list)
    for source_type  in data_sources.keys():
        print(f"{source_type} : {len(data_sources[source_type])} urls found")

        # For now, we'll just keep them until we've collected all and 
        # report on how many we found
        for url in data_sources[source_type]:
            result = host.get(url).response
            # The data comes as a byte string of base 64 encoded JSon objects, each
            # separated by a new line.
            payload = b64decode(result['data']).decode("utf-8").split("\n")
            for record in payload:
                if record.strip() != "":
                    data[source_type].append(json.loads(record))

    return data


def test_bulk_export_patients(host, prep_server):
    patients = prep_server['_ALL']['Patient']

    # As of writing this test, local SMILES is a little behind the current, and some bulk_export features
    # are not functional that are reported to be working on the official docs
    bulk_data = bulk_export(host, "Patient")

    assert len(patients) == len(bulk_data['entry']), f"Did we get the same number: {len(patients)} == {len(bulk_data['entry'])}"

def test_bulk_export_group(host, prep_server):
    target_group = None
    # Get the corresponding group with references to a few patients

    response = host.get("Group").response
    for group in response['entry']:
        group = group['resource']
        if 'member' in group:
            # Make sure the first member is a patient
            member = group['member'][0]['entity']['reference'].split("/")

            if member[0] == 'Patient':
                target_group = group
                break
    
    assert target_group is not None, "Make sure we could find a valid group"

    bulk_data = bulk_export(host, f"Group/{target_group['id']}")
    assert len(target_group['member']) == len(bulk_data['entry'])

_bulk_data_complete = None
@pytest.mark.parametrize("resource_type", ['Condition', 'DiagnosticReport', 'DocumentReference', 'Observation', 'Organization', 'Patient', 'ResearchStudy', 'ResearchSubject', 'Specimen', 'Task'])
def test_bulk_export_all(host, prep_server, resource_type):
    global _bulk_data_complete
    if _bulk_data_complete is None:
        _bulk_data_complete = bulk_export(host, "")
    
    assert resource_type in _bulk_data_complete, f"Test for {resource_type} in bulk output"
    assert len(prep_server['_ALL'][resource_type]) == len(_bulk_data_complete[resource_type]), f"Did we get 'everything' for {resource_type}? ({len(prep_server['_ALL'][resource_type])} == {len(_bulk_data_complete[resource_type])})"

def test_bulk_export_subset(host, prep_server):
    subset_resources = ['Patient', 'Observation']

    bulk_data = bulk_export(host, "", resources=subset_resources)
    
    for resource_type in subset_resources:
        assert resource_type in bulk_data
        assert len(prep_server['_ALL'][resource_type]) == len(bulk_data[resource_type]), f"Did we get 'everything' for {resource_type}? ({len(prep_server['_ALL'][resource_type])} == {len(bulk_data[resource_type])})"
