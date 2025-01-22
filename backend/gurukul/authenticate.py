from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from rest_framework import generics
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm




class HomepageAPIView(APIView):
    '''
        This is just an example view for checking backend as this scenario will be handled in frontend
    '''
    def get(self, request):
        url_data = {
            'Signup': 'http://127.0.0.1:8000/signup',
            'Login': 'http://127.0.0.1:8000/login',
            'Logout': 'http://127.0.0.1:8000/logout',
            'Users': 'http://127.0.0.1:8000/users',

        }
        return Response(url_data, status=status.HTTP_200_OK)


# class UserCreate(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class SignupAPIView(ObtainAuthToken):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password1')
#         if not username or not password:
#             return Response({'error': 'Username and password are required'}, status=400)

#         user = User.objects.create_user(username=username, password=password)
#         token, _ = Token.objects.get_or_create(user=user)
#         # return Response({'token': token.key})
#         response = Response({'token': token.key})

#         # # Set token in response headers
#         # response['Authorization'] = f'Token {token.key}'

#         # Redirect user to a different URL
#         return redirect('login')


class UserLogin(APIView):

    # def get(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         return Response({'error': 'User Already Authenticated'}, status=status.HTTP_400_BAD_REQUEST)
    #     data = {"email" : "" ,"password" : ""}
    #     return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data

            refresh = RefreshToken.for_user(user)

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.COOKIES['auth_token'] = ''
        print(request.user)
        logout(request)
        response = Response("Logged out successfully.")
    
    # Redirect shortly
        response['Refresh'] = '3; url=/'  # Redirect to '/new-page/' after 3 seconds
    
        return response
        # return Response({'success': 'Logged out successfully'})
