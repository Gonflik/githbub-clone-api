from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, permissions
from .models import Issue, Comment
from apps.repositories.models import Repository
from .serializers import IssueSerializer, CommentSerializer
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from apps.common.permissions import IsOwner
# Create your views here.


class IsOwnerOrCollaboratorOrPublic(permissions.BasePermission):
    def has_permission(self, request, view):
        repo = get_object_or_404(Repository, pk=view.kwargs["repository_pk"])

        if repo.visibility == "PUBLIC":
            return True

        if not request.user.is_authenticated:
            return False

        is_owner = repo.user == request.user    
        is_collaborator = repo.collaborators.filter(pk=request.user.pk).exists()

        return is_owner or is_collaborator


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerOrCollaboratorOrPublic]

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            return [IsOwnerOrCollaboratorOrPublic()]
        if self.action in ["create", "partial_update"]:
            return [permissions.IsAuthenticated(), IsOwnerOrCollaboratorOrPublic()]
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), IsOwner()]
        return super().get_permissions() 

    def get_queryset(self):
        return Issue.objects.filter(repository=self.kwargs["repository_pk"]).prefetch_related("comments")

    def perform_create(self, serializer):
        repo = get_object_or_404(Repository, pk=self.kwargs["repository_pk"])
        serializer.save(user=self.request.user, repository=repo)

    def partial_update(self, request, *args, **kwargs):
        obj = self.get_object()
        repo = get_object_or_404(Repository, pk=self.kwargs["repository_pk"])

        if request.user == obj.user:
            pass
        elif request.user == repo.user and set(request.data.keys()) == {"status"}:
            pass
        else:
            raise PermissionDenied
        
        return super().partial_update(request, *args, **kwargs)


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet
):
    serializer_class = CommentSerializer
    http_method_names = ["post", "patch", "delete"]

    def get_queryset(self):
        return Comment.objects.filter(issue=self.kwargs["issue_pk"], user=self.request.user, issue__repository_id=self.kwargs["repository_pk"])

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, pk=self.kwargs["issue_pk"], repository=self.kwargs["repository_pk"])
        serializer.save(user=self.request.user, issue=issue)


