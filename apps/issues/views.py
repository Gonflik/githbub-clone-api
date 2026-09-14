from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Issue, Comment, Label
from django.db.models import Q
from apps.repositories.models import Repository
from .serializers import IssueSerializer, CommentSerializer, LabelSerializer
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from apps.common.permissions import IsOwner
from apps.organizations.models import OrgMember
from apps.common.pagination import StandardPagination
# Create your views here.


class IsOwnerOrCollaboratorOrPublic(permissions.BasePermission):
    def __init__(self, skip_public: bool = False):
        self._skip_public = skip_public
        super().__init__()


    def has_permission(self, request, view):
        repo = get_object_or_404(Repository, pk=view.kwargs["repository_pk"])

        if not self._skip_public:
            if repo.visibility == "PUBLIC":
                return True
            else:
                if not request.user.is_authenticated:
                    return False
        is_owner = request.user == repo.user
        if repo.organization is not None:
            try:
                member = OrgMember.objects.get(user=request.user, organization=repo.organization)
            except OrgMember.DoesNotExist:
                is_owner = False
            else:
                is_owner = member.role == "OWNER"

          
        is_collaborator = repo.collaborators.filter(user=request.user).exists()

        return is_owner or is_collaborator


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            return [IsOwnerOrCollaboratorOrPublic()]
        if self.action in ["labels"]:
            return [permissions.IsAuthenticated(), IsOwnerOrCollaboratorOrPublic(skip_public=True)]
        if self.action == "create":
            return [IsOwnerOrCollaboratorOrPublic(), permissions.IsAuthenticated()]
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = Issue.objects.filter(repository=self.kwargs["repository_pk"]).prefetch_related("comments")
        label_ids = self.request.query_params.getlist('label')
        if label_ids:
            queryset = queryset.filter(labels__id__in=label_ids).distinct()

        search_param = self.request.query_params.get('q')
        if search_param:
            queryset = queryset.filter(
                Q(title__icontains=search_param) |
                Q(description__icontains=search_param)
            )

        return queryset

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

    @action(detail=True, methods=["post"])
    def labels(self, request, repository_pk=None, pk=None, **kwargs):
        issue = self.get_object()
        label_ids = request.data.get("labels", [])

        if not isinstance(label_ids, list) or not label_ids:
            return Response({"labels": "Expected a non-empty list of label IDs."}, status=status.HTTP_400_BAD_REQUEST)

        labels = Label.objects.filter(id__in=label_ids, repository=issue.repository)

        if labels.count() != len(label_ids):
            return Response({"labels": "One or more labels not found in this repository."}, status=status.HTTP_400_BAD_REQUEST)

        issue.labels.add(*labels)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["delete"], url_path="labels/(?P<label_id>[^/.]+)")
    def remove_label(self, request, repository_pk=None, pk=None, label_id=None):
        issue = self.get_object()

        label = get_object_or_404(Label, id=label_id, repository=issue.repository)

        if not issue.labels.filter(id=label.id).exists():
            return Response({"detail": "Label not on this issue."}, status=404)

        issue.labels.remove(label)
        return Response(status=status.HTTP_204_NO_CONTENT)


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



class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCollaboratorOrPublic]

    def get_queryset(self):
        return Label.objects.filter(repository=self.kwargs["repository_pk"])

    def perform_create(self, serializer):
        repo = get_object_or_404(Repository, pk=self.kwargs["repository_pk"])
        serializer.save(repository=repo)

