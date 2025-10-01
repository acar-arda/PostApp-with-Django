from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from auth_app.models import EmailVerification
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from mail_account import email
import locale

locale.setlocale(locale.LC_ALL, "tr_TR.UTF-8")

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

@login_required
def profile_update(request):
    if request.method == "POST":
        profile_form = ProfileUpdateForm(request.POST, user=request.user, instance=request.user)
        old_email = User.objects.get(id = request.user.id).email
        if profile_form.is_valid():
            name = request.POST.get("name").strip().title().split()
            first_name = " ".join(name[:-1]).strip()
            last_name = name[-1]
            updated_user = profile_form.save(commit=False)
            updated_user.first_name = first_name
            updated_user.last_name = last_name
            updated_user.save()
            
            user = User.objects.get(id = request.user.id)
            new_email = user.email
            if old_email != new_email:
                user.is_active = False
                user.save()

                request.session["pending_user_id"] = user.pk
                request.session["pending_username"] = user.username
                request.session["pending_user_email"] = user.email

                verification = EmailVerification.objects.get(user=user)
                verification.is_verified = False
                verification.code = EmailVerification.generate_code()
                verification.save()
                send_mail("Doğrulama Kodunuz",
                        f"Doğrulama Kodunuz: {verification.code}",
                        email,
                        [user.email])

                return redirect("verify_email")
            else:
                messages.success(request, "Bilgileriniz başarıyla güncellendi.")
                return redirect("dashboard")
    else:
        profile_form = ProfileUpdateForm(user=request.user, instance=request.user)

    return render(request, "profile.html", {"profile_form": profile_form})