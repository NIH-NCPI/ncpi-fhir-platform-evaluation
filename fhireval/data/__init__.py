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
import sys

from pprint import pformat
from collections import OrderedDict, defaultdict

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
    'DiagnosticReport',
    'ConceptMap'
]

_model_resource_order = [
    'CodeSystem',
    'ValueSet',
    'StructureDefinition',
    'ImplementationGuide'
]

# Some resources don't actually have an id. Here, we'll provide 
# the alternate prarameter to search on
_alternate_search_params = {
    "SearchParameter": "url"
}

# Permit the application to bypass reprovision based on flag from user
_skip_reprovision = False

def skip_reprovision(do_skip=None):
    """Safely set the skip flag"""
    global _skip_reprovision
    if do_skip is not None:
        _skip_reprovision = do_skip

    return _skip_reprovision


def delete_from_response(host, resource_type, response, sleep_til_gone=True):
    """Delete a resource object based on response from a get
    
    Delete a resource based on contents from a get. This will use the object's ID if possible, 
    which should prevent deleting content with overlapping names or URIs

    :param host:  Fixture referencing the fhirclient object
    :type host: ncpi-fhir-client
    :param resource_tye: Which resource type is to be deleted (Patient, ResarchStudy, etc)
    :type resource_type: String
    :param response: The record obtained from the fhir server itself with details about what is to be deleted
    :type response: dict
    :param sleep_til_gone: When true, the function blocks until the object is truly deleted
    :type sleep_til_gone: bool
    """
    if "resource" in response:
        id = response['resource']['id']

        # Some systems expect integer IDs, while others expect GUIDs, which obviously aren't convertable to ints
        try:
            id = int(id)
        except:
            pass
        delete_result = host.delete_by_record_id(resource_type, id)
        if delete_result['status_code'] < 300: #!= 409:
            if sleep_til_gone:
                if 'name' in response['resource']:
                    host.sleep_until(f"{resource_type}?name={response['resource']['name']}", 0)
                elif 'url' in response['resource']:
                    host.sleep_until(f"{resource_type}?url={response['resource']['url']}", 0)
                elif 'identifier' in response['resource']:

                    idnt = response['resource']['identifier'][0]
                    host.sleep_until(f"{resource_type}?identifier={idnt['system']}|{idnt['value']}", 0)
                else:
                    pdb.set_trace()
                    host.sleep_until(f"{resource_type}/{id}", 0)
        return delete_result['status_code']

def delete_content_by_name(host, resource_type, record, sleep_til_gone=True):
    """Delete resource object based on name found inside record

    :param host:  Fixture referencing the fhirclient object
    :type host: ncpi-fhir-client
    :param resource_tye: Which resource type is to be deleted (Patient, ResarchStudy, etc)
    :type resource_type: String
    :param record: Containing a valid name for the item. This may be from the fhir server or possible some other source of JSON like objects
    :type record: dict
    :param sleep_til_gone: When true, the function blocks until the object is truly deleted
    :type sleep_til_gone: bool    
    """
    return_codes = []
    qry = f"{resource_type}?name={record['name']}"
    for response in host.get(qry).entries:
        return_codes.append(delete_from_response(host, resource_type, response, sleep_til_gone))

    return return_codes

# Helper script to provide an easy way to clear out old test data
def delete_content_for_resource(host, resource_type, records=None, sleep_til_gone=True):
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


    if records is None:
        redos = []
        last_response = None
        entries = host.get(f"{resource_type}").entries

        deleted_count = 0
        if len(entries) > 0:
            print(f"Deleting {len(entries)} from {resource_type}\t", end='', flush=True)
            for response in entries:
                return_code = delete_from_response(host, resource_type, response, sleep_til_gone=False)
                if return_code == 409:
                    redos.append(response)
                else:
                    deleted_count += 1
        
        for response in redos:
            delete_from_response(host, resource_type, response, sleep_til_gone=False)
            deleted_count += 1
        
        if deleted_count > 0 and sleep_til_gone:
            host.sleep_until(f"{resource_type}", 0, message=resource_type)
        elif len(entries) > 0:
            print()
    else:
        # We may need slightly different ways to delete some of the resource types
        for record in records:
            identifier = get_identifier(record)

            qry = f"identifier={identifier[0]['system']}|{identifier[0]['value']}"
            if identifier is None and resource_type in _alternate_search_params:
                if param not in record:
                    print(record.keys())
                qry = f"{param}={record[param]}"
            for response in host.get(
                f"{resource_type}?{qry}"
            ).entries:
                if "resource" in response:
                    delete_from_response(host, resource_type, response)

