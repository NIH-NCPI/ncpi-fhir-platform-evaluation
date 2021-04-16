#!/usr/bin/env python
import logging
from importlib import reload
import sys
from csv import writer
import pdb

from argparse import ArgumentParser, FileType
from yaml import safe_load
from ncpi_fhir_client.fhir_client import FhirClient
from ncpi_fhir_client import fhir_auth
from fhir_walk.config import DataConfig

from fhireval import __name__ as libpath
import fhireval.test_suite
from fhireval.runner import Runner, __name__ as runner_path
from collections import defaultdict
from pathlib import Path
from fhireval.test_result import TestResult

import pdb

# Keep all of our tests in child directory, test_suite
base_dir = Path(libpath)
suite_path = base_dir / "test_suite"


def example_config(writer, auth_type=None):
    """Returns a block of text containing one or all possible auth modules example configurations"""

    modules = fhir_auth.get_modules()
    print(
        f"""# Example Hosts Configuration.
# 
# This is a basic yaml file (yaml.org) where each root level tag represents a 
# system "name" and it's children's keys represent key/values to assign to a 
# host configuration which includes the authentication details.
#
# All host entries should have the following key/values:
# host_desc             - This is just a short description which can be used
#                         for log names or whatnot
# target_service_url    - This is the URL associated with the actual API 
# auth_type             - This is the module name for the authentication used
#                         by the specified host
#
# Please note that there can be multiple hosts that use the same authentication
# mechanism. Users must ensure that each host has a unique "key" """,
        file=writer,
    )
    for key in modules.keys():
        if auth_type is None or auth_type == key:
            other_entries = {
                "host_desc": f"Example {key}",
                "target_service_url": "https://example.fhir.server/R4/fhir",
            }

            modules[key].example_config(writer, other_entries)


def find_test_modules(root_dir=None):
    """Aggregate the list of test files and aggregate them together with their parent 'module' directory

    returns {dirname=>[test_file1, test_file2, ...]}
    """
    global suite_path

    if root_dir is None:
        root_dir = suite_path

    # Now, we expect that each of those tests lives in a "test set" which will be a
    # python module with a couple of special variables
    module_files = defaultdict(list)
    files = list(suite_path.glob("**/test_*.py"))

    for file in files:
        module_files[str(file.parent.name)].append(file)

    return module_files


