from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportTemplateViewSet

router = DefaultRouter()
router.register(r'report_templates', ReportTemplateViewSet, basename='reporttemplate')

urlpatterns = [
    path('', include(router.urls)),
]
