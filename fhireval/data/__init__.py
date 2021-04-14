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

# DO NOT import this. Just use the load_test_data function. It won't reload if the
# data has already been loaded.
_resource_data = None

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
            delete_result = host.delete_by_record_id(resource_type, int(id))

    if records is None:
        for response in host.get(f"{resource_type}").entries:
            delete_from_response(response)
    else:
        # We may need slightly different ways to delete some of the resource types
        for record in records:
            if 'identifier' in record:
                for response in host.get(
                    f"{resource_type}?identifier={record['identifier'][0]['system']}|{record['identifier'][0]['value']}"
                ).entries:
                    if "resource" in response:
                        delete_from_response(response)

def load_test_data():
    global _resource_data

    if _resource_data is None:
        _resource_data = defaultdict(lambda: defaultdict(list))

        # Discover our test data and organize it into a nice litle dict with the
        # following structure:  groupname => resource_name => [fhir_compatible_dicts]
        files = pkg_resources.resource_listdir(__name__, "")
        for fn in files:
            if Path(fn).suffix.lower() == ".json":
                content = json.loads(
                    pkg_resources.resource_string(__name__, fn).decode("utf-8")
                )
                print(content.keys())
                groupname = content["groupname"]
                for resource_type in content.get("resources", []):
                    for record in content["resources"][resource_type]:
                        _resource_data["_ALL"][resource_type].append(record)
                        _resource_data[groupname][resource_type].append(record)
    
    return _resource_data
