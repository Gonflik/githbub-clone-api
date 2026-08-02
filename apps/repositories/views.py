from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import RepositorySerializer, StarSerializer
from .models import Repository, Star

# Create your views here.


class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    @action(detail=True, methods=["post"])
    def stars(self, request, pk=None):
        repo = self.get_object()
        Star.objects.get_or_create(user=request.user, repository=repo)
        return Response(status=status.HTTP_201_CREATED)

    @stars.mapping.delete
    def remove_star(self, request, pk=None):
        repo = self.get_object()
        Star.objects.filter(user=request.user, repository=repo).delete()
        return Response(status=status.HTTP_200_OK)