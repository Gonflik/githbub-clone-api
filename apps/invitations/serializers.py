from rest_framework import serializers
from .models import Invitation
from apps.accounts.models import CustomUser


class InvitationSerializer(serializers.ModelSerializer):
    invitee = serializers.SlugRelatedField(slug_field="username", queryset=CustomUser.objects.all())
    invited_by = serializers.SlugRelatedField(slug_field="username", read_only=True)


    def create(self, validated_data):
        return Invitation.objects.create(**validated_data)

    class Meta:
        model = Invitation
        fields = ['id', 'invitee', 'invited_by', 'status', 'created_at', 'updated_at']
        read_only_fields = ["id", "status", "invited_by", "created_at", "updated_at"]