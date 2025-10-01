from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from .forms import RegisterForm, VerifyEmailForm
from .models import EmailVerification, ForgotPasswordVerification
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.mail import send_mail
from mail_account import email
import locale

locale.setlocale(locale.LC_ALL, "tr_TR.UTF-8")

class CustomLoginView(LoginView):
    template_name = 'auth_app/login.html'

    def form_invalid(self, form):
        username = form.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            form.add_error('username', "Kullanıcı bulunamadı.")
            return super().form_invalid(form)
        if not user.is_active:
            self.request.session["pending_user_id"] = user.pk
            self.request.session["pending_username"] = user.username
            self.request.session["pending_user_email"] = user.email
            return redirect("/verify_email")
        print("Giriş başarısız")
        return super().form_invalid(form)

def logout_view(request):
    logout(request)
    return redirect("login")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = request.POST.get("name").strip().title().split()
            user = User.objects.create_user(
                first_name = " ".join(name[:-1]).strip(),
                last_name = name[-1],
                username = form.cleaned_data["username"],
                email = form.cleaned_data["email"],
                password = form.cleaned_data["password"],
                is_active = False
            )

            request.session["pending_user_id"] = user.pk
            request.session["pending_username"] = user.username
            request.session["pending_user_email"] = user.email

            verification = EmailVerification.objects.create(user=user)
            send_mail("Doğrulama Kodunuz",
                      f"Doğrulama Kodunuz: {verification.code}",
                      email,
                      [user.email])

            return redirect("verify_email")
    else:
        form = RegisterForm()

    return render(request, "auth_app/register.html", {"form": form})

def verify_email(request):
    user_id = request.session.get("pending_user_id")
    username = request.session.get("pending_username")
    try:
        user_email = User.objects.get(username=username).email
    except:
        return redirect("home")
    if request.method == "POST":
        code = request.POST.get("code")
        print(code)
        try:
            verification = EmailVerification.objects.get(code=code, user_id=user_id, is_verified=False)
            verification.is_verified = True
            verification.code = ""
            verification.old_code = code
            verification.save()

            user = verification.user
            user.is_active = True
            user.save()

            if request.user:
                return redirect("profile")
            else:
                return redirect("login")
        except EmailVerification.DoesNotExist:
            messages.error(request, "Geçersiz kod.")
            return redirect("verify_email")
    else:
        if not request.user.is_authenticated and not request.user.is_active:
            if request.session.get("pending_username") == None:
                return redirect("home")
            else:
                return render(request, "auth_app/verify_email.html", {"username": username, "user_email": user_email})
    return redirect("home")

@login_required
def change_password(request):
    if request.method == "POST":
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Bilgileriniz başarıyla güncellendi.")
            return redirect("dashboard")
    else:
        password_form = PasswordChangeForm(user=request.user)
    return render(request, "auth_app/change_password.html", {"password_form": password_form})

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email = email)
            request.session['forgot_user_email'] = user.email
            verification, created = ForgotPasswordVerification.objects.get_or_create(user=user)
            if not created:
                verification.code = ForgotPasswordVerification.generate_code()
                verification.save()
            send_mail("Doğrulama Kodunuz",
                        f"Doğrulama Kodunuz: {verification.code}",
                        email,
                        [user.email])
            return redirect("forgot_password_verify")
        except User.DoesNotExist:
            messages.error(request, "Böyle bir kullanıcı bulunmamaktadır.")
            return redirect("forgot_password")
        
    return render(request, "auth_app/forgot_password.html")

def forgot_password_verify(request):
    try:
        user_email = request.session.get('forgot_user_email')
    except:
        return redirect("forgot_password")
    
    user = User.objects.get(email = user_email)

    if request.method == "POST":
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]

            try:
                verification = ForgotPasswordVerification.objects.get(code=code, user_id=user.pk)
            except:
                messages.error(request, "Yanlış kod girdiniz.")
                return redirect("forgot_password_verify")
            
            verification.is_verified = True
            verification.code = ""
            verification.old_code = code
            verification.save()

            request.session['forgot_user_email_verified'] = user.email
            request.session.pop('forgot_user_email', None)
            
            return redirect("forgot_password_change")

    else:
        form = VerifyEmailForm(request.POST)
        
    return render(request, "auth_app/forgot_password_verify.html", {"user_email": user_email, "form": form})

def forgot_password_change(request):
    try:
        user_email = request.session.get('forgot_user_email_verified')
    except:
        return redirect("forgot_password")
    
    user = User.objects.get(email = user_email)

    if request.method == "POST":
        password_form = SetPasswordForm(user=user, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            messages.success(request, "Bilgileriniz başarıyla güncellendi.")
            request.session.pop('forgot_user_email_verified', None)
            return redirect("login")
    else:
        password_form = PasswordChangeForm(user=request.user)
    return render(request, "auth_app/forgot_password_change.html", {"password_form": password_form})