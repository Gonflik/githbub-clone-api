from rest_framework import serializers
from .models import Organization, OrgMember

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "org_name", "display_name", "description", "created_by", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class OrgMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgMember
        fields = ["id", "role", "user", "organization", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "organization", "created_at", "updated_at"]
        