from twilio.rest import Client
from django.conf import settings

from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes
from rest_framework.viewsets import (
    ModelViewSet,
    ViewSet,
    GenericViewSet,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import (
    AkvoGatewayForm as Forms,
    AkvoGatewayData as FormData,
)
from .serializers import (
    ListFormSerializer,
    TwilioSerializer,
    ListDataSerializer,
    DetailDataSerializer,
)
from .constants import StatusTypes
from .feed import Feed

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
from_number = settings.TWILIO_PHONE_NUMBER


@permission_classes([AllowAny])
class CheckView(GenericViewSet):
    def check(self, request):
        return Response({"message": settings.TWILIO_ACCOUNT_SID})


class AkvoFormViewSet(ModelViewSet):
    serializer_class = ListFormSerializer
    queryset = Forms.objects.all()


class TwilioViewSet(ViewSet):
    def create(self, request, form_instance: Forms = None):
        serializer = TwilioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        feed = Feed()

        image_type = serializer.validated_data.get("MediaContentType0")
        image_url = serializer.validated_data.get("MediaUrl0")
        phone = serializer.data.get("phone")
        body = serializer.validated_data.get("Body")
        lat = serializer.validated_data.get("Latitude")
        lng = serializer.validated_data.get("Longitude")
        text = feed.get_answer_text(
            body=body,
            image_url=image_url,
            lat=lat,
            lng=lng,
        )
        init, form_id = feed.get_init_survey_session(text=text)
        datapoint = feed.get_draft_datapoint(phone=phone)
        survey = (
            form_instance
            if form_instance
            else feed.get_form(form_id=form_id, data=datapoint)
        )
        lq = feed.get_question(form=survey, data=datapoint)
        message = None
        if text in feed.welcome and not datapoint and not form_instance:
            message = feed.get_list_form()

        new_datapoint = not datapoint and phone and len(str(phone).strip())
        init_session = form_instance or init
        if new_datapoint and init_session:
            # create new survey session by creating new datapoint
            FormData.objects.create(
                form=survey,
                phone=phone,
                status=StatusTypes.draft,
            )
            message = f"{lq.order}. {lq.text}"

        if datapoint and lq:
            valid_answer = feed.validate_answer(
                text=text, question=lq, data=datapoint, image_type=image_type
            )
            if valid_answer:
                feed.insert_answer(text=text, question=lq, data=datapoint)
                nq = feed.get_last_question(data=datapoint)
                if nq:
                    # show next question
                    message = f"{nq.order}. {nq.text}"
                    message += feed.show_options(question=nq)
                else:
                    feed.set_as_completed(data=datapoint)
                    message = "Thank you!"
            else:
                message = f"{lq.order}. {lq.text}"
                message += feed.show_options(question=lq)

        client = Client(account_sid, auth_token)
        feed.send_to_client(
            client=client,
            from_number=from_number,
            body=message,
            to_number=phone,
        )
        return Response(message)

    def instance(self, request, pk=None):
        queryset = Forms.objects.all()
        form = get_object_or_404(queryset, pk=pk)

        return self.create(request=request, form_instance=form)


class DataModelPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "current": self.page.number,
                "total": self.page.paginator.count,
                "total_page": self.page.paginator.num_pages,
                "data": data,
            }
        )


class DataViewSet(ModelViewSet):
    queryset = FormData.objects.all()
    serializer_class = ListDataSerializer
    pagination_class = DataModelPagination

    def retrieve(self, request, pk=None):
        queryset = FormData.objects.filter(status=StatusTypes.submitted)
        datapoint = get_object_or_404(queryset, pk=pk)
        serializer = DetailDataSerializer(datapoint)
        return Response(serializer.data)
