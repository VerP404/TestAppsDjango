from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from report.models import Report, ReportData
from report.api.serializers import ReportSerializer, ReportDataSerializer


class ReportViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт для работы с отчетами.
    При создании нового отчета автоматически генерируются записи ReportData.
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Указываем текущего пользователя, если есть авторизация
        report = serializer.save(user=self.request.user)
        # После создания отчета генерируем данные пересечений
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
    """
    Эндпоинт для работы с ячейками отчета (ReportData) независимо.
    """
    queryset = ReportData.objects.all()
    serializer_class = ReportDataSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
