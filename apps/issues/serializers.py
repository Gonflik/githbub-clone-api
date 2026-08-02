from rest_framework import serializers
from models import Issue, Comment


class IssueSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField
    updated_at = serializers.ReadOnlyField

    class Meta:
        model = Issue
        fields = ["id" ,"title", "description", "status", "created_at", "updated_at"]


class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField
    updated_at = serializers.ReadOnlyField

    class Meta:
        model = Comment
        fields = ["id", "contents", "created_at", "updated_at"]



