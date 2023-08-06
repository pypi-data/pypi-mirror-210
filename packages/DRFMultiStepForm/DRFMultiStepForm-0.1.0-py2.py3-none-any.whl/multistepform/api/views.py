from rest_framework import viewsets
from multistepform.models import Form, FormStep, FormField, FormResponse
from multistepform.api.serializers import FormSerializer, FormStepSerializer, FormFieldSerializer


class FormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer


class FormStepViewSet(viewsets.ModelViewSet):
    queryset = FormStep.objects.all()
    serializer_class = FormStepSerializer


class FormFieldViewSet(viewsets.ModelViewSet):
    queryset = FormField.objects.all()
    serializer_class = FormFieldSerializer
