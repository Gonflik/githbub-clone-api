from django.shortcuts import render
from rest_framework import routers, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User successfully created!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer
        if serializer.is_valid():
            user = authenticate(
                request,
                username=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            ),
            if not user:
                return Response({"error": "Invalid credentials!"}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({"message": "Logged in!need to add JWT and shit..",
                             "tokens": get_tokens(user)}, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user) 
        return Response(serializer.data)
# Create your views here.
