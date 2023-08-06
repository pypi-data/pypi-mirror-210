from django.test import TestCase, Client
from django.core.management import call_command
from rest_framework import status
from AkvoDjangoFormGateway.models import (
    AkvoGatewayData as FormData,
    AkvoGatewayAnswer as Answers,
)
from AkvoDjangoFormGateway.serializers import (
    ListDataSerializer,
    DetailDataSerializer,
)
from AkvoDjangoFormGateway.constants import QuestionTypes

client = Client()

TOTAL = 20
PER_PAGE = 10


class TwilioDataEndpointTestCase(TestCase):
    def setUp(self):
        call_command(
            "gateway_form_seeder",
            "-f",
            "./backend/source/forms/1.json",
            "-t",
            True,
        )
        call_command(
            "fake_gateway_data_seeder", "-r", TOTAL, "-t", True, "-s", True
        )

    def test_list_endpoint(self):
        response = client.post("/api/gateway/data/")
        self.assertEqual(response.status_code, 405)
        res = response.data

        response = client.get("/api/gateway/data/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            list(response.data), ["current", "total", "total_page", "data"]
        )
        res = response.data
        self.assertEqual(res["total"], 20)
        self.assertEqual(res["current"], 1)
        self.assertEqual(res["total_page"], 2)

    def test_get_first_10_items(self):
        queryset = FormData.objects.all()[:PER_PAGE]
        serializer = ListDataSerializer(queryset, many=True)

        response = client.get("/api/gateway/data/?page=1")
        res = response.data
        self.assertEqual(res["total"], 20)
        self.assertEqual(res["current"], 1)
        self.assertEqual(res["total_page"], 2)
        self.assertEqual(res["data"], serializer.data)

    def test_get_last_10_items(self):
        queryset = FormData.objects.all()[PER_PAGE:]
        serializer = ListDataSerializer(queryset, many=True)

        response = client.get("/api/gateway/data/?page=2")
        res = response.data

        self.assertEqual(res["total"], 20)
        self.assertEqual(res["current"], 2)
        self.assertEqual(res["total_page"], 2)
        self.assertEqual(res["data"], serializer.data)

    def test_pagination_endpoint(self):
        response = client.get("/api/gateway/data/?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        res = response.data
        self.assertEqual(res["current"], 2)

    def test_pagination_invalid(self):
        response = client.get("/api/gateway/data/?page=3")
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res["detail"], "Invalid page.")

    def test_success_retrieve_endpoint(self):
        data = FormData.objects.first()
        response = client.get(f"/api/gateway/data/{data.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = DetailDataSerializer(instance=data)
        self.assertEqual(
            list(response.json()),
            [
                "id",
                "status",
                "form",
                "name",
                "phone",
                "geo",
                "created",
                "updated",
                "answers",
            ],
        )
        self.assertEqual(response.data, serializer.data)

    def test_error_404_retrieve_endpoint(self):
        response = client.get("/api/gateway/data/1234/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_answer_text_content(self):
        answer = Answers.objects.filter(
            question__type=QuestionTypes.text
        ).first()
        response = client.get(f"/api/gateway/data/{answer.data.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data
        res_answer = list(
            filter(lambda x: x["id"] == answer.id, res["answers"])
        )
        self.assertEqual(answer.name, res_answer[0]["value"])

    def test_answer_value_content(self):
        answer = Answers.objects.filter(
            question__type=QuestionTypes.number
        ).first()
        response = client.get(f"/api/gateway/data/{answer.data.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data
        res_answer = list(
            filter(lambda x: x["id"] == answer.id, res["answers"])
        )
        self.assertEqual(answer.value, res_answer[0]["value"])

    def test_answer_options_value(self):
        answer = Answers.objects.filter(
            question__type=QuestionTypes.multiple_option
        ).first()
        response = client.get(f"/api/gateway/data/{answer.data.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data
        res_answer = list(
            filter(lambda x: x["id"] == answer.id, res["answers"])
        )
        self.assertEqual(answer.options, res_answer[0]["value"])
