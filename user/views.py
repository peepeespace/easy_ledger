import json
import hashlib
import datetime
from cryptography.fernet import Fernet

from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User
from db.models import ClientSession
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
    """
    REST 로그인 기능은 jwt token endpoint로 보내어 시도한다.

    LoginView는 소켓 연결을 하기 전에 로그인과 동시에 token 정보를 받기 위함이다.
    """
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        session_type = request.data.get('session_type')

        user = authenticate(username=username, password=password)

        if user is not None:
            # 현존하는 소켓 연결이 있는지 확인한다.
            existing_conn = ClientSession.objects.filter(user=user, session_type=session_type).all()
            if existing_conn:
                # 연결을 하나로 제한 (추후 변경 가능)
                existing_conn.delete()

            # Create Fernet key
            key = Fernet.generate_key()
            key_str = key.decode('utf-8')

            # Create JWT Tokens
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]

            tokens = RefreshToken.for_user(user)
            refresh_token = str(tokens)
            access_token = str(tokens.access_token)

            user_info = {
                'username': username,
                'timestamp': timestamp,
                'refresh_token': refresh_token,
                'access_token': access_token
            }

            session_id = hashlib.sha1(json.dumps(user_info).encode('utf-8')).hexdigest()

            session = ClientSession(user=user,
                                    is_authenticated=True,
                                    timestamp=timestamp,
                                    session_type=session_type,
                                    session_id=session_id,
                                    key=key_str)
            session.save()

            return Response({'status': 'success', 'user': user.id, 'result': user_info, 'key': key_str}, status=200)
        else:
            return Response({'status': 'failed', 'message': 'wrong credentials'}, status=400)