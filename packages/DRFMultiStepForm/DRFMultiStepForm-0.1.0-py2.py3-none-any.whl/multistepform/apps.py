# -*- coding: utf-8
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

class multistepform(AppConfig):
    name = 'multistepform'
    
    def ready(self):
        from django.conf import settings
        if 'tinymce' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured('tinymce must be in installed apps.')