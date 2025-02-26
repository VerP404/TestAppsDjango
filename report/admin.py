from django.contrib import admin
from .models import Report, ReportData


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("template", "user", "date", "status", "created_at", "updated_at")
    search_fields = ("template__title", "user__username")
    date_hierarchy = "date"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            obj.create_or_update_data()

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status in ['for_approval', 'approved']:
            # Если отчёт уже для утверждения или утвержден – делаем все поля недоступными для редактирования
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)



@admin.register(ReportData)
class ReportDataAdmin(admin.ModelAdmin):
    """
    Отдельная админка для данных отчёта.
    """
    list_display = ("report", "row", "column", "value")
    list_filter = ("report", "row__table", "column__table")
    search_fields = ("report__template__title", "row__title", "column__title")
