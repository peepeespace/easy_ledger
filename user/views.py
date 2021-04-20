from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions

from user.models import User
# from db.permissions import IsOwner
from user.serializers import UserSerializer


class UserViewList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = User.objects.all().order_by('id')
        username_by = self.request.GET.get('username')
        email_by = self.request.GET.get('email')
        if username_by:
            queryset = queryset.filter(username=username_by)
        if email_by:
            queryset = queryset.filter(email=email_by)
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)


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