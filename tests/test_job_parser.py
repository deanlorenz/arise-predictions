import unittest
import logging
import sys

from tests.utils.logger_redirector import LoggerRedirector
from preprocessing import job_parser

"""
Tests for job parser.
"""

logger = logging.getLogger('test-logger')

logging.basicConfig(
    format="%(asctime)s %(module)s %(levelname)s: %(message)s",
    level=logging.INFO,
    stream=sys.stdout)


class TestJobParser(unittest.TestCase):

    def setUp(self):
        # unittest has reassigned sys.stdout and sys.stderr by this point
        LoggerRedirector.redirect_loggers(fake_stdout=sys.stdout, 
                                          fake_stderr=sys.stderr)

    def test_get_job_outputs(self):
        """
        Test that we can get the job outputs parsed from job_spec.yaml
        """
        loaded_job_spec = job_parser.parse_job_spec(
            "tests/resources/job_spec.yaml")
        target_variables = sorted(list(loaded_job_spec[1]))
        self.assertTrue(1, len(target_variables))
        self.assertIn("tokens_per_second", target_variables)
