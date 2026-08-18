from django.db import models


class Organization(models.Model):
    org_name = models.CharField(max_length=40, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(null=True)

    created_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name="created_organizations")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrgMember(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"
        GUEST = "GUEST", "Guest"

    role = models.CharField(max_length=6, choices=Role.choices, default=Role.MEMBER)

    user = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="org_memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'organization')



# Create your models here.
