from django.db import models
from django.conf import settings
from report_template.models import (
    ReportTemplate,
    RowTemplate,
    ColumnTemplate
)


class Report(models.Model):
    """
    Конкретный отчёт, созданный пользователем (или системой) на основе шаблона.
    Например, пользователь выбирает "Шаблон отчёта" и указывает дату.
    """
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.template.title} от {self.date}"

    class Meta:
        verbose_name = "Отчёт"
        verbose_name_plural = "Отчёты"

    def create_or_update_data(self):
        """
        Метод, который создаёт (или дополняет) ReportData
        для всех строк/столбцов в выбранном шаблоне.
        """
        # Идём по всем таблицам в шаблоне, затем по строкам и столбцам.
        # Для простоты в этом примере не создаём отдельную модель "ReportTable",
        # а просто создаём данные на пересечении RowTemplate и ColumnTemplate.
        for table_tpl in self.template.tables.all():
            row_qs = table_tpl.rows.all()
            col_qs = table_tpl.columns.all()
            for row_tpl in row_qs:
                for col_tpl in col_qs:
                    # Создаём запись, если её ещё нет
                    # По умолчанию value = 0, если вы хотите хранить числа
                    # Или value=None, если хотите хранить null
                    ReportData.objects.get_or_create(
                        report=self,
                        row=row_tpl,
                        column=col_tpl,
                        defaults={'value': 0}  # или defaults={'value': None}
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