if __name__ == "__main__":
    host_config_filename = Path("fhir_hosts")

    if not host_config_filename.is_file() or host_config_filename.stat().st_size == 0:
        example_config(sys.stdout)
        sys.stderr.write(
            f"""
A valid host configuration file, fhir_hosts, must exist in cwd and was not 
found. Example configuration has been written to stout providing examples 
for each of the auth types currently supported.\n"""
        )
        sys.exit(1)

    host_config = safe_load(host_config_filename.open("rt"))

    # Just capture the available environments to let the user
    # make the selection at runtime
    env_options = sorted(host_config.keys())

    module_files = find_test_modules()
    module_names = sorted([x for x in module_files.keys()])
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    parser = ArgumentParser(
        description="Run tests against a FHIR server to evaluate how well the server performs against other platforms."
    )
    parser.add_argument(
        "-e",
        "--env",
        choices=env_options,
        default=env_options[0],
        help=f"Remote configuration to be used to access the FHIR server",
    )
    parser.add_argument(
        "-m",
        "--module",
        choices=module_names,
        default=[],
        action="append",
        help="Name test_suite to be exercised. May be used multiple times (default is all tests).",
    )
    parser.add_argument(
        "--show-error-trace",
        action="store_true",
        help="Permit tests to generate back trace lists for failures (useful only for debugging problems)",
    )
    parser.add_argument(
        "-o",
        "--out",
        default="reports",
        type=str,
        help="Directory where reports will be written",
    )
    parser.add_argument(
        "-r",
        "--report-prefix",
        type=str,
        default="",
        help="Prefix to be used for report files (default is the name provided in RC file for selected environment)",
    )

    parser.add_argument(
        "-d",
        "--log-dir",
        type=str,
        default="logs",
        help="Directory for log to be written",
    )

    parser.add_argument(
        "--example_cfg",
        action="store_true",
        help="Write example configuration to stdout and exit. ",
    )

    parser.add_argument(
        "-l",
        "--log-level",
        choices=log_levels.keys(),
        default="ERROR",
        help="The minimum level of detail written to the log",
    )

    args = parser.parse_args()

    if args.example_cfg:
        example_config(sys.stdout)
        sys.exit(1)

    fhireval.test_suite.fhir_client = FhirClient(host_config[args.env])
    # pdb.set_trace()
    # config = DataConfig.config(env=args.env)
    if args.report_prefix.strip() == "":
        args.report_prefix = fhireval.test_suite.fhir_client.host_desc.lower().replace(
            " ", "_"
        )

    reload(logging)

    Path(args.log_dir).mkdir(parents=True, exist_ok=True)

    logfn = f"{args.log_dir}/{args.report_prefix}-evaluation.log"

    logging.basicConfig(
        filename=logfn,
        filemode="w",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=log_levels[args.log_level],
    )

    print(f"Logging to '{logfn}', level {args.log_level}.")
    fhireval.test_suite.fhir_client.init_log()
    if len(args.module) == 0:
        args.module = module_names

    test_runners = {}
    total_file_count = 0
    module_prefix = str(suite_path).replace("/", ".")
    for modulename in args.module:
        runner = Runner(f"{module_prefix}.{modulename}", module_files[modulename])
        test_runners[runner.set_id] = runner
        total_file_count = total_file_count + len(module_files[modulename])
        logging.info(
            f"Module Identified: {modulename} with {len(module_files[modulename])} test sets inside."
        )

    # Make sure we have a report directory
    report_dir = Path(args.out)
    report_dir.mkdir(exist_ok=True, parents=True)

    with open(report_dir / f"{args.report_prefix}.csv", "wt") as outf:
        logging.info(
            f"Running {total_file_count} test sets from {len(test_runners)} module(s)."
        )
        print(
            f"Running {total_file_count} test sets from {len(test_runners)} module(s)."
        )
        runner_flags = ["--json-report-file=none", "-v", "--disable-warnings"]
        if not args.show_error_trace:
            runner_flags.append("--tb=no")

        for runner in sorted(test_runners.keys()):
            test_runners[runner].perform_tests(runner_flags)

        total_score = 0

        heading = f"{'Test Name':<40} {'Score':<6} {'Max':<6} {'   %':6} {'#Pass':>6} {'#Fail':>6} {'#Tot':>6}"
        rpt_writer = writer(outf, delimiter=",", quotechar='"')
        rpt_writer.writerow(
            [
                "Module_Name",
                "Test_ID",
                "Score",
                "Total_Possible_Score",
                "Perc",
                "#Tests_Passed",
                "#Tests_Failed",
                "#Total_Test_Count",
            ]
        )

        print(heading)
        print("-" * len(heading))
        summary_result = TestResult(test_id="Final Score")
        for runner in sorted(test_runners.keys()):
            runner_summary = test_runners[runner].summary_result
            summary_result.add_child(runner_summary)
            total_score = total_score + runner_summary.report_score(
                test_runners[runner].set_name, rpt_writer
            )
        # perc = total_score / total_tested * 100
        summary = summary_result.as_str()
        # summary = f"{'Final Score':<40} {total_score:<6.1f} {summary_result.test_weight:<6.1f} {perc:>6.1f}% {total_passed:>6} {total_failed:>6} {total_tested:>6}"
        print("-" * len(summary))
        print(summary)
        logging.info(summary)
        rpt_writer.writerow(
            [f"{fhireval.test_suite.fhir_client.host_desc} Final Score"]
            + summary_result.as_row()
        )
        """
                'Final Score',
                total_score,
                summary_result.test_weight,
                perc, 
                total_passed,
                total_failed,
                total_tested])
        """
    with open(report_dir / f"{args.report_prefix}-detailed.csv", "wt") as outf:
        rpt_writer = writer(outf, delimiter=",", quotechar='"')
        TestResult.header_details(rpt_writer)

        for runner in sorted(test_runners.keys()):
            test_runners[runner].report_details(rpt_writer)
