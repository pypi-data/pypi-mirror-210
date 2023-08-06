from django.urls import path, include
from rest_framework import routers
from  multistepform.api.views import FormViewSet, FormStepViewSet, FormFieldViewSet

router = routers.DefaultRouter()
router.register('forms', FormViewSet)
router.register('form-steps', FormStepViewSet)
router.register('form-fields', FormFieldViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
