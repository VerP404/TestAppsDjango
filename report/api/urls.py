from django.urls import path, include
from rest_framework.routers import DefaultRouter
from report.api.views import ReportViewSet, ReportDataViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'reportdata', ReportDataViewSet, basename='reportdata')

urlpatterns = [
    path('', include(router.urls)),
]
