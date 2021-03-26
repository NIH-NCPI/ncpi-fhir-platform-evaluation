
fhir_client = None

def get_host(env=None):
    global fhir_client
    return fhir_client

