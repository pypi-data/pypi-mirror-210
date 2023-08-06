import os
from django.test import TestCase


class EnvironmentValueTest(TestCase):
    def test_environment_variables_present(self):
        expected_variables = [
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER",
        ]

        for variable in expected_variables:
            with self.subTest(variable=variable):
                self.assertIn(variable, os.environ)
