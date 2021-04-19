from django.contrib.auth import authenticate

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from user.models import User
from user.serializers import UserSerializer


class UserViewList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LoginView(APIView):
    def post(self, request):
        id = request.data.get('username')
        pw = request.data.get('password')
        user = authenticate(username=id, password=pw)
        if user is not None:
            try:
                return Response({'Token': user.auth_token.key, 'id': user.id})
            except:
                return Response({'success': 'login success, but no token available'})
        else:
            return Response({'fail': 'no such user'})