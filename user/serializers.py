from rest_framework import serializers
from user.models import User, UserProfile
from rest_framework.authtoken.models import Token


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        if 'profile' in validated_data.keys():
            profile_data = validated_data.pop('profile')
        else:
            profile_data = {}
        password = validated_data.pop('password')
        del validated_data['groups']
        del validated_data['user_permissions']
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Token.objects.create(user=user)
        UserProfile.objects.create(user=user, **profile_data)
        return user