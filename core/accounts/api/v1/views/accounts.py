from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from accounts.api.v1.serializers import *
from rest_framework.decorators import action
from accounts.utils import Util
from django.contrib.sites.shortcuts import get_current_site
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from accounts.messages import Messages
from django.conf import settings
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from accounts.authenticator import CustomCookieJWTAuthenticator
from accounts.tasks import email_verification
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    # Generating jwt token
    # passing it to a url
    # if user enters that url
    # verification successfully
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email = user.email
        token = self.get_token_for_user(user)
        verification_link = f"https://127.0.0.1:8002/verify/{token}"
        email_verification.delay(user.username, email, verification_link)
        response = {
            "detail": Messages.registered_successfully
        }
        return Response(response, status=status.HTTP_200_OK)
    @staticmethod
    def get_token_for_user(user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
class EmailVerificationAPIView(generics.GenericAPIView):
    def get(self, request, token, *args, **kwargs):
        try:
            token_obj = AccessToken(token)
            user_id = token_obj["user_id"]
            user = User.objects.get(id=user_id)
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response(
                    {"detail": "Email verified successfully"},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Email is already verified."},
                    status=status.HTTP_200_OK
                )        
        except (TokenError, InvalidToken):
            return Response(
                {"error": "The verification link is invalid or has expired."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        

class LoginViewSet(viewsets.ModelViewSet):
    """
    Login view to handle login authentication
    """
    permission_classes = (AllowAny,)
    authentication_classes = () 
    queryset = User.objects.filter(is_active=True, is_verified=True)
    serializer_class = LoginSerializer

    @csrf_exempt
    @action(detail=False, methods=["post"], name="login")
    def login(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token = RefreshToken.for_user(user)
        access_token = str(token.access_token)
        refresh_token = str(token)  # This is the refresh token

        response = Response(
            {
                "user_id": user.id,
                "email": user.email,                
                "detail": Messages.authenticated_successfully,
            },
            status=status.HTTP_200_OK,
        )

        # Access token cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=access_token,
            domain=settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
            path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
            expires=int(
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", True),
            httponly=settings.SIMPLE_JWT.get("AUTH_COOKIE_HTTP_ONLY", True),
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
        )

        # Refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            domain=settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
            path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
            expires=int(
                settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", True),
            httponly=settings.SIMPLE_JWT.get("AUTH_COOKIE_HTTP_ONLY", True),
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
        )
        csrf_token = get_token(request)
        response.set_cookie(
            key='csrftoken',
            value=csrf_token,
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", True),
            httponly=False,  # Must be readable by JS to send in header
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            path="/",
        )

        return response


class ChangePasswordView(viewsets.GenericViewSet):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=["post"], name="change_password")
    def change_password(self, request, *args, **kwargs):
        self.object = self.request.user
        serializer = self.get_serializer(data=request.data, context={
                                         "request": self.request})

        serializer.is_valid(raise_exception=True)

        # set_password also hashes the password that the user will get
        self.object.set_password(serializer.data.get("new_password"))
        self.object.save()
        response = {
            'detail': Messages.password_changed_successfully,
        }

        return Response(response, status=status.HTTP_200_OK)


class RefreshTokenViewSet(viewsets.GenericViewSet):
    serializer_class = RefreshTokenSerializer
    permission_classes = (AllowAny,)
    authentication_classes = () 

    @csrf_exempt
    @action(detail=False, methods=["post"], name="refresh_token")
    def refresh_token(self, request):
        # Deserialize refresh token from cookie
        refresh_cookie = request.COOKIES.get("refresh_token")
        serializer = self.get_serializer(
            data={"refresh_token": refresh_cookie})
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh_obj = serializer.validated_data["refresh"]

        # Generate new tokens
        new_refresh = RefreshToken.for_user(user) if settings.SIMPLE_JWT.get(
            "ROTATE_REFRESH_TOKENS", False) else refresh_obj
        new_access = str(new_refresh.access_token)

        response = Response(
            {"detail": Messages.token_refreshed_successfully},
            status=status.HTTP_200_OK,
        )

        # Set access token cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=new_access,
            domain=settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
            path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", True),
            httponly=settings.SIMPLE_JWT.get("AUTH_COOKIE_HTTP_ONLY", True),
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
        )

        # Set refresh token cookie only if rotating
        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
            response.set_cookie(
                key="refresh_token",
                value=str(new_refresh),
                domain=settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
                path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
                expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", True),
                httponly=True,
                samesite=settings.SIMPLE_JWT.get(
                    "AUTH_COOKIE_SAMESITE", "Lax"),
            )

        # Update CSRF token
        csrf_token = get_token(request)
        response.set_cookie(
            key="csrftoken",
            value=csrf_token,
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", True),
            httponly=False,  # must be readable by JS
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            path="/",
        )

        return response


class PasswordResetRequestEmailApiView(viewsets.GenericViewSet):
    serializer_class = PasswordResetRequestEmailSerializer

    @action(detail=True, methods=["post"], name="reset_password_request")
    def reset_password_request(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = RefreshToken.for_user(user).access_token
        schema = "https" if settings.USE_SSL_CONFIG else "http"
        domain = settings.FRONTED_DOMAIN
        data = {'email': user.email, "domain": domain,
                "token": str(token), "schema": schema}
        Util.send_templated_email(
            'accounts/emails/reset_password_template.html', user.email, "Reset Password Request", data)
        return Response({'detail': Messages.password_reset_link_sent}, status=status.HTTP_200_OK)


class PasswordResetSetNewApiView(viewsets.GenericViewSet):
    serializer_class = SetNewPasswordSerializer

    @action(detail=True, methods=["patch"], name="reset_password_confirm")
    def reset_password_confirm(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'detail': Messages.password_reset_completed}, status=status.HTTP_200_OK)


class LogoutViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    authentication_classes = () 

    @csrf_exempt
    @action(detail=False, methods=["post"], name="logout")
    def logout(self, request):
        response = Response(
            {"detail": Messages.logout_successfully}, status=status.HTTP_200_OK)

        # Clear access token cookie
        response.delete_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
            domain=settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
        )

        # Clear refresh token cookie
        response.delete_cookie(
            key="refresh_token",
            path=settings.SIMPLE_JWT.get("AUTH_COOKIE_PATH", "/"),
            domain=settings.SIMPLE_JWT.get("AUTH_COOKIE_DOMAIN"),
        )

        # Optional: clear CSRF token
        response.delete_cookie("csrftoken", path="/")

        return response


class SessionVerifyView(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @action(detail=False, methods=["post"])
    def session_verify(self, request):
        authenticator = CustomCookieJWTAuthenticator()
        try:
            user, _ = authenticator.authenticate(request)
            if user is None:
                return Response({"is_authenticated": False}, status=401)

            return Response({
                "is_authenticated": True,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                }
            })
        except Exception:
            return Response({"is_authenticated": False}, status=401)