def resource_order():
    return _resource_order

def load_test_model(host):
    """Load the full model into memory"""

    print("Loading Model into memory")
    wait_list = []

    # For the IG, we'll need to replace references id (pre submission) => id
    ig_id_lookup = {}
    for resource in _model_resource_order:
        if resource in _resource_data['_MODEL']:
            for record in _resource_data['_MODEL'][resource]:
                if resource == 'ImplementationGuide':
                    build_references(record, ig_id_lookup)
                    pdb.set_trace()
                id = None
                if "id" in record:
                    id = record['id']
                response = host.load(resource, record, validate_only=False, skip_insert_if_present=True)
                
                if 'resource' not in response['response']:
                    if 'id' in response['response']:
                        new_id = response['response']['id']
                    else:
                        pdb.set_trace()
                else:
                    new_id = response['response']['resource']['id']
                ig_id_lookup[id] = new_id

                if response['status_code'] != 201:
                    pdb.set_trace()
                    print(resource)
                    print(response)
                wait_list.append(f"{resource}?url={record['url']}")
    print("Sleeping until model components are recognized")
    for url in wait_list:
        print(url)
        host.sleep_until(url, 1, message=url)


def delete_test_model(host):
    """Purges the existing customized model in order to permit a newer version to be loaded in it's place"""
    print("Deleting the previous test model if present")

    wait_list = []
    for resource in _model_resource_order[::-1]:
        if resource in _resource_data['_MODEL']:
            for record in _resource_data['_MODEL'][resource]:
                print(f"Deleting {resource} by name: {record['name']}")
                delete_content_by_name(host, resource, record, sleep_til_gone=False)
                qry = f"{resource}?name={record['name']}"
                # Make sure the database has caught up before proceeding
                wait_list.append(qry)

    print("Waiting for previous model cleanup to complete")
    for qry in wait_list:
        print(qry)
        host.sleep_until(qry, 0, message=qry)
    
def load_test_data(return_copy=False):
    global _resource_data, _resource_order

    if _resource_data is None:
        _resource_data = defaultdict(lambda: defaultdict(list))

        # Discover our test data and organize it into a nice litle dict with the
        # following structure:  groupname => resource_name => [fhir_compatible_dicts]
        files = pkg_resources.resource_listdir(__name__, "")
        for fn in files:
            if Path(fn).suffix.lower() == ".json":
                print(f"{fn}: \n\t", end='', flush=True)
                content = json.loads(
                    pkg_resources.resource_string(__name__, fn).decode("utf-8")
                )
                groupname = content["groupname"]
                datatype = content['datatype']
                for resource_type in content.get("resources", []):
                    print(f" {resource_type} ", end='', flush=True)

                    # Don't really need to add model resource types to the list
                    if datatype == 'Data' and resource_type not in _resource_order:
                        _resource_order.append(resource_type)
                    for record in content["resources"][resource_type]:
                        if datatype == 'Data':
                            _resource_data["_ALL"][resource_type].append(record)
                        elif datatype == 'Model':
                            _resource_data['_MODEL'][resource_type].append(record)
                        elif datatype == 'TestOnly':
                            # This shouldn't be added to either _ALL nor _MODEL, since 
                            # it really isn't normal data. Tests using data from this
                            # group, though, should be sure to clean up after themselves
                            pass
                        else:
                            print(f"{fn} has an invalid datatype, {datatype}, so giving up. 'datatype' must be either: Data or Model")
                            sys.exit(1)
                        _resource_data[groupname][resource_type].append(record)
                print()
    if return_copy:
        return copy.deepcopy(_resource_data)

    return _resource_data


