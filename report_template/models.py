from django.db import models
from django.core.exceptions import ValidationError

# ====== Миксин для автоназначения порядка ====== #
class AutoOrderMixin(models.Model):
    """
    Абстрактный миксин для автоматического назначения порядкового номера
    при первом сохранении (когда order=0).
    """
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок"
    )

    class Meta:
        abstract = True

    def assign_order(self, filter_kwargs=None):
        """
        Если self.order == 0, ищем max(order) среди объектов,
        подходящих под filter_kwargs, и ставим order = max+1.
        """
        if self.order == 0:
            if filter_kwargs is None:
                filter_kwargs = {}
            max_val = self.__class__.objects.filter(**filter_kwargs).aggregate(models.Max('order'))['order__max']
            self.order = (max_val or 0) + 1


# ====== Основная модель отчёта ====== #
class ReportTemplate(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активность")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Шаблон отчета"
        verbose_name_plural = "Шаблоны отчетов"


# ====== Шаблон таблицы ====== #
class TableTemplate(AutoOrderMixin):
    """
    Шаблон таблицы привязан к конкретному шаблону отчёта.
    В ОДНОЙ таблице можно:
    - Создавать строки напрямую (RowTemplate, group=None)
    - Создавать группы строк (RowGroup), внутри которых тоже могут быть строки
    - Аналогично для столбцов
    """
    report = models.ForeignKey(
        ReportTemplate,
        on_delete=models.CASCADE,
        related_name="tables",
        verbose_name="Отчет"
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активность")

    def save(self, *args, **kwargs):
        # Автоназначение order (если ==0) в рамках одного отчёта
        self.assign_order(filter_kwargs={'report': self.report})
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Отчет: {self.report.title})"

    class Meta:
        ordering = ['order']
        verbose_name = "Шаблон таблицы"
        verbose_name_plural = "Шаблоны таблиц"


# ====== Группы строк ====== #
class RowGroup(AutoOrderMixin):
    table = models.ForeignKey(
        TableTemplate,
        on_delete=models.CASCADE,
        related_name="row_groups",
        verbose_name="Таблица"
    )
    parent_group = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subgroups",
        verbose_name="Родительская группа"
    )
    title = models.CharField(max_length=255, verbose_name="Название группы")

    def save(self, *args, **kwargs):
        # Если order == 0, подставляем max+1 в рамках (table, parent_group)
        self.assign_order(filter_kwargs={
            'table': self.table,
            'parent_group': self.parent_group
        })
        super().save(*args, **kwargs)

    def __str__(self):
        parent_info = f" -> {self.parent_group.title}" if self.parent_group else ""
        return f"{self.title}{parent_info} (Таблица: {self.table.title})"

    class Meta:
        ordering = ['order']
        verbose_name = "Группа строк"
        verbose_name_plural = "Группы строк"


# ====== Строки ====== #
class RowTemplate(AutoOrderMixin):
    table = models.ForeignKey(
        TableTemplate,
        on_delete=models.CASCADE,
        related_name="rows",
        verbose_name="Таблица"
    )
    group = models.ForeignKey(
        RowGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rows",
        verbose_name="Группа"
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    is_active = models.BooleanField(default=True, verbose_name="Активность")

    def save(self, *args, **kwargs):
        # Формируем фильтр для assign_order
        # Если group задана, то ищем max(order) внутри этой группы
        # Если group нет, то ищем max(order) среди строк без группы
        filter_kwargs = {'table': self.table}
        if self.group:
            filter_kwargs['group'] = self.group
        else:
            filter_kwargs['group__isnull'] = True

        self.assign_order(filter_kwargs=filter_kwargs)
        super().save(*args, **kwargs)

    def __str__(self):
        g = self.group.title if self.group else "Без группы"
        return f"{self.title} (Группа: {g})"

    class Meta:
        ordering = ['order']
        verbose_name = "Строка"
        verbose_name_plural = "Строки"


# ====== Группы столбцов ====== #
class ColumnGroup(AutoOrderMixin):
    table = models.ForeignKey(
        TableTemplate,
        on_delete=models.CASCADE,
        related_name="column_groups",
        verbose_name="Таблица"
    )
    parent_group = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subgroups",
        verbose_name="Родительская группа"
    )
    title = models.CharField(max_length=255, verbose_name="Название группы")

    def save(self, *args, **kwargs):
        self.assign_order(filter_kwargs={
            'table': self.table,
            'parent_group': self.parent_group
        })
        super().save(*args, **kwargs)

    def __str__(self):
        parent_info = f" -> {self.parent_group.title}" if self.parent_group else ""
        return f"{self.title}{parent_info} (Таблица: {self.table.title})"

    class Meta:
        ordering = ['order']
        verbose_name = "Группа столбцов"
        verbose_name_plural = "Группы столбцов"


# ====== Столбцы ====== #
class ColumnTemplate(AutoOrderMixin):
    table = models.ForeignKey(
        TableTemplate,
        on_delete=models.CASCADE,
        related_name="columns",
        verbose_name="Таблица"
    )
    group = models.ForeignKey(
        ColumnGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="columns",
        verbose_name="Группа"
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    is_active = models.BooleanField(default=True, verbose_name="Активность")

    def save(self, *args, **kwargs):
        filter_kwargs = {'table': self.table}
        if self.group:
            filter_kwargs['group'] = self.group
        else:
            filter_kwargs['group__isnull'] = True
        self.assign_order(filter_kwargs=filter_kwargs)
        super().save(*args, **kwargs)

    def __str__(self):
        g = self.group.title if self.group else "Без группы"
        return f"{self.title} (Группа: {g})"

    class Meta:
        ordering = ['order']
        verbose_name = "Столбец"
        verbose_name_plural = "Столбцы"
