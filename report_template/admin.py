from django.contrib import admin
from .models import (
    ReportTemplate,
    TableTemplate,
    RowGroup,
    RowTemplate,
    ColumnGroup,
    ColumnTemplate
)

# =========== Inlines для строк =========== #
class RowGroupInline(admin.TabularInline):
    model = RowGroup
    extra = 0
    fields = ("title", "order", "parent_group")

class RowTemplateInline(admin.TabularInline):
    model = RowTemplate
    extra = 0
    fields = ("title", "is_active", "order", "group")


# =========== Inlines для столбцов =========== #
class ColumnGroupInline(admin.TabularInline):
    model = ColumnGroup
    extra = 0
    fields = ("title", "order", "parent_group")

class ColumnTemplateInline(admin.TabularInline):
    model = ColumnTemplate
    extra = 0
    fields = ("title", "is_active", "order", "group")


@admin.register(TableTemplate)
class TableTemplateAdmin(admin.ModelAdmin):
    """
    Админка для таблицы. Показываем все inlines сразу:
    - Группы строк
    - Прямые строки
    - Группы столбцов
    - Прямые столбцы

    Так вы сможете «смешивать» группированные и негруппированные элементы
    в одной таблице, если это требуется.
    """
    list_display = ("title", "report", "is_active", "order")
    list_filter = ("report", "is_active")
    search_fields = ("title",)

    inlines = [
        RowGroupInline,
        RowTemplateInline,
        ColumnGroupInline,
        ColumnTemplateInline
    ]

    # Если хотите, чтобы инлайны показывались только после сохранения таблицы:
    # переопределите get_inline_instances
    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return []
    #     return super().get_inline_instances(request, obj)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")
    search_fields = ("title",)


@admin.register(RowGroup)
class RowGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "table", "parent_group", "order")
    list_filter = ("table", "parent_group")
    search_fields = ("title",)


@admin.register(RowTemplate)
class RowTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "table", "group", "is_active", "order")
    list_filter = ("table", "is_active", "group")
    search_fields = ("title",)


@admin.register(ColumnGroup)
class ColumnGroupAdmin(admin.ModelAdmin):
    list_display = ("title", "table", "parent_group", "order")
    list_filter = ("table", "parent_group")
    search_fields = ("title",)


@admin.register(ColumnTemplate)
class ColumnTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "table", "group", "is_active", "order")
    list_filter = ("table", "is_active", "group")
    search_fields = ("title",)
