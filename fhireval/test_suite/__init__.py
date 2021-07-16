import pdb

fhir_client = None

def get_host(env=None):
    global fhir_client
    return fhir_client


def get_identifier(record):
    if "identifier" in record:
        idnt = record['identifier']

        # Normalize the return since we don't really want to build in so 
        # much context
        if type(idnt) is list:
            return idnt
        return [idnt]
    else:
        pdb.set_trace()
        pull.rabbit()