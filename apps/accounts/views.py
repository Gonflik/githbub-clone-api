from django.shortcuts import render
from rest_framework import routers, viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import ValidationError
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from .models import CustomUser
from apps.common.pagination import StandardPagination

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User successfully created!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_tokens(user):
    refresh  = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                username=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if not user:
                return Response({"detail": "Invalid credentials!"}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({"message": "Logged in!",
                            "tokens": get_tokens(user)}, status=status.HTTP_200_OK)

class MeView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user) 
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(CustomUser, username=username)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token required!"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out!"},status=status.HTTP_200_OK)
        except TokenError:
            return Response({"detail": "Invalid token!"}, status=status.HTTP_400_BAD_REQUEST)


class RepositoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get(self, request, username=None):
        from apps.repositories.serializers import RepositorySerializer
        from apps.repositories.models import Repository
        user = get_object_or_404(CustomUser, username=username)

        if user != self.request.user:
            queryset = Repository.objects.filter(
                Q(user=user) & (Q(visibility=Repository.Status.PUBLIC) | Q(collaborators__user=self.request.user))
            ).distinct()
        else:
            queryset = Repository.objects.filter(user=user)

        search_param = request.query_params.get('q')
        if search_param:
            queryset = queryset.filter(
                Q(name__icontains=search_param) |
                Q(description__icontains=search_param)
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = RepositorySerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

class UserSearchView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardPagination


    def get(self, request):
        search_param = request.query_params.get('q')
        if not search_param:
            raise ValidationError("You need a query param(q=) for search!")

        queryset = CustomUser.objects.filter(
            Q(username__icontains=search_param) |
            Q(display_name__icontains=search_param)
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

# Create your views here.
