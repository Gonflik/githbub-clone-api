from django.shortcuts import render
from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError 

from .models import Invitation
from apps.repositories.models import Collaborator
from apps.organizations.models import OrgMember
from .serializers import InvitationSerializer
from apps.repositories.serializers import CollaboratorSerializer
from apps.organizations.serializers import OrgMemberSerializer


class IsInvitee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user != obj.invitee:
            return False
        return True
        
class InvitationViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
    ):
    permission_classes = [IsInvitee]
    serializer_class = InvitationSerializer

    def get_queryset(self):
        return Invitation.objects.filter(invitee=self.request.user)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        inv = self.get_object()
        user = request.user

        if inv.status != "PENDING":
            raise ValidationError("Invitation is no longer pending!")

        inv.status = "ACCEPTED"
        inv.save()

        if inv.repository is not None:
            collaborator = Collaborator.objects.create(user=user, repository=inv.repository)
            serializer = CollaboratorSerializer(collaborator)
        else:
            orgmember = OrgMember.objects.create(user=user, organization=inv.organization)
            serializer = OrgMemberSerializer(orgmember)


        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        inv = self.get_object()

        if inv.status != "PENDING":
            raise ValidationError("Invitation is no longer pending!")

        inv.status = "DECLINED"
        inv.save()

        return Response({"detail": "Invitation declined."}, status=status.HTTP_200_OK)

# Create your views here.
