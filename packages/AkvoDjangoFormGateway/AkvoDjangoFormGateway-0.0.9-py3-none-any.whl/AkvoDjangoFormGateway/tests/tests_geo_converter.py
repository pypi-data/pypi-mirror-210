from django.test import TestCase
from django.core.management import call_command
from AkvoDjangoFormGateway.models import (
    AkvoGatewayAnswer as Answers
)
from AkvoDjangoFormGateway.constants import QuestionTypes


class GeoConverterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        call_command(
            "gateway_form_seeder",
            "-f",
            "./backend/source/forms/1.json",
            "-t",
            True,
        )
        call_command(
            "fake_gateway_data_seeder",
            "-r",
            1,
            "-s",
            True,
        )

    def test_reverse_geo_code_from_prev_format(self):
        geo_answer = Answers.objects.filter(
                question__type=QuestionTypes.geo).first()
        self.assertIsInstance(geo_answer.options, list)
        self.assertIsInstance(geo_answer.options[0], float)
        self.assertIsInstance(geo_answer.options[1], float)
        geo_answer.options = ",".join(str(g) for g in geo_answer.options)
        geo_answer.save()
        self.assertIsInstance(geo_answer.options, str)
        self.assertIsNone(geo_answer.name)
        call_command("gateway_geo_converter")
        geo_answer = Answers.objects.filter(
                question__type=QuestionTypes.geo).first()
        self.assertIsInstance(geo_answer.name, str)

    def test_reverse_geo_code_from_new_format(self):
        geo_answer = Answers.objects.filter(
                question__type=QuestionTypes.geo).first()
        self.assertIsInstance(geo_answer.options, list)
        self.assertIsNone(geo_answer.name)
        geo_answer.name = None
        geo_answer.save()
        call_command("gateway_geo_converter")
        geo_answer = Answers.objects.filter(
                question__type=QuestionTypes.geo).first()
        self.assertIsInstance(geo_answer.name, str)
