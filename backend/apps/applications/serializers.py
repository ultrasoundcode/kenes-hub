from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Application, ApplicationHistory, ApplicationComment,
    ApplicationSource, ApplicationType, ApplicationStatus
)

User = get_user_model()


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_application_type_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)

    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'number')

    def create(self, validated_data):
        application = Application.objects.create(**validated_data)
        ApplicationHistory.objects.create(
            application=application,
            user=self.context['request'].user,
            action='Создание заявки',
            new_status=application.status
        )
        return application

    def update(self, instance, validated_data):
        old_status = instance.status
        instance = super().update(instance, validated_data)
        
        if old_status != instance.status:
            ApplicationHistory.objects.create(
                application=instance,
                user=self.context['request'].user,
                action='Изменение статуса',
                old_status=old_status,
                new_status=instance.status
            )
        return instance


class ApplicationListSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_application_type_display', read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'number', 'subject', 'applicant_name',
            'application_type', 'type_display', 'status', 'status_display',
            'priority', 'created_at', 'deadline', 'assigned_to'
        )


class ApplicationHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = ApplicationHistory
        fields = '__all__'
        read_only_fields = ('created_at',)


class ApplicationCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = ApplicationComment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Application
        fields = ('status', 'comment', 'assigned_to')

    def update(self, instance, validated_data):
        comment = validated_data.pop('comment', '')
        old_status = instance.status
        instance = super().update(instance, validated_data)
        
        ApplicationHistory.objects.create(
            application=instance,
            user=self.context['request'].user,
            action='Изменение статуса',
            old_status=old_status,
            new_status=instance.status,
            comment=comment
        )
        return instance


class ApplicationStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_status = serializers.DictField(child=serializers.IntegerField())
    by_type = serializers.DictField(child=serializers.IntegerField())
    by_source = serializers.DictField(child=serializers.IntegerField())
    this_month = serializers.IntegerField()
    completed_this_month = serializers.IntegerField()