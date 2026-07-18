from django.db import models


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

    user = None

    def __str__(self):
        return f"{self.id}: {self.name}"
    
class Star(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




