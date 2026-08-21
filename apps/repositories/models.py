from django.db import models
from django.conf import settings

class Repository(models.Model):
    class Status(models.TextChoices):
        PRIVATE = "PRIVATE", "Private"
        PUBLIC = "PUBLIC", "Public"

    name = models.CharField(max_length=100)
    description = models.TextField()
    visibility = models.CharField(max_length=7, choices=Status.choices, default=Status.PUBLIC)
    
    open_issues_count = None

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="repositories", null=True)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="repositories", null=True)

    starred_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Star",
        related_name="starred_repositories"
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_user_reponame"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, organization__isnull=True) |
                    models.Q(user__isnull=True, organization__isnull=False)
                ),
                name="ck_repo_has_one_owner"
            )
        ]

    def __str__(self):
        return f"{self.id}: {self.name}"
    
class Star(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "repository"],
                name="unique_repository_star"
            )
        ]


class Collaborator(models.Model):
    #add class permission_level(read, write, admin)
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="collaborations")
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name="collaborators")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('repository', 'user')



