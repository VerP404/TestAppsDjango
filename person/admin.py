from django.contrib import admin
from .models import Insurance, InsurancePolicy, PhysicalPerson
from .forms import InsurancePolicyInlineFormSet


# Inline для полисов физического лица
class InsurancePolicyInline(admin.TabularInline):
    model = InsurancePolicy
    formset = InsurancePolicyInlineFormSet
    extra = 1
    fields = ('enp', 'start_date', 'end_date', 'insurance')
    verbose_name = "Полис"
    verbose_name_plural = "Полисы"


@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    # Полисы редактируются через inline, поэтому отдельную админку для InsurancePolicy регистрировать не будем.


@admin.register(PhysicalPerson)
class PhysicalPersonAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date', 'snils')
    search_fields = ('last_name', 'first_name', 'snils', 'phone')
    inlines = [InsurancePolicyInline]
