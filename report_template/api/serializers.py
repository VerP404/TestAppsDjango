from rest_framework import serializers
from report_template.models import (
    ReportTemplate,
    TableTemplate,
    RowGroup,
    RowTemplate,
    ColumnGroup,
    ColumnTemplate
)


class RowTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RowTemplate
        fields = ['id', 'title', 'order', 'is_active']


class ColumnTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColumnTemplate
        fields = ['id', 'title', 'order', 'is_active']


class RowGroupSerializer(serializers.ModelSerializer):
    # Рекурсивное включение подгрупп
    subgroups = serializers.SerializerMethodField()
    # Прямые строки, принадлежащие группе
    rows = RowTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = RowGroup
        fields = ['id', 'title', 'order', 'subgroups', 'rows']

    def get_subgroups(self, obj):
        groups = obj.subgroups.all()
        return RowGroupSerializer(groups, many=True).data


class ColumnGroupSerializer(serializers.ModelSerializer):
    subgroups = serializers.SerializerMethodField()
    columns = ColumnTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = ColumnGroup
        fields = ['id', 'title', 'order', 'subgroups', 'columns']

    def get_subgroups(self, obj):
        groups = obj.subgroups.all()
        return ColumnGroupSerializer(groups, many=True).data


class TableTemplateSerializer(serializers.ModelSerializer):
    rows = RowTemplateSerializer(many=True, read_only=True)
    row_groups = RowGroupSerializer(many=True, read_only=True)
    columns = ColumnTemplateSerializer(many=True, read_only=True)
    column_groups = ColumnGroupSerializer(many=True, read_only=True)

    class Meta:
        model = TableTemplate
        fields = ['id', 'title', 'description', 'is_active', 'order',
                  'rows', 'row_groups', 'columns', 'column_groups']


class ReportTemplateSerializer(serializers.ModelSerializer):
    tables = TableTemplateSerializer(many=True, read_only=True)

    class Meta:
        model = ReportTemplate
        fields = ['id', 'title', 'description', 'is_active', 'tables']
