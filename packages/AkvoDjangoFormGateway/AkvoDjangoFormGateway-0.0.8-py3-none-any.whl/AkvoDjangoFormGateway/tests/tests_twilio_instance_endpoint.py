from django.test import TestCase, Client
from django.core.management import call_command
from rest_framework import status
from AkvoDjangoFormGateway.feed import Feed
from AkvoDjangoFormGateway.models import (
    AkvoGatewayQuestion as Questions,
    AkvoGatewayAnswer as Answers,
)

client = Client()
feed = Feed()
# Tests
# consider that 8 digit phone number will
# skip to send twillio message
phone_number = "12345678"


class TwilioInstanceEndpointTestCase(TestCase):
    def setUp(self):
        call_command(
            "gateway_form_seeder",
            "-f",
            "./backend/source/forms/1.json",
            "-t",
            True,
        )

    def test_instance_not_found(self):
        form_id = 12345678
        response = client.post(
            f"/api/gateway/twilio/{form_id}?format=json",
            data={},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json(),
            {"detail": "Not found."},
        )

    def test_instance_request(self):
        form_id = 1
        # Send hi as first message
        reply_text = "hi"
        response = client.post(
            f"/api/gateway/twilio/{form_id}?format=json",
            {"From": f"whatsapp:+{phone_number}", "Body": reply_text},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No welcome message and select forms
        self.assertNotEqual(response.json(), feed.get_list_form())

        # Got the first question
        fq = Questions.objects.filter(form=form_id).order_by("order").first()
        self.assertEqual(response.json(), f"{fq.order}. {fq.text}")

        # Survey session is created
        datapoint = feed.get_draft_datapoint(phone=phone_number)

        # Answer first question
        reply_text = "test complaint"
        response = client.post(
            f"/api/gateway/twilio/{form_id}",
            {"Body": reply_text, "From": f"whatsapp:+{phone_number}"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            feed.validate_answer(text=reply_text, question=fq, data=datapoint),
            True,
        )
        # 2. Photo question
        question = feed.get_question(form=datapoint.form, data=datapoint)
        self.assertEqual(response.json(), f"{question.order}. {question.text}")

        # Answer photo question
        image_type = "image/jpg"
        image = "http://twilio.example/image/CaseSensiTiVe2.jpg"
        response = client.post(
            f"/api/gateway/twilio/{form_id}",
            {
                "Body": "",
                "From": f"whatsapp:+{phone_number}",
                "MediaContentType0": image_type,
                "MediaUrl0": image,
            },
        )
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

        # 3. GPS question
        question = feed.get_question(form=datapoint.form, data=datapoint)
        self.assertEqual(response.json(), f"{question.order}. {question.text}")

        # Answer GPS question
        lat = "-79121.1"
        lng = "112121"
        text = feed.get_answer_text(
            body=None,
            image_url=None,
            lat=lat,
            lng=lng,
        )
        response = client.post(
            f"/api/gateway/twilio/{form_id}",
            {
                "Body": "",
                "From": f"whatsapp:+{phone_number}",
                "Latitude": lat,
                "Longitude": lng,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text=text,
                question=question,
                data=datapoint,
            ),
            True,
        )

        # 4. Phone question
        question = feed.get_question(form=datapoint.form, data=datapoint)

        # Answer Phone question
        reply_text = "0829111"
        json_form = {
            "Body": reply_text,
            "From": f"whatsapp:+{phone_number}",
        }
        response = client.post(f"/api/gateway/twilio/{form_id}", json_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text=reply_text,
                question=question,
                data=datapoint,
            ),
            True,
        )

        # 5. Single option question
        question = feed.get_question(form=datapoint.form, data=datapoint)

        # Answer Single option question
        reply_text = "Option 2"
        json_form = {
            "Body": reply_text,
            "From": f"whatsapp:+{phone_number}",
        }
        response = client.post(f"/api/gateway/twilio/{form_id}", json_form)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            feed.validate_answer(
                text=reply_text,
                question=question,
                data=datapoint,
            ),
            True,
        )

        # 6. Multiple option question
        question = feed.get_question(form=datapoint.form, data=datapoint)

        # Answer Multiple option question
        reply_text = "MULTi 1, Multi 3"
        response = client.post(
            f"/api/gateway/twilio/{form_id}",
            {
                "Body": reply_text,
                "From": f"whatsapp:+{phone_number}",
            },
        )
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
        self.assertEqual(answer.options, ["multi 1", "multi 3"])

        # 7. Date question
        question = feed.get_question(form=datapoint.form, data=datapoint)

        # Answer date question
        reply_text = "15-12-1999"
        response = client.post(
            f"/api/gateway/twilio/{form_id}",
            {
                "Body": reply_text,
                "From": f"whatsapp:+{phone_number}",
            },
        )
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
