from django.test import TestCase, Client
from django.core.management import call_command
from AkvoDjangoFormGateway.feed import Feed
from AkvoDjangoFormGateway.models import (
    AkvoGatewayQuestion as Questions,
    AkvoGatewayAnswer as Answers,
)
from AkvoDjangoFormGateway.serializers import TwilioSerializer

client = Client()
feed = Feed()
# Tests
# consider that 8 digit phone number will
# skip to send twillio message
phone_number = "12345678"


class TwilioEndpointTestCase(TestCase):
    def setUp(self):
        call_command(
            "gateway_form_seeder",
            "-f",
            "./backend/source/forms/1.json",
            "-t",
            True,
        )

    def test_request_type(self):
        # GET not allowed
        response = client.get("/api/gateway/twilio/")
        self.assertEqual(response.status_code, 405)

        # POST allowed
        response = client.post("/api/gateway/twilio/")
        self.assertEqual(response.status_code, 200)

    def test_welcome_message(self):
        json_form = {"Body": "hi", "From": f"whatsapp:+{phone_number}"}
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), feed.get_list_form())

    def test_start_survey_session(self):
        reply_text = "ready#1"

        init, form_id = feed.get_init_survey_session(text=reply_text)
        json_form = {"Body": reply_text, "From": f"whatsapp:+{phone_number}"}
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 200)

        datapoint = feed.get_draft_datapoint(phone=phone_number)
        survey = feed.get_form(form_id=form_id, data=datapoint)
        question = feed.get_question(form=survey)
        # First question shown when survey session started
        # This response related to line code: 47
        self.assertEqual(response.json(), f"{question.order}. {question.text}")

        # datapoint is exist
        self.assertEqual(datapoint.phone, phone_number)
        # Form id equal with datapoint
        self.assertEqual(survey.id, datapoint.form.id)

        # Answer First question
        reply_text = "text answer"
        json_form = {"Body": reply_text, "From": f"whatsapp:+{phone_number}"}
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 200)

        # Photo question
        question = feed.get_question(form=survey, data=datapoint)
        self.assertEqual(response.json(), f"{question.order}. {question.text}")

        # Answer wrong photo question no MediaContentType0
        image = "http://twilio.example/image/caseSensiT1Ve.png"
        json_form = {
            "Body": "",
            "From": f"whatsapp:+{phone_number}",
            "MediaUrl0": image,
        }
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 400)
        serializer = TwilioSerializer(data=json_form)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            response.json(),
            {
                "non_field_errors": [
                    "MediaContentType0 is required when MediaUrl0 is present."
                ]
            },
        )

        image_type = "image/png"
        json_form = {
            "Body": "",
            "From": f"whatsapp:+{phone_number}",
            "MediaContentType0": image_type,
        }
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 400)
        serializer = TwilioSerializer(data=json_form)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            response.json(),
            {
                "non_field_errors": [
                    "MediaUrl0 is required when MediaContentType0 is present."
                ]
            },
        )

        # Answer right photo question
        json_form = {
            "Body": "",
            "From": f"whatsapp:+{phone_number}",
            "MediaContentType0": image_type,
            "MediaUrl0": image,
        }
        response = client.post("/api/gateway/twilio/", json_form)
        stored_image = Answers.objects.filter(question=question).first().name
        self.assertEqual(image, stored_image)
        self.assertNotEqual(image.lower(), stored_image)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text="",
                question=question,
                data=datapoint,
                image_type=image_type,
            ),
            True,
        )

        # GPS question
        question = feed.get_question(form=survey, data=datapoint)

        # Answer Wrong GPS question
        lat = "-9.1161"
        json_form = {
            "Body": "",
            "From": f"whatsapp:+{phone_number}",
            "Latitude": lat,
        }
        text = feed.get_answer_text(
            body=None,
            image_url=None,
            lat=lat,
        )
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 400)
        serializer = TwilioSerializer(data=json_form)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            response.json(),
            {
                "non_field_errors": [
                    "Longitude is required when Latitude is present."
                ]
            },
        )

        lng = "10.11"
        json_form = {
            "Body": "",
            "From": f"whatsapp:+{phone_number}",
            "Longitude": lng,
        }
        text = feed.get_answer_text(
            body=None,
            image_url=None,
            lng=lng,
        )
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 400)
        serializer = TwilioSerializer(data=json_form)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            response.json(),
            {
                "non_field_errors": [
                    "Latitude is required when Longitude is present."
                ]
            },
        )

        # Answer GPS question
        json_form = {
            "Body": "",
            "From": f"whatsapp:+{phone_number}",
            "Latitude": lat,
            "Longitude": lng,
        }
        text = feed.get_answer_text(
            body=None,
            image_url=None,
            lat=lat,
            lng=lng,
        )
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text=text,
                question=question,
                data=datapoint,
            ),
            True,
        )

        # Phone question
        question = feed.get_question(form=survey, data=datapoint)
        # Answer Phone question
        reply_text = "0829111"
        json_form = {
            "Body": reply_text,
            "From": f"whatsapp:+{phone_number}",
        }
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text=reply_text,
                question=question,
                data=datapoint,
            ),
            True,
        )

        # Single option question
        question = feed.get_question(form=survey, data=datapoint)
        # Answer Single option question
        reply_text = "optiOn 1"
        json_form = {
            "Body": reply_text,
            "From": f"whatsapp:+{phone_number}",
        }
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text=reply_text,
                question=question,
                data=datapoint,
            ),
            True,
        )

        # Multiple option question
        question = feed.get_question(form=survey, data=datapoint)
        # Answer Multiple option question
        reply_text = "multi 1, Multi 2"
        json_form = {
            "Body": reply_text,
            "From": f"whatsapp:+{phone_number}",
        }
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text=reply_text,
                question=question,
                data=datapoint,
            ),
            True,
        )
        answer = Answers.objects.filter(
            data=datapoint, question=question
        ).first()
        self.assertEqual(answer.options, ["multi 1", "multi 2"])

        # Date question
        question = feed.get_question(form=survey, data=datapoint)
        # Answer date question
        reply_text = "15-12-1999"
        json_form = {
            "Body": reply_text,
            "From": f"whatsapp:+{phone_number}",
        }
        response = client.post("/api/gateway/twilio/", json_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text=reply_text,
                question=question,
                data=datapoint,
            ),
            True,
        )
        answer = Answers.objects.filter(
            data=datapoint, question=question
        ).first()
        self.assertEqual(answer.name, reply_text)
        self.assertEqual(response.json(), "Thank you!")

    def test_show_options(self):
        opt_question = Questions.objects.get(pk=5)
        opt_question_output = "\n- option 1\n- option 2\n"
        self.assertEqual(
            feed.show_options(question=opt_question), opt_question_output
        )

        multi_opt_q = Questions.objects.get(pk=6)
        multi_opt_output = (
            "\n- multi 1\n- multi 2\n- multi 3\n\nYou can select more than one"
            " separated by commas. *eg: op1,op2*"
        )
        self.assertEqual(
            feed.show_options(question=multi_opt_q), multi_opt_output
        )

        non_opt_q = Questions.objects.get(pk=1)
        self.assertEqual(feed.show_options(question=non_opt_q), "")

    def test_get_init_survey_session(self):
        test1 = "ready#1"
        test2 = "#1"
        test3 = "1"
        init, form_id = feed.get_init_survey_session(text=test1)
        self.assertEqual(init, True)
        init, form_id = feed.get_init_survey_session(text=test2)
        self.assertEqual(init, False)
        init, form_id = feed.get_init_survey_session(text=test3)
        self.assertEqual(init, False)
