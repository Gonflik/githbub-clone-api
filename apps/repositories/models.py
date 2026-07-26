from django.db import models
from django.conf import settings

class Repository(models.Model):
    class Status(models.TextChoices):
        PRIVATE = "PRIV", "Private"
        PUBLIC = "PUBL", "Public"
    name = models.CharField(max_length=100)
    description = models.TextField()
    visibility = models.CharField(max_length=4, choices=Status.choices, default=Status.PUBLIC)
    
    stars_count = None
    open_issues_count = None

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="repositories")
    starred_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Star",
        related_name="starred_repositories"
    )

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


