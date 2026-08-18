from django.db import models

class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"

    repository = models.ForeignKey("repositories.Repository", on_delete=models.CASCADE, related_name="invitations", null=True)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="invitations", null=True)

    invitee = models.ForeignKey("accounts.CustomUser", on_delete=models.CASCADE, related_name="invitations")

    invited_by = models.ForeignKey("accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name="sent_invitations")
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('repository', 'invitee')
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(repository__isnull=False, organization__isnull=True) |
                    models.Q(repository__isnull=True, organization__isnull=False)
                ),
                name="ck_invitation_onto_one_shit"
            )
        ]
# Create your models here.