def build_references(record, id_list):
    """Replace the inplace references with identifiers with actual IDs from 
    successful inserts. Please note the ID that will be matched on will be
    the first identifier, so please make sure the data is correctly defined."""

    # Bulk Export doesn't order things as nicely as it could
    # so we may need to 
    for key, value in record.items():
        if key == "reference":
            if type(value) is dict:
                if not build_references(value, id_list):
                    return False
            else:
                resource, identifier = value.split("/")

                if identifier not in id_list:
                    print(identifier)
                    return False

                record[key] = f"{resource}/{id_list[identifier]}"
        else:
            if type(value) is list:
                for item in value:
                    if type(item) is dict:
                        if not build_references(item, id_list):
                            return False
            if type(value) is dict:
                if not build_references(value, id_list):
                    return False
    return True
            

@pytest.fixture(scope="module")
def prep_server(host):
    if skip_reprovision():
        global _resource_data
        print("Warning, not purging and reloading data to avoid forever debug loops")
        if _resource_data is None:
            load_test_data()

        return _resource_data
    return reprovision_server(host)


def delete_test_data(host):
    print("Deleting the previous test content if present")
    load_test_data()

    wait_list = []
    for resource in resource_order()[::-1]:
        if resource in _resource_data['_ALL']:  
            delete_content_for_resource(host, resource, None, sleep_til_gone=False)
            wait_list.append(resource)
    
    for resource in wait_list:
        host.sleep_until(resource, 0, message=resource)

def reprovision_server(host):
    """This will build up the FHIR server, clearing out pre-existing records if
    any exist. This does perform yield and does not clean up after itself. The 
    idea here is that this data is loaded one time and only one time. Tests such
    as CRUD that presume a clean server should be run prior to the first use of this
    fixture. """
    global _resource_data, _inserted_id_list
    # For the CRUD, we just need to make sure we delete any leftover data from
    # failed tests and then, in the teardown, we do it once again
    completed_resources = defaultdict(list)

    if len(_inserted_id_list) == 0:
        # If we are selectively running tests, this may not exist yet
        if _resource_data is None:
            load_test_data()

        delete_test_data(host)
        print("Loading the test objects into the server")        
        observations = defaultdict(int)
        wait_list = {}
        # There are some issues with order that must be considered, so we'll use 
        # this guided list to help ensure that we get our references worked out
        for resource in resource_order():
            print(resource)
            if resource in _resource_data['_ALL']:
                records = copy.deepcopy(_resource_data['_ALL'][resource])
                #record_count = len(records)

                for orig_record in records:
                    record = copy.deepcopy(orig_record)
                    if build_references(record, _inserted_id_list):
                        response = host.post(resource, record, validate_only=False)

                        if response['status_code'] != 201:
                            pdb.set_trace()
                            print(resource)
                            print(pformat(response))

                            # Let's just try again, just for giggles
                            response = host.post(resource, record, validate_only=False)
                            
                            print(pformat(response))
                        identifier = get_identifier(response['response'])

                        idnt = identifier[0]['value']
                        if idnt in _inserted_id_list:
                            print(f"We found something that is in the dataset twice: {resource} {idnt}")
                            assert 0

                        _inserted_id_list[identifier[0]['value']] = response['response']['id']
                        completed_resources[resource].append(record)
                    else:
                        observations[record['identifier'][0]['value']] += 1
                        if observations[record['identifier'][0]['value']] > 1:
                            pdb.set_trace()
                        records.append(orig_record)

                wait_list[resource] = len(completed_resources[resource])
        for resource in wait_list.keys():
            host.sleep_until(resource, wait_list[resource], message=resource)
    if len(completed_resources) > 0:
        _resource_data['_ORIG'] = _resource_data['_ALL']
        _resource_data['_ALL'] = completed_resources
    return _resource_data

def id_list():
    return _inserted_id_list