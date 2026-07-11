from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from accounts.api.v1.exceptions import CustomValidationException
from accounts.messages import Messages
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """Registration serializer with password checkup"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True, required=True,
        style={
            'input_type': 'password',
        }
    )
    password1 = serializers.CharField(
        max_length=68, min_length=6, write_only=True, required=True,
        style={
            'input_type': 'password',
        }
    )

    class Meta:
        model = User
        fields = ["email", "username", "phone_number", "password", "password1"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password1"]:
            raise serializers.ValidationError(
                {"details": Messages.passwords_doesnt_match}
            )
            
        if User.objects.filter(email=attrs.get("email")).exists():
            raise CustomValidationException(
                {"detail": Messages.registration_failed})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password1")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    """Login serializer"""
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': Messages.email_missing,
        }
    )
    password = serializers.CharField(required=True,
        error_messages={
            'required': Messages.password_missing,
        })

    class Meta:
        model = User
        fields = ["email",'password']

    def validate(self, attrs):
        attrs["user"] = None
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(is_active=True, is_verified=True, email=email)
        except User.DoesNotExist:
            raise CustomValidationException(
                {'detail': Messages.user_not_found})
            
        user = authenticate(request=self.context.get("request"), email=email, password=password)
        if not user:
            raise CustomValidationException(
                {'detail': Messages.invalid_credentials})
        else:
            attrs["user"] = user
        return super().validate(attrs)



class RefreshTokenSerializer(serializers.Serializer):
    def validate(self, attrs):
        request = self.context.get("request")
        token = request.COOKIES.get("refresh_token")

        if not token:
            raise CustomValidationException({'detail': Messages.jwt_missing})

        try:
            refresh = RefreshToken(token)
            user = User.objects.get(id=refresh["user_id"])
        except TokenError:
            raise CustomValidationException({'detail': Messages.jwt_invalid})
        except User.DoesNotExist:
            raise CustomValidationException({'detail': Messages.jwt_invalid})

        attrs["user"] = user
        attrs["refresh"] = refresh
        return attrs


class PasswordResetRequestEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise CustomValidationException(
                {"detail": Messages.no_user_with_email})
        attrs["user"] = user
        return super().validate(attrs)


class PasswordResetTokenVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=600)

    class Meta:
        model = User
        fields = ['token']

    def validate(self, attrs):
        token = attrs['token']
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
        except jwt.ExpiredSignatureError as identifier:
            raise CustomValidationException({'detail': Messages.token_expired})
        except jwt.exceptions.DecodeError as identifier:
            raise CustomValidationException({'detail': Messages.token_invalid})

        attrs["user"] = user
        return super().validate(attrs)


class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=600)
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    password1 = serializers.CharField(
        min_length=6, max_length=68, write_only=True)

    class Meta:
        fields = ['password', 'password1', 'token']

    def validate(self, attrs):
        if attrs["password"] != attrs["password1"]:
            raise CustomValidationException(
                {"details": Messages.passwords_doesnt_match}
            )
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            user.set_password(password)
            user.save()

            return super().validate(attrs)
        except Exception as e:
            raise AuthenticationFailed(Messages.reset_link_invalid, 401)
class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        request = self.context.get("request")     
        if not request.user.check_password(attrs["old_password"]):
            raise CustomValidationException(
                {"detail": Messages.old_password_doenst_match})
        
        if attrs["new_password"] != attrs["new_password1"]:
            raise CustomValidationException(
                {"detail": Messages.new_password_doenst_match})
            
        return attrs
    
    