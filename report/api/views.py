from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from report.models import Report, ReportData
from report.api.serializers import ReportSerializer, ReportDataSerializer


class ReportViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт для работы с отчетами.
    При создании нового отчета автоматически генерируются записи ReportData.
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [AllowAny]  # Разрешаем доступ всем

    def perform_create(self, serializer):
        """
        Переопределяем метод perform_create, чтобы вызвать create_or_update_data.
        """
        report = serializer.save()
        report.create_or_update_data()

    @action(detail=True, methods=['get'], url_path='data')
    def data(self, request, pk=None):
        """
        Дополнительный эндпоинт для получения всех ячеек (ReportData)
        для конкретного отчета. URL: /api/reports/{id}/data/
        """
        report = self.get_object()
        serializer = ReportDataSerializer(report.data.all(), many=True)
        return Response(serializer.data)


class ReportDataViewSet(viewsets.ModelViewSet):
    queryset = ReportData.objects.all()
    serializer_class = ReportDataSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        report_id = self.kwargs.get('report_id')
        row_id = self.kwargs.get('row_id')
        col_id = self.kwargs.get('col_id')
        return self.queryset.get(report=report_id, row=row_id, column=col_id)

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # Если статус отчёта не "черновик", редактирование запрещено
            if instance.report.status != 'draft':
                return Response(
                    {"error": "Редактирование запрещено – отчёт уже отправлен на утверждение или утвержден."},
                    status=403
                )
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


