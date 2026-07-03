from django.urls import path, include
from accounts.api.v1 import views


urlpatterns = [
    # Registration management
    path(
        "register",
        views.RegisterViewSet.as_view(
            {"post": "create"}
        ),
        name="register",
    ),
    path("verify/<str:token>/",
         views.EmailVerificationAPIView.as_view(),
         name="verification"
         ),
    path(
        "login",
        views.LoginViewSet.as_view({"post": "login"}),
        name="login",
    ),
    path(
        "logout",
        views.LogoutViewSet.as_view({"post": "logout"}),
        name="logout",
    ),
    path(
        "refresh-token",
        views.RefreshTokenViewSet.as_view({"post": "refresh_token"}),
        name="refresh-token",
    ),
    path(
        "session/verify",
        views.SessionVerifyView.as_view({"get": "session_verify"}),
        name="session-verify",
    ),


    # Password management
    path("change-password",
         views.ChangePasswordView.as_view({"post": "change_password"}),
         name="change_password"),
    
    path("reset-password",
         views.PasswordResetRequestEmailApiView.as_view({"post": "reset_password_request"}),
         name="reset_password_request"),
    
    path("reset-password/set-password",
         views.PasswordResetSetNewApiView.as_view({"post": "reset_password_confirm"}),
         name="reset_password_confirm"),

]
