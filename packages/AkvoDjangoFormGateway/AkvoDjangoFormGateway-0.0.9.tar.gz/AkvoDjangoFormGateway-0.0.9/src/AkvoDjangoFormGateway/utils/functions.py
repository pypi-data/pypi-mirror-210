import random
from datetime import datetime, timedelta, time
from faker import Faker
from django.utils import timezone
from django.utils.timezone import make_aware

from AkvoDjangoFormGateway.models import (
    AkvoGatewayForm as Forms,
    AkvoGatewayData as FormData,
    AkvoGatewayAnswer as Answers,
)
from AkvoDjangoFormGateway.constants import QuestionTypes, StatusTypes


fake = Faker()


def get_answer_value(answer: Answers):
    if answer.question.type in [
        QuestionTypes.option,
        QuestionTypes.multiple_option,
    ]:
        return answer.options
    if answer.question.type == QuestionTypes.geo:
        return {
            "lat": answer.options[0],
            "lng": answer.options[1],
            "address": answer.name
        }
    elif answer.question.type == QuestionTypes.number:
        return answer.value
    else:
        return answer.name


def set_answer_option(data, question):
    option = None
    if question.type == QuestionTypes.option:
        option = [
            question.ag_question_question_options.order_by("?").first().name
        ]
    elif question.type == QuestionTypes.multiple_option:
        option = list(
            question.ag_question_question_options.order_by("?").values_list(
                "name", flat=True
            )[
                : fake.random_int(
                    min=2, max=question.ag_question_question_options.count()
                )
            ]
        )
    return option


def set_answer_data(data, question):
    name = None
    value = None
    option = set_answer_option(data, question)

    if question.type == QuestionTypes.geo:
        option = data.geo
    elif question.type == QuestionTypes.text:
        name = fake.sentence(nb_words=3)
    elif question.type == QuestionTypes.number:
        value = fake.random_int(min=10, max=50)
    elif question.type == QuestionTypes.photo:
        name = fake.image_url()
    elif question.type == QuestionTypes.date:
        name = fake.date_between_dates(
            date_start=timezone.datetime.now().date() - timedelta(days=90),
            date_end=timezone.datetime.now().date(),
        ).strftime("%d-%m-%Y")
    else:
        pass
    return name, value, option


def add_fake_answers(data: FormData, submitted: bool = False) -> None:
    form = data.form
    questions = form.ag_form_questions.all()
    number_of_answered = (
        questions.count()
        if submitted
        else random.choice(form.ag_form_questions.values_list("id", flat=True))
    )
    for index, question in enumerate(questions):
        if index < number_of_answered:
            name, value, option = set_answer_data(data, question)
            Answers.objects.create(
                data=data,
                question=question,
                name=name,
                value=value,
                options=option,
            )


def seed_data(repeat: int, test: bool = False, submitted: bool = False):
    for form in Forms.objects.all():
        if not test:
            print(f"\nSeeding - {form.name}")
        for i in range(repeat):
            now_date = datetime.now()
            start_date = now_date - timedelta(days=5 * 365)
            created = fake.date_between(start_date, now_date)
            created = datetime.combine(created, time.min)
            lat = fake.latitude()
            lng = fake.longitude()
            geo_value = [float(lat), float(lng)]
            data = FormData.objects.create(
                form=form,
                name=fake.pystr_format(),
                phone=fake.phone_number(),
                geo=geo_value,
            )
            data.created = make_aware(created)
            data.save()
            add_fake_answers(data=data, submitted=submitted)
            number_of_answered = Answers.objects.filter(data=data.id).count()
            if submitted:
                data.status = StatusTypes.submitted
                data.save()
            if len(form.ag_form_questions.all()) == number_of_answered:
                data.status = StatusTypes.submitted
                data.save()
