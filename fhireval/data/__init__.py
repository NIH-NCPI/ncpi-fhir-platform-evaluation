"""
Test data is expected to be created to cover the needs for each of NCPI
members' needs and will likely be aggregated into separate files. The data
for each group can be stored as a single large json file or as separate 
files. Each file will have some wrapper information that help sort the
data so that test authors can access it easily enough.

Each of these files must be valid json files with the following root level
properties:
  "groupname": 'Whatever the group name is, such as DbGAP or CMG"
  "resources": { 
      "resource_1" : [
          list of valid fhir objects that can be "created" as part of a given
          resource (so for patients, 'resource_1' above would be 'Patient'). 
          These should all be of the same resource type
      ],
      "resource_2" : [
          list of valid fhir objects, etc
      ]
}

A special groupname, _ALL will be created containing a copy of all resources 
found in each of the groups.

It is assumed that the contents of each of the resource lists are valid and 
should load uniquely into a fhir server
"""
import pkg_resources
from pathlib import Path
from collections import defaultdict
import json
import copy
from time import sleep 

from collections import OrderedDict

from fhireval.test_suite import get_identifier

import pytest

import pdb

# DO NOT import any of these. Only use related functions to ensure that client
# calls are accessing the proper version in case it's replaced during an intialization
# call

# products from loading JSON objects
# Please note that once this module's prep_server is run, this will be modified
# with valid reference information and will not reflect the original source objects
# completely
_resource_data = None

# Identifier=>FHIR ID  (identifier is first identifier in the list)
_inserted_id_list = {}

# Helpful for ensuring that items with dependencies are correctly loaded/deleted
# in the right order
_resource_order = [
    'Organization',
    'ResearchStudy',
    'Patient',
    'Specimen',
    'ResearchSubject',
    'Practitioner',
    'PractitionerRole',
    'Condition',
    'Group',
    'Observation',
    'DocumentReference',
    'Task',
    'ConceptMap'
]

# Some resources don't actually have an id. Here, we'll provide 
# the alternate prarameter to search on
_alternate_search_params = {
    "SearchParameter": "url"
}
# Helper script to provide an easy way to clear out old test data
def delete_content_for_resource(host, resource_type, records=None):
    """Wrapper for deleting a resource object if it exists

    This function will identify the matches, get IDs and delete them. It
    is safe to call if the records do not exist (so it is suitable for
    cleanup prior to beginning tests in case some previous test data is
    left behind)

    :param host: Fixture referencing the fhirclient object
    :type host: ncpi-fhir-client
    :param resource_type: Which resource type is to be deleted (Patient, ResarchStudy, etc)
    :type resource_type: String
    :param records: one or more fhir objects which conform to the specified resource_type
    :type records: list of dictionary objects
    """

    def delete_from_response(response):
        if "resource" in response:
            id = response['resource']['id']

            # Some systems expect integer IDs, while others expect GUIDs, which obviously aren't convertable to ints
            try:
                id = int(id)
            except:
                pass
            delete_result = host.delete_by_record_id(resource_type, id)
            return delete_result['status_code']

    if records is None:
        redos = []
        for response in host.get(f"{resource_type}").entries:
            return_code = delete_from_response(response)
            if return_code == 409:
                redos.append(response)
        
        for response in redos:
            delete_from_response(response)
    else:
        # We may need slightly different ways to delete some of the resource types
        for record in records:
            identifier = get_identifier(record)
            print(f"Ooga: {identifier[0]['system']}|{identifier[0]['value']}")

            qry = f"identifier={identifier[0]['system']}|{identifier[0]['value']}"
            if identifier is None and resource_type in _alternate_search_params:
                if param not in record:
                    print(record.keys())
                    pdb.set_trace()
                qry = f"{param}={record[param]}"
            for response in host.get(
                f"{resource_type}?{qry}"
            ).entries:
                if "resource" in response:
                    delete_from_response(response)

def resource_order():
    return _resource_order

def load_test_data(return_copy=False):
    global _resource_data, _resource_order

    if _resource_data is None:
        _resource_data = defaultdict(lambda: defaultdict(list))

        # Discover our test data and organize it into a nice litle dict with the
        # following structure:  groupname => resource_name => [fhir_compatible_dicts]
        files = pkg_resources.resource_listdir(__name__, "")
        for fn in files:
            if Path(fn).suffix.lower() == ".json":
                print(fn)
                content = json.loads(
                    pkg_resources.resource_string(__name__, fn).decode("utf-8")
                )
                groupname = content["groupname"]
                for resource_type in content.get("resources", []):
                    print(f"{fn} {resource_type}")
                    #pdb.set_trace()
                    if resource_type not in _resource_order:
                        print(f"Adding resource type, {resource_type} to the list.")
                        _resource_order.append(resource_type)
                    for record in content["resources"][resource_type]:
                        _resource_data["_ALL"][resource_type].append(record)
                        _resource_data[groupname][resource_type].append(record)
    
    if return_copy:
        return copy.deepcopy(_resource_data)

    return _resource_data


def build_references(record, id_list):
    """Replace the inplace references with identifiers with actual IDs from 
    successful inserts. Please note the ID that will be matched on will be
    the first identifier, so please make sure the data is correctly defined."""

    for key, value in record.items():
        if key == "reference":
            resource, identifier = value.split("/")

            if identifier not in id_list:
                print(id_list.keys())
                print(identifier)
            print(f"Replacing ID: {identifier} with {id_list[identifier]}")
            record[key] = f"{resource}/{id_list[identifier]}"
        else:
            if type(value) is list:
                for item in value:
                    if type(item) is dict:
                        build_references(item, id_list)
            if type(value) is dict:
                build_references(value, id_list)
            

@pytest.fixture(scope="module")
def prep_server(host):
    """This will build up the FHIR server, clearing out pre-existing records if
    any exist. This does perform yield and does not clean up after itself. The 
    idea here is that this data is loaded one time and only one time. Tests such
    as CRUD that presume a clean server should be run prior to the first use of this
    fixture. """
    global _resource_data, _inserted_id_list
    # For the CRUD, we just need to make sure we delete any leftover data from
    # failed tests and then, in the teardown, we do it once again


    if len(_inserted_id_list) == 0:
        # If we are selectively running tests, this may not exist yet
        if _resource_data is None:
            load_test_data()

        print("Loading the test objcts into memory")
        # We are assuming the server is solely used for testing, so just delete 
        # everything.
        print("Deleting the previous test content if present")
        for resource in resource_order()[::-1]:
            print(f"Deleting All Content for {resource}")
            delete_content_for_resource(host, resource, None)

        # Give the server a little bit of time make sure everything finishes 
        # being deleted
        sleep(5)
        
        # There are some issues with order that must be considered, so we'll use 
        # this guided list to help ensure that we get our references worked out
        for resource in resource_order():
            print(resource)

            if resource in _resource_data['_ALL']:
                records = _resource_data['_ALL'][resource]

                for orig_record in records:
                    #pdb.set_trace()
                    record = orig_record.copy()
                    build_references(record, _inserted_id_list)
                    response = host.post(resource, record, validate_only=False)

                    if response['status_code'] != 201:
                        pdb.set_trace()
                        print(resource)
                        print(response)
                    identifier = get_identifier(response['response'])

                    idnt = identifier[0]['value']
                    if idnt in _inserted_id_list:
                        print(f"We found something that is in the dataset twice: {resource} {idnt}")
                        assert 0

                    _inserted_id_list[identifier[0]['value']] = response['response']['id']

    return _resource_data

def id_list():
    return _inserted_id_list