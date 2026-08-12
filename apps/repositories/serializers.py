from rest_framework import serializers
from .models import Repository, Star, Invitation, Collaborator


class RepositorySerializer(serializers.ModelSerializer):

    stars_count = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = ["id" ,"name", "description", "visibility" ,"stars_count","created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Repository.objects.create(user=user, **validated_data)

    def validate_name(self, value):
        user = self.context["request"].user
        if Repository.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("You already have a repository with this name.")
        return value

    def get_stars_count(self, obj):
        return Star.objects.filter(repository=obj).count()



class StarSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Star
        fields = ['id', 'user', 'repository', 'created_at']
        read_only_fields = ["id", "created_at"]


class InvitationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invitation
        fields = ['id', 'invitee', 'repository', 'invited_by', 'status', 'created_at', 'updated_at']
        read_only_fields = ["id", "created_at", "updated_at"]

class CollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborator
        fields = []