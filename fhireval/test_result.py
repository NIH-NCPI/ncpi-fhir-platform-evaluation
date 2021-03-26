"""
Module to be used to capture the results from execution of a single test
"""
from importlib import import_module
import pdb
import re

class TestResult:
    test_extraction_w_params = re.compile(r"(?P<test_module>[A-Za-z_]*).py::(?P<test_name>[A-Za-z_]*)\[(?P<params>[A-Za-z\-_0-9]*)\]")
    test_extraction_no_params = re.compile(r"(?P<test_module>[A-Za-z_]*).py::(?P<test_name>[A-Za-z_]*)")
    def __init__(self, test_filename=None, results=None, test_id=None):
        self.children = []
        self.summary_score = 0

        if test_filename:
            module = import_module(str(test_filename).replace(".py", "").replace("/", "."))

            self.test_id = module.test_id
            self.test_weight = module.test_weight
            self.passed = results['summary']['passed']
            self.failed = results['summary']['failed']
            self.total = results['summary']['total']


            # We can keep the results for possible reporting of the various tets run
            self._results = results
        else:
            self.test_id = test_id

            if self.test_id is None:
                self.test_id = '(Summary)'
            self.test_weight = 0
            self.passed = 0
            self.failed = 0
            self.total = 0
            self._results = {
                "test_name": self.test_id,
                "result_summary": {},
                "contents": {}
            }

    def add_child(self, child):
        """Children are added as children and their values are added into the local values as summary data"""

        self.test_weight += child.test_weight
        self.passed += child.passed
        self.failed += child.failed
        self.total += child.total
        self.summary_score += child.score
        self.children.append(child)

    @property
    def percentage_success(self):
        if self.total == 0:
            return 0
        return float(self.passed)/self.total
    
    @property
    def score(self):
        return self.percentage_success * self.test_weight

    def as_str(self):
        if self.summary_score == 0:
            self.summary_score = self.score
        return f"{self.test_id:<40} {self.summary_score:<6.1f} {self.test_weight:<6.1f} {100*self.percentage_success:>6.1f} {self.passed:>6} {self.failed:>6} {self.total:>6}"      
    def as_row(self):
        if self.summary_score == 0:
            self.summary_score = self.score
        return [
            self.test_id,
            self.summary_score,
            self.test_weight,
            self.percentage_success,
            self.passed,
            self.failed,
            self.total
            ]

    @classmethod
    def header_details(cls, writer):
        writer.writerow([
                'Test_Module',
                'Test_name',
                'Test_Parameters',
                'Outcome',
                'Setup_Duration',
                'Call_Duration',
                'Teardown_Duration'
            ])

    def report_details(self, set_name, writer):
        if len(self.children) > 0:
            for child in self.children:
                child.report_details(self.test_id, writer)
        else:
            for node in self._results['tests']:
                node_components = TestResult.test_extraction_w_params.search(node['nodeid'])

                # Only some tests will be built using parametrize fixtures
                if node_components is None:
                    node_components = TestResult.test_extraction_no_params.search(node['nodeid'])
                    params = ""
                else:
                    params = node_components['params']

                if node_components is None:
                    print(node['nodeid'])
                    pdb.set_trace()

                writer.writerow([
                    set_name,
                    node_components['test_name'],
                    params,
                    node['outcome'],
                    node['setup']['duration'],
                    node['call']['duration'],
                    node['teardown']['duration']
                ])


    def report_score(self, set_name, writer=None):
        for child in self.children:
            if writer:
                writer.writerow([set_name] + child.as_row())
            print(child.as_str())
        if writer:
            writer.writerow([set_name] + self.as_row())
        summary_line = self.as_str()
        print("-" * len(summary_line))
        print(summary_line + "\n")
        return self.score