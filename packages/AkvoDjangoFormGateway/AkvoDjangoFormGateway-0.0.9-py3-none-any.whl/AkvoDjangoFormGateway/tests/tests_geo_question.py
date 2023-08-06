from unittest.mock import patch
from django.test import TestCase
from django.conf import settings
from django.core.management import call_command
from AkvoDjangoFormGateway.models import (
    AkvoGatewayData as FormData,
    AkvoGatewayQuestion as Questions,
)
from AkvoDjangoFormGateway.constants import QuestionTypes
from AkvoDjangoFormGateway.utils.services import geo_service, store_geo_service

google_map_api_key = settings.GOOGLE_MAPS_API_KEY


class GeoQuestionTestCase(TestCase):
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

    def tearDown(self):
        # Clean up any resources or data after each test
        super().tearDown()

    def test_geo_service_with_key(self):
        lat = -7.38984
        lng = 109.4935524
        res = geo_service(
            latitude=lat, longitude=lng, api_key=google_map_api_key
        )
        self.assertEqual(list(res), ["plus_code", "results", "status"])
        self.assertEqual(res["status"], "OK")
        self.assertEqual(res["plus_code"]["global_code"], "6P4FJF6V+3C7")
        self.assertEqual(
            res["results"][0]["place_id"], "ChIJdc0ZWgRVZS4ReRrJz_q9TxU"
        )

    def test_geo_service_without_key(self):

        lat = -7.38984
        lng = 109.4935524
        res = geo_service(
            latitude=lat, longitude=lng, api_key=None
        )
        self.assertEqual(res, None)

    def test_geo_service_without_lng(self):
        lat = -7.38984
        lng = None
        res = geo_service(
            latitude=lat, longitude=lng, api_key=google_map_api_key
        )
        self.assertEqual(res, None)

    def test_geo_service_without_lat(self):
        lat = None
        lng = 109.4935524
        res = geo_service(
            latitude=lat, longitude=lng, api_key=google_map_api_key
        )
        self.assertEqual(res, None)

    def test_geo_service_without_lat_lng(self):
        lat = None
        lng = None
        res = geo_service(
            latitude=lat, longitude=lng, api_key=google_map_api_key
        )
        self.assertEqual(res, None)

    def test_geo_service_without_wrong_key_format(self):
        lat = -7.38984
        lng = 109.4935524
        res = geo_service(
            latitude=lat, longitude=lng, api_key=["secret", "key"]
        )
        self.assertEqual(res, None)

    def test_store_geo_service(self):
        datapoint = FormData.objects.first()

        # check if all questions are answered
        answers = datapoint.ag_data_answer.all()
        self.assertEqual(
            len(answers), datapoint.form.ag_form_questions.all().count()
        )

        # check geolocation answer
        question = Questions.objects.filter(type=QuestionTypes.geo).first()
        geo_answer = datapoint.ag_data_answer.filter(question=question).first()
        self.assertNotEqual(geo_answer, None)

        # formatted_address should not be empty or null
        geo_answer = store_geo_service(
            answer=geo_answer, api_key=google_map_api_key
        )
        self.assertNotEqual(geo_answer.name, None)

    @patch("AkvoDjangoFormGateway.utils.services.requests.get")
    def test_exception_handling(self, mock_get):
        # Configure the mock to raise an exception when called
        mock_get.side_effect = Exception("Mocked exception")

        lat = -7.38984
        lng = 109.4935524
        res = geo_service(
            latitude=lat, longitude=lng, api_key=google_map_api_key
        )

        # Assert that the result matches the expected behavior
        self.assertIsNone(res)
