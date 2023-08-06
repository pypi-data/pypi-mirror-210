import json
from datetime import datetime
from twilio.rest import Client
from .models import (
    AkvoGatewayForm as Forms,
    AkvoGatewayData as FormData,
    AkvoGatewayAnswer as Answers,
    AkvoGatewayQuestion as Questions,
)
from .constants import QuestionTypes, StatusTypes
from .utils.validation import (
    is_number,
    is_valid_string,
    is_date,
    is_valid_geolocation,
    is_valid_image,
)


class Feed:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self):
        self.welcome = ["hi", "hello", "info"]

    def get_init_survey_session(self, text: str):
        init = False
        form_id = None
        if "#" in text:
            info = str(text).split("#")
            form_id = info[1]
            init = len(info) == 2 and str(info[0]).lower() == "ready"
        return init, form_id

    def get_form(self, form_id: int = None, data: FormData = None) -> Forms:
        survey = None
        if data:
            survey = data.form
        if form_id:
            survey = Forms.objects.get(pk=form_id)
        return survey

    def get_last_question(self, data: FormData) -> Questions:
        if data.form.ag_form_questions.count() == data.ag_data_answer.count():
            # Return null if all questions are answered
            return None
        aws = data.ag_data_answer.all()
        ids = [aw.question.id for aw in aws]
        qs = (
            data.form.ag_form_questions.exclude(id__in=ids)
            .order_by("order")
            .first()
        )
        return qs

    def get_question(
        self, form: Forms = None, data: FormData = None
    ) -> Questions:
        qs = None
        if form:
            qs = form.ag_form_questions.all().first()
        if data and data.ag_data_answer.count():
            qs = self.get_last_question(data=data)
        return qs

    def get_draft_datapoint(self, phone: str) -> FormData:
        datapoint = (
            FormData.objects.filter(phone=phone, status=StatusTypes.draft)
            .all()
            .first()
        )
        return datapoint

    def get_list_form(self) -> str:
        forms = Forms.objects.all()
        msg = "Welcome to Akvo Survey\n\n."
        msg += "*Please select the form below:*\n"
        for f in forms:
            msg += f"- #{f.id} | {f.name}\n"
        msg += (
            "by replying to this message with the following format to start a"
            " new survey\n"
        )
        msg += "*READY#FORM_ID* (e.g *READY#1*)"
        return msg

    def validate_answer(
        self,
        text: str,
        question: Questions,
        data: FormData,
        image_type: str = None,
    ) -> None:
        # is alphanumeric by default
        is_valid = is_valid_string(input=text)
        if question.type == QuestionTypes.number:
            is_valid = is_number(input=text)
        if question.type == QuestionTypes.date:
            is_valid = is_date(input=text)
        if question.type == QuestionTypes.geo:
            is_valid = is_valid_geolocation(json_string=text)
        if question.type == QuestionTypes.photo:
            is_valid = is_valid_image(image_type=image_type)
        if question.type in [
            QuestionTypes.option,
            QuestionTypes.multiple_option,
        ]:
            lto = [str(o).lower() for o in str(text).split(",")]
            opt = [
                str(o.name).lower()
                for o in question.ag_question_question_options.all()
            ]
            count = len(set(lto).intersection(set(opt)))
            is_valid = count > 0
        return is_valid

    def insert_answer(self, text: str, question: Questions, data: FormData):
        name = None
        value = None
        options = None
        if question.type == QuestionTypes.number:
            value = text
        if question.type == QuestionTypes.geo:
            options = text
        if question.type == QuestionTypes.date:
            date_format = "%d-%m-%Y"
            dv = datetime.strptime(text, date_format)
            name = dv.strftime(date_format)
        if question.type in [
            QuestionTypes.option,
            QuestionTypes.multiple_option,
        ]:
            options = [str(t.strip()) for t in text.split(",")]
        if not name and not value and not options:
            name = text
        return Answers.objects.create(
            question=question,
            data=data,
            name=name,
            value=value,
            options=options,
        )

    def set_as_completed(self, data: FormData) -> None:
        data.status = StatusTypes.submitted
        data.save()

    def get_answer_text(
        self,
        body: str = None,
        image_url: str = None,
        lat: str = None,
        lng: str = None,
    ) -> str:
        text = body
        if image_url:
            text = image_url
            return text
        if lat and lng:
            text = json.dumps(
                [
                    lat,
                    lng,
                ]
            )
        return str(text).lower()

    def send_to_client(
        self,
        client: Client,
        from_number: str,
        body: str,
        to_number: str,
        type: str = "whatsapp",
    ):
        valid_number = len(to_number) > 8
        if valid_number:
            client.messages.create(
                from_=f"{type}:+{from_number}",
                body=body,
                to=f"{type}:+{to_number}",
            )

    def show_options(self, question: Questions) -> str:
        text = ""
        if question.type in [
            QuestionTypes.option,
            QuestionTypes.multiple_option,
        ]:
            text += "\n"
            for opt in question.ag_question_question_options.all():
                text += f"- {opt.name}\n"
            if question.type == QuestionTypes.multiple_option:
                text += (
                    "\nYou can select more than one separated by commas. *eg:"
                    " op1,op2*"
                )
        return text
