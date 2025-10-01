from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Şifre (Tekrar)")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise ValidationError("Şifreler uyuşmuyor")
        return cd["password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Bu e-posta zaten kayıtlı.")
        return email
    
class VerifyEmailForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, label="Doğrulama Kodu")