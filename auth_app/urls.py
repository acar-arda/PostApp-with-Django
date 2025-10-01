from django.urls import path
from auth_app import views

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("verify_email/", views.verify_email, name="verify_email"),
    path("change_password/", views.change_password, name="change_password"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("forgot_password/verify/", views.forgot_password_verify, name="forgot_password_verify"),
    path("forgot_password/change/", views.forgot_password_change, name="forgot_password_change"),
]