"""
Encapsulates each test "module". It will run those modules, caputure their results and report the results
"""

import pytest
from pytest_jsonreport.plugin import JSONReport

from importlib import import_module
from fhireval.test_result import TestResult

class Runner:
    json_reporter = JSONReport()
    def __init__(self, dirname, filenames):
        self.dirname = dirname
        self.module_name = dirname.split(".")[-1]

        # We should allow the test_ids to determine order 
        self.filenames = {}
        # self.filenames = filenames
        self.script_filename = __name__

        # We'll attach the results using the test_id from the file
        self.test_results = {}      

        module = import_module(dirname)
        self.set_id = module.test_set_id
        self.set_name = module.test_set_name
        self.summary_result = None

        for file in filenames:
            mod_name = ".".join(list(file.parent.parts) + [file.stem])
            fmod = import_module(mod_name)
            self.filenames[fmod.test_id] = file
 
    def perform_tests(self, args):
        self.summary_result = TestResult(test_id=f"{self.set_id:<10} - {self.set_name} (Summary)")
        for test_id in sorted(self.filenames.keys()):
            filename = self.filenames[test_id]
            json_reporter = JSONReport()
            pytest.main(args + [str(filename)], plugins=[json_reporter])
            test_result = TestResult(filename, json_reporter.report)
            #self.test_results[test_result.test_id] = test_result
            self.summary_result.add_child(test_result)

            """
            self.summary_result.test_weight += test_result.test_weight
            self.summary_result.passed += test_result.passed
            self.summary_result.failed += test_result.failed
            self.summary_result.total += test_result.total    
            """

    # Eventually, I think we want to capture Pass/Fail/Except/etc for every
    # single test in a way that would let someone do some very detailed comparisons
    # across different platform. That information should be available from the 
    # report we get from pytest, so there may need to be some cleanup.
    def report_details(self, report):
        for test_id in sorted(self.filenames.keys()):
            self.summary_result.report_details(self.set_name, report)

    def report_score(self, report=None):
        """Report is a csv.writer object if provided and will capture the summary"""
        module = f"{self.set_id:<10} - {self.set_name}"
        #total_score = 0
        for test_id in sorted(self.test_results.keys()):
            test_result = self.test_results[test_id]
            if report:
                report.writerow([self.set_name] + test_result.as_row())
            print(test_result.as_str())
            #total_score += score
        #perc = total_score / self.total_weight * 100
        #summary_line = f"{module:<40} {total_score:<6.1f} {self.total_weight:<6.1f} {perc:>6.1f} {self.total_passed:>6} {self.total_failed:>6} {self.total_tested:>6}"
        summary_line = self.summary_result.as_str()

        if report:
            report.writerow(self.summary_result.as_row())
            """
            report.writerow([
                self.module_name,
                'Summary', 
                total_score,
                self.total_weight,
                perc, 
                self.total_passed,
                self.total_failed,
                self.total_tested
                ])
                """
        print("-" * len(summary_line))
        print(summary_line + "\n")
        return self.summary_result.score()




