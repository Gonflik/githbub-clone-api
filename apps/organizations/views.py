from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError 
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .serializers import OrganizationSerializer, OrgMemberSerializer
from apps.invitations.serializers import InvitationSerializer
from apps.invitations.models import Invitation
from .models import Organization, OrgMember
from rest_framework.decorators import action
from rest_framework.response import Response

class IsOwnerMember(permissions.BasePermission):
    def has_permission(self, request, view):
        org_name = view.kwargs.get("org_name", view.kwargs.get("org_org_name"))
        if not org_name:
            return True

        org = get_object_or_404(Organization, org_name=org_name)
        try:
            user = OrgMember.objects.get(user=request.user, organization=org)
        except OrgMember.DoesNotExist:
            raise PermissionDenied

        return user.role == "OWNER"

class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        org_name = view.kwargs.get("org_name", view.kwargs.get("org_org_name"))
        if not org_name:
            return True

        org = get_object_or_404(Organization, org_name=org_name)
        return OrgMember.objects.filter(organization=org, user=request.user).exists()

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [permissions.IsAuthenticated, IsOwnerMember]

    lookup_field = "org_name"

    queryset = Organization.objects.all()

    def get_permissions(self):
        if self.action == "retrieve":
            return [AllowAny()]
        if self.action == "leave":
            return [permissions.IsAuthenticated(), IsMember()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        org = serializer.save(created_by=user)

        OrgMember.objects.create(user=user, organization=org, role="OWNER")

    @action(detail=True, methods=['post'])
    def leave(self, request, org_name=None):
        org = self.get_object()
        member = get_object_or_404(OrgMember, user=request.user, organization=org)
        if OrgMember.objects.filter(role="OWNER").count() == 1 and member.role == "OWNER":
            return Response({"detail": "Can't leave. Atleast 1 owner needs to exist in an organization!"}, status=status.HTTP_403_FORBIDDEN)
        
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrgMemberViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated(), IsMember()]
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), IsOwnerMember()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return InvitationSerializer
        return OrgMemberSerializer

    def get_queryset(self):
        return OrgMember.objects.filter(organization__org_name=self.kwargs["org_org_name"])

    def perform_create(self, serializer):
        org = get_object_or_404(Organization, org_name=self.kwargs["org_org_name"])
        try:
            member = OrgMember.objects.get(user=self.request.user, organization=org)
        except OrgMember.DoesNotExist:
            raise PermissionDenied
        

        if member.role != "OWNER":
            raise PermissionDenied

        invitee = serializer.validated_data["invitee"]

        if self.request.user == invitee:
            raise ValidationError("Cant invite self!")
        
        if OrgMember.objects.filter(user=invitee, organization=org).exists():
            raise ValidationError("Invitee is already a member!")

        if Invitation.objects.filter(organization=org, invitee=invitee, status="PENDING").exists():
            raise ValidationError("Invitee already has a pending invitation!")

        declined_invite = Invitation.objects.filter(organization=org, invitee=invitee, status="DECLINED")
        if declined_invite.exists():
            declined_invite.update(status="PENDING")
            serializer.instance = declined_invite.first()
            return 
            

        serializer.save(invitee=invitee, organization=org, invited_by=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        org = get_object_or_404(Organization, org_name=self.kwargs["org_org_name"])
        try:
            user = OrgMember.objects.get(user=request.user, organization=org)
        except OrgMember.DoesNotExist:
            raise PermissionDenied

        if user.role == "OWNER":
            pass
        elif user.role == "MEMBER" and set(request.data.keys()) == {"visibility"}:
            pass
        else:
            raise PermissionDenied
        
        return super().partial_update(request, *args, **kwargs)
    

# Create your views here.
