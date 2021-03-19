# ncpi-fhir-platform-evaluation
This repository is intended to be a comprehensive test suite that can be run against any FHIR server to evaluate it's capabilities with regard to the key components enumerated in the (https://docs.google.com/document/d/14v262NcQ3gi_zA2aYhGA1n57jqyu9iyv4lx5y0ldfRA/edit#heading=h.v5btdkozye9p) In addition to an automated series of tests, there should also be a companion dataset which features all aspects of the projects requirements that has no restrictions to access (i.e. simulated data). 

This test suite will assume that the endpoint exists and that security tokens/cookies/passwords are properly configured on the server such that the test suite can perform all tasks including create, delete, update and read. Server setup and configuration will remain separate and evaluation on setup issues and experiences should be written up separately.

The test framework will provide a flexible host configuration that can be extended to support both cloud and local platform authentication.

