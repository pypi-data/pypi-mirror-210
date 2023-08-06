# -*- coding: utf-8 -*-

from django.db import models

from model_utils.models import TimeStampedModel
from tinymce.models import HTMLField 

class Form(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class FormStep(TimeStampedModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"Step {self.step_number} of {self.form.name}"
    

class FormField(TimeStampedModel):
    FIELD_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('url', 'URL'),
        ('password', 'Password'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('select', 'Select'),
        ('file', 'File Upload'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime', 'Date-Time'),
        ('color', 'Color Picker'),
        ('range', 'Range Slider'),
        ('hidden', 'Hidden'),
        ('custom', 'Custom'),
    ]
    step = models.ForeignKey(FormStep, on_delete=models.CASCADE, related_name='fields')
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    placeholder = models.CharField(max_length=255)
    help_text = models.TextField(blank=True, null=True)
    meta_data = HTMLField(blank=True, null=True)
    validation_regex = models.CharField(max_length=255, blank=True)
    validation_error_message = models.CharField(max_length=255, blank=True)
    is_required = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    is_readonly = models.BooleanField(default=False)
    options = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class FormResponse(TimeStampedModel):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='responses')
    submitted_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    


