from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError 
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from .serializers import OrganizationSerializer, OrgMemberSerializer
from apps.invitations.serializers import InvitationSerializer
from apps.invitations.models import Invitation
from .models import Organization, OrgMember

class IsOwnerOrReadOnly(permissions.BasePermission):
      def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
             return True
        
        user = OrgMember.objects.get(user=request.user)

        return user.role == "OWNER"

class IsMemberOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        org = get_object_or_404(Organization, org_name=view.kwargs["org_name"])
        member = OrgMember.objects.get(user=request.user)
    
        return member is not None

class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsOwnerOrReadOnly]

    lookup_field = "org_name"

    queryset = Organization.objects.all()

    def get_permissions(self):
        if self.action == "retrieve":
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        user = self.request.user
        org = serializer.save(created_by=user)

        OrgMember.objects.create(user=user, organization=org, role="OWNER")


class OrgMemberViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ["list", "retrieve"]: #this kinda sucks
            return [IsMemberOrOwner]
        return super().get_permissions()

    def get_serializer_class(self):
            if self.action == 'create':
                return InvitationSerializer
            return OrgMemberSerializer

    def get_queryset(self):
        if self.request.user.has_perm('IsMemberOrOwner'):
            return OrgMember.objects.filter(organization__org_name=self.kwargs["org_name"])
        return OrgMember.objects.filter(Q(organization__org_name=self.kwargs["org_name"]) & Q(visibility="PUBLIC"))

    def perform_create(self, serializer):
        org = get_object_or_404(Organization, org_name=self.kwargs["org_name"])
        member = get_object_or_404(OrgMember, user=self.request.user)

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

    def destroy(self, request, *args, **kwargs):
        org = get_object_or_404(Organization, org_name=self.kwargs["org_name"])
        member = get_object_or_404(OrgMember, user=self.request.user)

        if member.role != "OWNER":
            raise PermissionDenied
        return super().destroy(request, *args, **kwargs)

    

# Create your views here.
