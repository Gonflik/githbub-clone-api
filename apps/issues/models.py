from django.db import models

# Create your models here.

class Label(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#FFFFFF")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    repository = models.ForeignKey("repositories.Repository", on_delete=models.CASCADE, related_name="labels")

    class Meta:
        unique_together = ("repository", "name")

class Issue(models.Model):
    class IssueStatus(models.TextChoices): 
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"

    title = models.CharField(max_length=72)
    description = models.TextField()
    status = models.CharField(max_length=6, choices=IssueStatus.choices, default=IssueStatus.OPEN)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="issues")
    repository = models.ForeignKey("repositories.Repository", on_delete=models.CASCADE, related_name="issues")

    labels = models.ManyToManyField(Label, related_name="issues", blank=True)


class Comment(models.Model):
    contents = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="comments")



