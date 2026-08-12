from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import RepositorySerializer, StarSerializer, InvitationSerializer, CollaboratorSerializer
from rest_framework.permissions import AllowAny
from .models import Repository, Star, Invitation, Collaborator

# Create your views here.


class IsOwnerOrReadOnly(permissions.BasePermission):
      def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
             return True
        return obj.user == request.user
      
class RepositoryViewSet(viewsets.ModelViewSet):
    serializer_class = RepositorySerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        if self.action in ["stars", "remove_star"]:
            return [permissions.IsAuthenticated()]
        return super().get_permissions() 

    def get_object(self):
        obj = get_object_or_404(Repository, pk=self.kwargs["pk"])
        if obj.visibility == Repository.Status.PRIVATE and obj.user != self.request.user:
            raise PermissionDenied
        self.check_object_permissions(self.request, obj)
        return obj 

    def get_queryset(self):
          user = self.request.user
          if user.is_authenticated:
                return Repository.objects.filter(Q(user=user) | Q(visibility=Repository.Status.PUBLIC))
          return Repository.objects.filter(visibility=Repository.Status.PUBLIC)
    
    @action(detail=True, methods=["post"])
    def stars(self, request, pk=None):
        repo = self.get_object()
        user = request.user
        if Star.objects.filter(user=user, repository=repo).exists():
            return Response({"detail": "Already starred!"}, status=status.HTTP_409_CONFLICT)
        Star.objects.get_or_create(user=user, repository=repo)
        return Response(status=status.HTTP_201_CREATED)

    @stars.mapping.delete
    def remove_star(self, request, pk=None):
        repo = self.get_object()
        user = request.user
        if not Star.objects.filter(user=user, repository=repo).exists():
                    return Response({"detail": "Not starred!"}, status=status.HTTP_409_CONFLICT)
        Star.objects.filter(user=user, repository=repo).delete()
        return Response(status=status.HTTP_200_OK)


class CollaboratorViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    def get_serializer_class(self):
        if self.action == 'create':
            return InvitationSerializer
        return CollaboratorSerializer
    

    def perform_create(self, serializer):
        repo =  get_object_or_404(Repository, pk=self.kwargs["repository_pk"])
        #serializer.save(repository=repo, invited_by=self.request.user, invitee=)

class InvitationViewSet(viewsets.GenericViewSet):
    pass



