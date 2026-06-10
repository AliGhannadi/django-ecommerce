from rest_framework import serializers
from rest_framework.response import Response
from accounts.models import User, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
       model = Profile
       fields = ("first_name", "last_name", "user",)
       
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ("id", "username", "profile")
        
        

