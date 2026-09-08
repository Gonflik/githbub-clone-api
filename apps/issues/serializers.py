from rest_framework import serializers
from .models import Issue, Comment, Label


class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = ["id", "contents", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "name", "color", "repository", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "repository"]
        

class IssueSerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    comments = CommentSerializer(many=True ,read_only=True)

    labels = LabelSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = ["id" ,"title", "description", "status", "created_at", "updated_at", "labels", "comments"]
        read_only_fields = ["id", "created_at", "updated_at"]

    

