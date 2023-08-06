import unittest
import sys
import json

sys.path.append('..')

from FCSAPIAccess import *

with open("../credentials.json") as f:
    credentials = json.load(f)


class TestCaseComparisons(unittest.TestCase):
    def test_correct_credentials(self):
        FCSAPIAccess(
            credentials["client_id"], credentials["client_secret"],
            []
        )

    def test_expired_access_token(self):
        access = FCSAPIAccess(
            credentials["client_id"], credentials["client_secret"],
            Scope.FULL_ACCESS
        )

        access.set_access_token(credentials["expired_access"], credentials["expired_refresh"])
        self.assertNotEqual(
            access.project.list_directories(),
            {'error': 'expired_code', 'error_description': 'The provided code is expired.'}
        )

    def test_incorrect_credentials(self):
        self.assertRaises(
            InvalidGrantException,
            lambda: FCSAPIAccess(
                credentials["client_id"] + "BAD", credentials["client_secret"],
                Scope.FULL_ACCESS
            )
        )


if __name__ == '__main__':
    unittest.main()
