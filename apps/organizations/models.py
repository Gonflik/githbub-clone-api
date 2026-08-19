from django.db import models


class Organization(models.Model):
    org_name = models.CharField(max_length=40, unique=True)
    display_name = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)

    created_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name="created_organizations")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrgMember(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        MEMBER = "MEMBER", "Member"

    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        PRIVATE = "PRIVATE", "Private"

    role = models.CharField(max_length=6, choices=Role.choices, default=Role.MEMBER)
    visibility = models.CharField(max_length=7, choices=Visibility.choices, default=Visibility.PRIVATE)

    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="org_memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'organization')



# Create your models here.
