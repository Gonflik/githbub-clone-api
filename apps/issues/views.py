from django.shortcuts import render
from rest_framework import routers, viewsets
from models import Issue, Comment
from serializers import IssueSerializer, CommentSerializer
# Create your views here.




class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer



