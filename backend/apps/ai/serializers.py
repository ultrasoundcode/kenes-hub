from rest_framework import serializers
from .models import AIConversation, AIMessage, AIKnowledgeBase, AIUsageStats, AIIntent


class AIMessageSerializer(serializers.ModelSerializer):
    intent_name = serializers.CharField(source='intent.name', read_only=True)

    class Meta:
        model = AIMessage
        fields = '__all__'
        read_only_fields = ('created_at',)


class AIConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = AIConversation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content,
                'created_at': last_msg.created_at
            }
        return None

    def get_message_count(self, obj):
        return obj.messages.count()


class AIKnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIKnowledgeBase
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class AIUsageStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIUsageStats
        fields = '__all__'


class AIIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIIntent
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')