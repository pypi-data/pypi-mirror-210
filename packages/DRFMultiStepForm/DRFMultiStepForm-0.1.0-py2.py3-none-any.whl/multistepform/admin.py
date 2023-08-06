# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import (
   Form,
   FormStep,
   FormField,
   FormResponse,
)


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('name','description')


@admin.register(FormStep)
class FormStepAdmin(admin.ModelAdmin):
    list_display = ('form', 'step_number', 'name', 'description')


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    pass


@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    pass



