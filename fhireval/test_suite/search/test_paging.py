import pytest
import pdb

from fhireval.data import prep_server
from collections import defaultdict

test_id = f"{'2.10.1.9.2':<10} - Paging"

test_weight = 8

def parse_link(link_entry):
    link_data = defaultdict(list)

    #pdb.set_trace()
    for entry in link_entry:
        link_data[entry['relation']].append(entry['url'])

    
    return link_data

def test_paging(host, prep_server):
    # We know there are more than 5 patients, so let's just go with that
    qry_response = host.get(f"Patient", recurse=False, rec_count=5, raw_result=True)
    assert qry_response['status_code'] == 200
    assert qry_response['response']['resourceType'] == 'Bundle', "Sanity check that we got a bundle like expected"
    assert qry_response['response']['total'] > 5, "Make sure we got more records than our max page size"
    assert len(qry_response['response']['entry']) == 5, "Did we get only 5 records"
    link_data = parse_link(qry_response['response']['link'])
    assert 'next' in link_data, "Do we have a link for the next page?"

    # Just for giggles, let's go ahead and pull that next page 
    url = link_data['next'][0]

    # Step out of the intended use for FhirHost and do some stuff at a much
    # lower level to avoid issues with that URL from above

    # Take care of login details
    reqargs = {}
    host.auth.update_request_args(reqargs)    

    # Now, we'll just issue the request a bit more directly
    success, qry_response = host.client().send_request("GET", f"{url}", **reqargs)
    assert qry_response['status_code'] == 200
    assert qry_response['response']['resourceType'] == 'Bundle', "Sanity check that we got a bundle like expected"

    link_data = parse_link(qry_response['response']['link'])
    assert 'previous' in link_data, "Make sure that the previous link is present"

