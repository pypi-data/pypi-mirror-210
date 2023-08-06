from rest_framework import serializers
from .models import (
    AkvoGatewayForm,
    AkvoGatewayQuestion,
    AkvoGatewayQuestionOption,
    AkvoGatewayData,
    AkvoGatewayAnswer,
)
from .constants import QuestionTypes
from .utils.functions import get_answer_value


class CheckSerializer(serializers.Serializer):
    id = serializers.IntegerField(default=1)
    check = serializers.CharField(default="OK")


class ListFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvoGatewayForm
        fields = ["id", "name", "description", "version"]


class ListOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvoGatewayQuestionOption
        fields = ["id", "name", "order"]


class ListQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AkvoGatewayQuestion
        fields = ["id", "form", "order", "text"]


class ListDataSerializer(serializers.ModelSerializer):
    form_name = serializers.SerializerMethodField()

    class Meta:
        model = AkvoGatewayData
        fields = [
            "id",
            "status",
            "form_name",
            "name",
            "phone",
            "geo",
            "created",
            "updated",
        ]

    def get_form_name(self, obj):
        return obj.form.name


class ListDataAnswerSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    question_type = serializers.SerializerMethodField()

    class Meta:
        model = AkvoGatewayAnswer
        fields = ["question", "question_type", "value"]

    def get_question_type(self, obj):
        return QuestionTypes.FieldStr.get(obj.question.type)

    def get_value(self, instance: AkvoGatewayAnswer):
        return get_answer_value(instance)


class QuestionDefinitionSerializer(serializers.ModelSerializer):
    question_type = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    class Meta:
        model = AkvoGatewayQuestion
        fields = ["id", "text", "required", "question_type", "options"]

    def get_question_type(self, obj):
        return QuestionTypes.FieldStr.get(obj.type)

    def get_options(self, instance):
        options = (
            [
                options.name
                for options in instance.ag_question_question_options.all()
            ]
            if instance.ag_question_question_options.count()
            else None
        )
        return options


class TwilioSerializer(serializers.Serializer):
    Latitude = serializers.CharField(required=False)
    Longitude = serializers.CharField(required=False)
    MediaContentType0 = serializers.CharField(required=False)
    MediaUrl0 = serializers.URLField(required=False)
    SmsMessageSid = serializers.CharField(required=False)
    NumMedia = serializers.IntegerField(required=False)
    ProfileName = serializers.CharField(required=False)
    SmsSid = serializers.CharField(required=False)
    WaId = serializers.CharField(required=False)
    SmsStatus = serializers.CharField(required=False)
    Body = serializers.CharField(required=False)
    To = serializers.CharField(required=False)
    From = serializers.CharField(required=False)
    NumSegments = serializers.IntegerField(required=False)
    ReferralNumMedia = serializers.IntegerField(required=False)
    MessageSid = serializers.CharField(required=False)
    AccountSid = serializers.CharField(required=False)
    ApiVersion = serializers.CharField(required=False)
    phone = serializers.SerializerMethodField()

    def get_phone(self, obj):
        from_field = obj.get("From", "")
        if from_field.startswith("whatsapp:"):
            return from_field[10:]
        return from_field

    def validate(self, data):
        if data.get("MediaContentType0") and not data.get("MediaUrl0"):
            raise serializers.ValidationError(
                "MediaUrl0 is required when MediaContentType0 is present."
            )
        if data.get("MediaUrl0") and not data.get("MediaContentType0"):
            raise serializers.ValidationError(
                "MediaContentType0 is required when MediaUrl0 is present."
            )
        if not data.get("Latitude") and data.get("Longitude"):
            raise serializers.ValidationError(
                "Latitude is required when Longitude is present."
            )
        if data.get("Latitude") and not data.get("Longitude"):
            raise serializers.ValidationError(
                "Longitude is required when Latitude is present."
            )
        return data


class DetailAnswerSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    question_text = serializers.SerializerMethodField()

    class Meta:
        model = AkvoGatewayAnswer
        fields = ["id", "question_text", "value"]

    def get_value(self, instance: AkvoGatewayAnswer):
        return get_answer_value(instance)

    def get_question_text(self, obj):
        return obj.question.text


class DetailDataSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = AkvoGatewayData
        fields = [
            "id",
            "status",
            "form",
            "name",
            "phone",
            "geo",
            "created",
            "updated",
            "answers",
        ]

    def get_answers(self, obj):
        queryset = obj.ag_data_answer.all()
        serializer = DetailAnswerSerializer(queryset, many=True)
        return serializer.data
