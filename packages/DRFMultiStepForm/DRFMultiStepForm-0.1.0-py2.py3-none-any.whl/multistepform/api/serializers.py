from rest_framework import serializers
from multistepform.models import Form, FormStep, FormField, FormResponse


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ('id', 'step', 'field_type', 'name', 'label', 'placeholder', 'help_text', 'validation_regex',
                  'validation_error_message', 'is_required', 'is_hidden', 'is_readonly', 'options')


class FormStepSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    class Meta:
        model = FormStep
        fields = ('id', 'form', 'step_number', 'name', 'description', 'fields')



class FormSerializer(serializers.ModelSerializer):
    steps = FormStepSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = ('id', 'name', 'description', 'steps')
