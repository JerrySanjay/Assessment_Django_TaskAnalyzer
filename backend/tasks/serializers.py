from rest_framework import serializers

class TaskInputSerializer(serializers.Serializer):
    title = serializers.CharField()
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.IntegerField(required=False, default=1, min_value=0)
    importance = serializers.IntegerField(required=False, default=5, min_value=1, max_value=10)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False, default=list)
