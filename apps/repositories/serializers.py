from rest_framework import serializers
from .models import Repository, Star, Collaborator


class RepositorySerializer(serializers.ModelSerializer):
    stars_count = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Repository
        fields = ["id" ,"name", "description", "owner", "visibility" ,"stars_count", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "owner", "stars_count"]

    def validate_name(self, value):
        user = self.context["request"].user
        if Repository.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("You already have a repository with this name.")
        return value

    def get_owner(self, obj):
        if obj.user:
            return {"type": "user", "name": obj.user.username}
        return {"type": "organization", "name": obj.organization.org_name}

    def get_stars_count(self, obj):
        return Star.objects.filter(repository=obj).count()



class StarSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Star
        fields = ['id', 'user', 'repository', 'created_at']
        read_only_fields = ["id", "created_at"]


class CollaboratorSerializer(serializers.ModelSerializer):
    PERSONAL_ALLOWED = {"WRITE"}
    ORG_ALLOWED = {"READ", "WRITE", "ADMIN"}

    class Meta:
        model = Collaborator
        fields = ["id", "role", "user", "repository", "created_at"]
        read_only_fields = ["id", "user", "repository", "created_at"]

    def validate_role(self, value):
        repo = self.context["repository"]
        
        if repo.organization is None:
            if value not in self.PERSONAL_ALLOWED:
                raise serializers.ValidationError(
                    "Personal repository collaborators can only have 'write' role."
                )
        else:
            if value not in self.ORG_ALLOWED:
                raise serializers.ValidationError(
                    f"Organization repository collaborators can only have: {self.ORG_ALLOWED}"
                )
        return value
