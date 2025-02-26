from rest_framework import serializers
from report.models import Report, ReportData


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'template', 'date', 'status', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']



class ReportDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportData
        fields = ['id', 'report', 'row', 'column', 'value']
        # read_only_fields = ['report', 'row', 'column']
