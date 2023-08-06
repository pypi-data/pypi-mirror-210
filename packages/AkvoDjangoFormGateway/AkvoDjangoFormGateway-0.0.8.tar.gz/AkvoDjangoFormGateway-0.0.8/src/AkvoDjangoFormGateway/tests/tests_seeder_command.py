from io import StringIO
from django.test.utils import override_settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from AkvoDjangoFormGateway.models import AkvoGatewayForm as Forms


@override_settings(USE_TZ=False)
class FormSeederTestCase(TestCase):
    def call_gateway_form_seeder_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "gateway_form_seeder",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def call_fake_gateway_data_seeder_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "fake_gateway_data_seeder",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_call_command(self):
        forms = Forms.objects.all().delete()
        json_forms = ["Form Complaint"]
        # RUN SEED NEW FORM
        output = self.call_gateway_form_seeder_command(
            "-f", "./backend/source/forms/1.json"
        )
        if output:
            output = list(filter(lambda x: len(x), output.split("\n")))
        forms = Forms.objects.all()
        self.assertEqual(forms.count(), 1)

        for form in forms:
            self.assertIn(
                f"Form Created | {form.name} V{form.version}", output
            )
            self.assertIn(form.name, json_forms)
        # RUN UPDATE EXISTING FORM
        output = self.call_gateway_form_seeder_command(
            "-f", "./backend/source/forms/1.json"
        )
        if output:
            output = list(filter(lambda x: len(x), output.split("\n")))
        for form in forms:
            if form.version == 2:
                self.assertIn(
                    f"Form Updated | {form.name} V{form.version}", output
                )
        # RUN FAKE DATA SEEDER
        output = self.call_fake_gateway_data_seeder_command("-t", True)
        form = Forms.objects.get(name="Form Complaint")
        self.assertIn(output, form.name)

    def test_updating_form(self):
        out = StringIO()
        err = StringIO()
        first_version = "./backend/source/forms/1.json"
        call_command(
            "gateway_form_seeder",
            "--file",
            first_version,
            stdout=out,
            stderr=err,
        )
        self.assertEqual(out.getvalue(), "Form Created | Form Complaint V1\n")

        out = StringIO()
        err = StringIO()
        second_version = "./backend/source/forms/1-update-test.json"
        call_command(
            "gateway_form_seeder",
            "--file",
            second_version,
            stdout=out,
            stderr=err,
        )
        self.assertEqual(out.getvalue(), "Form Updated | Form Complaint V2\n")

    def test_seeder_raises_command_error(self):
        invalid_json_file = "./backend/source/forms/invalid.json"

        # Redirect stdout and stderr to StringIO to capture the output
        out = StringIO()
        err = StringIO()

        try:
            call_command(
                "gateway_form_seeder",
                "--file",
                invalid_json_file,
                stdout=out,
                stderr=err,
            )
            self.fail("CommandError was not raised")
        except CommandError as e:
            # Assert that the exception was raised
            self.assertEqual(
                str(e),
                f"[Errno 2] No such file or directory: '{invalid_json_file}'",
            )
        finally:
            # Print the captured output for debugging purposes
            print("stdout:", out.getvalue())
            print("stderr:", err.getvalue())
