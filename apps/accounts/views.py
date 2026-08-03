from django.shortcuts import render
from rest_framework import routers, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User successfully created!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"error": "Invalid credentials!"}, status=status.HTTP_401_UNAUTHORIZED)

            refresh  = RefreshToken.for_user(user)

            return Response({"message": "Logged in!",
                            "access": str(refresh.access_token),
                            "refresh": str(refresh),}, status=status.HTTP_200_OK)

class ProfileView(APIView):

    def get(self, request):
        serializer = UserSerializer(request.user) 
        return Response(serializer.data)
# Create your views here.
