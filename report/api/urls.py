from django.urls import path, include
from rest_framework.routers import DefaultRouter
from report.api.views import ReportViewSet, ReportDataViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'reportdata', ReportDataViewSet, basename='reportdata')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/<int:report_id>/data/<int:row_id>/<int:col_id>/',
         ReportDataViewSet.as_view({'patch': 'partial_update'})),
]
