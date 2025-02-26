from rest_framework import viewsets
from report_template.models import ReportTemplate
from .serializers import ReportTemplateSerializer


class ReportTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Эндпоинт для получения списка шаблонов отчётов с полной структурой таблиц.
    Можно фильтровать по активности, используя query параметр ?active=true (или false).
    """
    serializer_class = ReportTemplateSerializer
    queryset = ReportTemplate.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        active = self.request.query_params.get('active')
        if active is not None:
            if active.lower() in ['true', '1']:
                qs = qs.filter(is_active=True)
            elif active.lower() in ['false', '0']:
                qs = qs.filter(is_active=False)
        return qs
