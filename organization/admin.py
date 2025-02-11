from django.contrib import admin
from .models import Organization, MOConfiguration, Building, Department, RelatedDepartment, Station

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_mo', 'oid_mo')


@admin.register(MOConfiguration)
class MOConfigurationAdmin(admin.ModelAdmin):
    list_display = ('organization', 'configuration')
    # Можно добавить фильтры или поиск по организации


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'building', 'external_id')


@admin.register(RelatedDepartment)
class RelatedDepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'source', 'configuration')


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department')
