from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import StaffProfile


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control form-control-lg",
            "autofocus": True,
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-control form-control-lg",
        })


class StaffCreateForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": "form-control"}))
    display_name = forms.CharField(
        max_length=100, required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    role = forms.ChoiceField(
        choices=StaffProfile.ROLE_CHOICES, widget=forms.Select(attrs={"class": "form-select"})
    )

    def __init__(self, *args, allow_admin_role=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not allow_admin_role:
            self.fields["role"].choices = [(StaffProfile.KONOBAR, "Konobar")]
            self.fields["role"].initial = StaffProfile.KONOBAR
            self.fields["role"].widget = forms.HiddenInput()

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ky username ekziston tashmë.")
        return username

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password
