from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from .models import Profile, Address
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .validators import phone_validator

User = get_user_model()


class UserProfileForm(ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "input-username",
                "placeholder": "نام کاربریتان را وارد نمایید",
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "id": "input-email",
                "placeholder": "ایمیل را وارد نمایید",
            }
        )
    )
    phone = forms.CharField(
        max_length=15,
        validators=[phone_validator],
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "input-phone",
                "placeholder": "شماره موبایل را وارد نمایید",
            }
        ),
    )

    class Meta:
        model = Profile
        fields = [
            "avatar",
            "username",
            "email",
            "phone",
            "first_name",
            "last_name",
            "age",
            "gender",
            "newsletter",
            # "postcode",
            # "city",
            # "state",
            # "address",
            "description",
        ]
        widgets = {
            "avatar": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "id": "input-avatar",
                }
            ),
            "newsletter": forms.Select(
                attrs={"class": "form-control", "id": "input-newsletter"}
            ),
            
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "input-first-name",
                    "placeholder": "نام را وارد نمایید",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "input-last-name",
                    "placeholder": "نام خانوادگی را وارد نمایید",
                }
            ),
            
            "age": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "id": "input-age",
                    "placeholder": "سن را وارد کنید",
                }
            ),
            "gender": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "input-gender",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "id": "input-description",
                    "placeholder": "توظیحات",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        # Capture the user instance to update User model fields
        self.user = kwargs.pop("user", None)
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # Set initial values for User model fields
        if self.user:
            self.fields["username"].initial = self.user.username
            self.fields["email"].initial = self.user.email
            self.fields["phone"].initial = self.user.phone

    def clean_email(self):
        email = self.cleaned_data.get("email")
        # Ensure the email is unique among all users except the current user
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError(
                "ایمیل دیگری را انتخاب کنید، این ایمیل قبلاً استفاده شده است."
            )
        return email
    
    def clean_postcode(self):
        data = self.cleaned_data["postcode"]
        if not data.isdigit():
            raise ValidationError(_("کد پستی فقط شامل اعداد است."))
        if len(data) != 10:
            raise ValidationError(_("کد پستی باید 10 رقم باشد."))
        return data

    def save(self, commit=True):
        # Update User model fields
        if self.user:
            self.user.username = self.cleaned_data["username"]
            self.user.email = self.cleaned_data["email"]
            self.user.phone = self.cleaned_data["phone"]

            if commit:
                self.user.save()

        # Update Profile model fields
        profile = super(UserProfileForm, self).save(commit=False)
        profile.user = self.user  # Associate the profile with the user

        if commit:
            profile.save()
        return profile


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'postal_address', 'full_name', 'phone_number',
            'neighborhood', 'city', 'state', 'license_plate', 'unit',
            'postal_code', 'is_default'
        ]
        widgets = {
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            "postal_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "input-address",
                    "placeholder": "ادرس را وارد نمایید",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "input-city",
                    "placeholder": "شهر را وارد نمایید",
                }
            ),
            "state": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "input-state",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "input-postcode",
                    "placeholder": "کد پستی را وارد نمایید",
                }
            ),
        }
