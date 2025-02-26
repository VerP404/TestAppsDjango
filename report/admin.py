from django.contrib import admin
from .models import Report, ReportData


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Админка для отчётов.
    Без inlines — просто отдельный список,
    где можно увидеть, какой шаблон, пользователь, дата и т.д.
    """
    list_display = ("template", "user", "date", "created_at", "updated_at")
    search_fields = ("template__title", "user__username")
    date_hierarchy = "date"

    # Если хотите, чтобы при сохранении автоматически создавались данные:
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # После сохранения (при первом создании) вызываем метод для инициализации ячеек
        if not change:  # означает, что это новое создание
            obj.create_or_update_data()


@admin.register(ReportData)
class ReportDataAdmin(admin.ModelAdmin):
    """
    Отдельная админка для данных отчёта.
    """
    list_display = ("report", "row", "column", "value")
    list_filter = ("report", "row__table", "column__table")
    search_fields = ("report__template__title", "row__title", "column__title")
