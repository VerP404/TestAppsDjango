from django.db import models
from django.conf import settings
from report_template.models import (
    ReportTemplate,
    RowTemplate,
    ColumnTemplate
)


class Report(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('for_approval', 'Для утверждения'),
        ('approved', 'Утвержден'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь"
    )
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        verbose_name="Шаблон отчёта"
    )
    date = models.DateField(verbose_name="Дата отчёта")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.template.title} от {self.date} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Отчёт"
        verbose_name_plural = "Отчёты"

    def create_or_update_data(self):
        """
        Создаёт (или дополняет) ReportData для всех строк/столбцов в выбранном шаблоне.
        """
        for table_tpl in self.template.tables.all():
            row_qs = table_tpl.rows.all()
            col_qs = table_tpl.columns.all()
            for row_tpl in row_qs:
                for col_tpl in col_qs:
                    ReportData.objects.get_or_create(
                        report=self,
                        row=row_tpl,
                        column=col_tpl,
                        defaults={'value': 0}
                    )



class ReportData(models.Model):
    """
    Хранит значение, введённое пользователем (или системой) для пересечения
    RowTemplate и ColumnTemplate в рамках конкретного Report.
    """
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name="data",
        verbose_name="Отчёт"
    )
    row = models.ForeignKey(
        RowTemplate,
        on_delete=models.CASCADE,
        verbose_name="Строка (шаблон)"
    )
    column = models.ForeignKey(
        ColumnTemplate,
        on_delete=models.CASCADE,
        verbose_name="Столбец (шаблон)"
    )
    # Храним число, по умолчанию 0 (или null, если хотите)
    value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=0,
        verbose_name="Значение"
    )

    def __str__(self):
        return f"{self.report} / R:{self.row} / C:{self.column} => {self.value}"

    class Meta:
        verbose_name = "Данные отчёта"
        verbose_name_plural = "Данные отчёта"
        unique_together = (("report", "row", "column"),)
