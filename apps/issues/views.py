from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins
from .models import Issue, Comment
from apps.repositories.models import Repository
from .serializers import IssueSerializer, CommentSerializer
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
# Create your views here.




class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions() 

    def get_object(self):
        repo = get_object_or_404(Repository, pk=self.kwargs["repository_pk"])

        if repo.visibility == Repository.Status.PRIVATE and self.request.user != repo.user:
            raise PermissionDenied
                
        queryset = Issue.objects.prefetch_related("comments")
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])

        if self.action in ["update", "partial_update", "destroy"]:
            if obj.user != self.request.user:
                raise PermissionDenied

        return obj

    def get_queryset(self):
        repo = get_object_or_404(Repository, pk=self.kwargs["repository_pk"])

        if repo.visibility == Repository.Status.PRIVATE and self.request.user != repo.user:
            raise PermissionDenied
        
        return Issue.objects.filter(repository=repo).prefetch_related("comments")

    def perform_create(self, serializer):
        repo = get_object_or_404(Repository, pk=self.kwargs["repository_pk"])
        serializer.save(user=self.request.user, repository = repo)

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


