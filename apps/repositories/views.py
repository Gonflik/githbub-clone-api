from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import RepositorySerializer, StarSerializer, CollaboratorSerializer
from apps.invitations.serializers import InvitationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError, NotAuthenticated 
from .models import Repository, Star, Collaborator
from apps.invitations.models import Invitation
from apps.accounts.models import CustomUser
from apps.organizations.models import OrgMember
# Create your views here.




class IsOwnerOrOrgStuff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            if obj.visibility == "PUBLIC" and view.action == "retrieve":
                return True
            raise NotAuthenticated

        if obj.organization is not None:
            try:
                member = OrgMember.objects.get(user=request.user, organization=obj.organization)
            except OrgMember.DoesNotExist:
                try:
                    collab_guy = Collaborator.objects.get(user=request.user, repository=obj)
                except Collaborator.DoesNotExist:
                    if obj.visibility == "PUBLIC" and view.action in ["retrieve", "stars", "remove_star"]:
                        return True
                    raise PermissionDenied
                else:
                    if collab_guy.role == "ADMIN":
                        if view.action in ["retrieve", "partial_update", "stars", "remove_star"]:
                            return True
                        return False
                    if collab_guy.role == "WRITE":
                        if view.action in ["retrieve", "partial_update", "stars", "remove_star"]:
                            return True
                        return False
                    if collab_guy.role == "READ":
                        if view.action in ["retrieve", "stars", "remove_star"]:
                            return True
                        return False 
            else:
                return member.role == "OWNER"
        else:
            if obj.user == request.user:
                return True
            try:
                collab_guy = Collaborator.objects.get(user=request.user, repository=obj)
            except Collaborator.DoesNotExist:
                if obj.visibility == "PUBLIC" and view.action in ["retrieve", "stars", "remove_star"]:
                    return True
                raise PermissionDenied
            else:
                if view.action in ["retrieve", "partial_update", "stars", "remove_star"]:
                    return True
                raise PermissionDenied


class RepositoryViewSet(viewsets.ModelViewSet):
    serializer_class = RepositorySerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerOrOrgStuff]

    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        return super().get_permissions() 

    def get_object(self):
        obj = get_object_or_404(Repository, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj 

    def get_queryset(self):
          user = self.request.user
          if user.is_authenticated:
                return Repository.objects.filter(Q(user=user) | Q(visibility=Repository.Status.PUBLIC) | Q(collaborators__user=self.request.user))
          return Repository.objects.filter(visibility=Repository.Status.PUBLIC)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        repo = self.get_object()
        user = self.request.user

        if repo.organization is None and repo.user != user:
            allowed = {"description"}
            for field in list(serializer.validated_data.keys()):
                if field not in allowed:
                    raise PermissionDenied

        if repo.organization is not None:
            try:
                collab = Collaborator.objects.get(user=user, repository=repo)
            except Collaborator.DoesNotExist:
                pass
            else:
                allowed = {"description"} if collab.role == "WRITE" else set()
                for field in list(serializer.validated_data.keys()):
                    if field not in allowed:
                        raise PermissionDenied

        serializer.save()

    @action(detail=True, methods=["post"])
    def stars(self, request, pk=None, **kwargs):
        repo = self.get_object()
        user = request.user
        if Star.objects.filter(user=user, repository=repo).exists():
            return Response({"detail": "Already starred!"}, status=status.HTTP_409_CONFLICT)
        Star.objects.get_or_create(user=user, repository=repo)
        return Response(status=status.HTTP_201_CREATED)

    @stars.mapping.delete
    def remove_star(self, request, pk=None, **kwargs):
        repo = self.get_object()
        user = request.user
        if not Star.objects.filter(user=user, repository=repo).exists():
            return Response({"detail": "Not starred!"}, status=status.HTTP_409_CONFLICT)
        Star.objects.filter(user=user, repository=repo).delete()
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["post"])
    def transfer(self, request, pk=None, **kwargs):
        from apps.organizations.models import Organization
        repo = self.get_object()
        user = request.user 

        if request.data.get("user") and request.data.get("organization"):
            raise ValidationError("You can only transfer to either org or an user!")

        if not request.data.get("user") and not request.data.get("organization"):
            raise ValidationError("'user' or 'organization' have to be passed!")

        if request.data.get("user"):
            new_owner = get_object_or_404(CustomUser, username=request.data["user"])
            repo.user = new_owner
            repo.organization = None
        if request.data.get("organization"):
            new_owner = get_object_or_404(Organization, org_name=request.data["organization"])
            repo.organization = new_owner
            repo.user = None

        repo.save()

        Collaborator.objects.create(user=user, repository=repo)
        
        return Response({"detail": f"Ownership succesfully transferred to '{new_owner.org_name if isinstance(new_owner, Organization) else new_owner.username}'"}, status=status.HTTP_200_OK)



class IsRepositoryOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        from apps.organizations.models import OrgMember
        repo = get_object_or_404(Repository, pk=view.kwargs["repository_pk"])
        user = request.user
        
        if not user.is_authenticated:
            return False

        if repo.organization is not None:
            try:
                member = OrgMember.objects.get(user=request.user, organization=repo.organization)
            except OrgMember.DoesNotExist:
                raise PermissionDenied
            else:
                try:
                    collab = Collaborator.objects.get(user=request.user, repository=repo)
                except Collaborator.DoesNotExist:
                    pass
                else:
                    if collab.role == "ADMIN":
                        return True
            return member.role == "OWNER"

        return repo.user == user

class CollaboratorViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsRepositoryOwner]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_repo(self):
        if not hasattr(self, "_repo"):
            self._repo = get_object_or_404(Repository, pk=self.kwargs["repository_pk"])
        return self._repo

    def get_serializer_class(self):
        if self.action == 'create':
            return InvitationSerializer
        return CollaboratorSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["repository"] = self.get_repo()
        return context

    def get_queryset(self):
        return Collaborator.objects.filter(repository_id=self.kwargs["repository_pk"])
    

    def perform_create(self, serializer):
        repo =  self.get_repo()

        invitee = serializer.validated_data["invitee"]
       
        if self.request.user == invitee:
            raise ValidationError("Cant invite self!")

        if Collaborator.objects.filter(repository=repo, user=invitee).exists():
            raise ValidationError("User is already a collaborator!")

        if Invitation.objects.filter(repository=repo, invitee=invitee, status="PENDING").exists():
            raise ValidationError("User already has a pending invitation!")

        declined_invite = Invitation.objects.filter(repository=repo, invitee=invitee, status="DECLINED")
        if declined_invite.exists():
            declined_invite.update(status="PENDING")
            serializer.instance = declined_invite.first()
            return 
            

        serializer.save(invitee=invitee, repository=repo, invited_by=self.request.user)
    
class OrgRepositoryViewSet(RepositoryViewSet):
    from apps.organizations.views import IsOwnerMember
    from apps.organizations.models import Organization, OrgMember
    serializer_class = RepositorySerializer
    http_method_names = ['get', 'post']

    def get_permissions(self):
        if self.action in ["create", "transfer"]:
            return [permissions.IsAuthenticated(), self.IsOwnerMember()]
        if self.action in ["star", "remove_star"]:
            return [permissions.IsAuthenticated()]
        if self.action == "list":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        org = get_object_or_404(self.Organization, org_name=self.kwargs["org_org_name"])
        if self.request.user.is_authenticated:
            membership = self.OrgMember.objects.filter(user=self.request.user, organization=org).first()
            if membership and membership.role == "OWNER":
                return Repository.objects.filter(organization=org)
            return Repository.objects.filter(Q(visibility="PUBLIC") | Q(collaborators__user=self.request.user), organization=org)
        return Repository.objects.filter(organization=org, visibility="PUBLIC")

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_create(self, serializer):
        org = get_object_or_404(self.Organization, org_name=self.kwargs["org_org_name"])
        serializer.save(organization=org)
