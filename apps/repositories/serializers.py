from rest_framework import serializers
from .models import Repository, Star


class RepositorySerializer(serializers.ModelSerializer):
    created_at = serializers.ReadOnlyField
    updated_at = serializers.ReadOnlyField

    class Meta:
        model = Repository
        fields = ["id" ,"name", "description", "visibility" ,"created_at", "updated_at"]


class StarSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    created_at = serializers.ReadOnlyField()

    class Meta:
        model = Star
        fields = ['id', 'user', 'repository', 'created_at']



