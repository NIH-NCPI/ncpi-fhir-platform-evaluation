
# The bullet points associated with this set of tests in the evaluation document
test_set_id = "2.01"

# User friendly name of the tests
test_set_name = "Cap. Statement"


# Mem cache to avoid having to redo the same thing over and over
_capability_statement = None
_resources = None

import logging
logger = logging.getLogger(__name__)

def get_capability_statement(host):
    global _capability_statement, _resources
    if _capability_statement is None:
        entries = host.get('metadata', rec_count=-1).entries

        # Google wraps the capability statement into an array
        if type(entries) == list:
            assert len(entries) == 1, "Make sure only one statement was returned"
            entries = entries[0]

        logger.warning(f"Total number of resources: {len(entries['rest'][0]['resource'])}")
        _capability_statement = entries

        _resources = {}
        for res in entries['rest'][0]['resource']:
            _resources[res['type']] = res

    return _capability_statement

def get_resource(host, res_name):
    global _capability_statement, _resources

    if _resources is None:
        get_capability_statement(host)

    return _resources[res_name]



