# ncpi-fhir-platform-evaluation
This repository is intended to be a comprehensive test suite that can be run against any FHIR server to evaluate it's capabilities with regard to the key components enumerated in the [Google Doc](https://docs.google.com/document/d/14v262NcQ3gi_zA2aYhGA1n57jqyu9iyv4lx5y0ldfRA/edit#heading=h.v5btdkozye9p). In addition to an automated series of tests, there should also be a companion dataset which features all aspects of the projects requirements that has no restrictions to access (i.e. simulated data). 

This test suite will assume that the endpoint exists and that security tokens/cookies/passwords are properly configured on the server such that the test suite can perform all tasks including create, delete, update and read. Server setup and configuration will remain separate and evaluation on setup issues and experiences should be written up separately.

The test framework will provide a flexible host configuration that can be extended to support both cloud and local platform authentication.

# Installation
There are a small number of library dependencies. To install them, run the following command within the top level directory of the repository:
    pip install -r requrements.txt

Once this is done, you'll need to then install the program itself:
    python setup.py develop

Alternatively, you can do both with a single command:
    pip install -e .

(users can drop the -e argument if they aren't planning to perform any debugging)

I find it easier to debug using the "develop" option. Once the test suite is more stable, it will probably be preferable to not use the develop option unless the user plans to make changes to the test suite itself.

# Standard Linux Help
Users can always get a listing of options using the argument --help

# Basic Usage
The most important arguments are listed below, however, users can change details such as log directory, report directory, report prefix and log level using command line arguments. These are described in the default help listing described above.

## Choosing the platform to be tested
Once you have a valid hosts configuration, you can choose which host to run tests against using -e/--env host_id. The help listing will list each of the configured hosts the program has found in your fhir_hosts file

## Selecting test modules
This is probably useful only when writing tests, but you can provide one or more test modules using -m/--module (this argument may appear one or more times). Only the modules listed this way will be run. Please note that the report will be overwritten using only the specified tests, so please be sure to rerun the entire suite before checking in your final test results

## Trace Errors
To minimize the output during execution, the tests are run with only minimal feedback indicating pass/fail. However, when writing tests, it may be necessary to get the complete error report. --show-error-trace will turn this feature on. Please be aware that this creates a huge amount of extra output, and if you don't restrict which modules are run, the error of interest could very well scroll outside the buffer and be inaccessible.

# Building host configuration
FHIR hosts are identified within the [YAML file](yaml.org), fhir_hosts, found inside the current working directory. This file should not be checked into the repository and has been added to the ignore list. The YAML format for a host is of the form: 

    host_id:
        auth_type: 'auth_basic'
        username: 'admin'
        password: 'password'
        (etc)

The ":" indicate a key:value combination with entris with more indention parent/child relationship (in the example above, keys auth_type, username, password are child properties of the parent, host_id)

Users are welcome to define as many hosts as is needed but each one must be entered with a unique ID. IDs should consist of numbers/upper & lower case letters and underscores. Other characters may cause issues with the test's behavior.

There are two properties that must be present that are specific to the host, not the authentication typ: 
1.  host_desc   - This will be used to identify the tests in the report. Please note that this will be used to build a filename. Spaces will be replaced with "_", but slashes and other characters that have meaning in the filesystem should be avoided. 
2.  target_service_url - This is the actual URL associated with the fhir server being described. 

In addition to those two properties, users much provide a valid auth_type. This is just the authentication module's "id", which is just the "stem" of the python module's filename. The example config will provide the auth_type. 

## Autogeneration of example host file
If you run the script with no fhir_hosts file (or an empty one), the script will halt and write an example config to std out which may be redirected to the desired filename using standard redirection. Once that has been created, simply provide suitable IDs and parameters for the authentication schemes of interest and remove any others. Users can trigger this behavior at any time using the argument --example_cfg (please note that doing this will generate completely generic examples, so if you redirect the output to write over your personalized fhir_hosts file, your personlizations will be lost and you will have the default example which will likely not be valid for any actual FHIR server)

# Writing new auth modules
The authentication mechanics are wrapped inside the [NCPI FHIR Client Library](https://github.com/ncpi-fhir/ncpi-fhir-client). Adding new modules is straightforward: 

1.  Create a file inside the ncpi_fhir_client/fhir_auth directory. Filenames must start with auth_ and should be lowercase and underscores. This is known as [snake case](https://en.wikipedia.org/wiki/Snake_case). 
2.  Inside this file, create a class named the same as the python file created in #1 using [CamelCase](https://en.wikipedia.org/wiki/Camel_case). 
3.  This class must have the following functions:
    1.  Constructor must accept a dictionary from which any relevant key/values will be found
    2.  update_requst_args must accept the dictionary, request_args, which will be passed on as part of the request. Developers must understand which parts (header, auth, etc) must be updated to support the authentication scheme being built.
    3.  example_config takes two parameters: writer and other_entries. The writes just the "file" to be written to and the other_entries is a dictionary containing a few keys that aren't specific to the authentication module such as host_desc and the host's url. 
