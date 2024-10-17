from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import States
from django.core.validators import validate_email
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileForm(ModelForm):
    KHABAR_CHOICES = {
        ("TRUE", "مشترک خبرنامه"),
        ("FALSE", "عدم اشتراک در خبرنامه"),
    }

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "username",
            "address",
            "newsletter",
            "postcode",
            "city",
            "state",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "input-username",
                    "placeholder": "نام کاربریتان را وارد نمایید",
                }
            ),
            "newsletter": forms.Select(
                attrs={"class": "form-control", "id": "input-newsletter"}
            ),
            "postcode": forms.TextInput(
                attrs={
                    "input_type": "number",
                    "class": "form-control",
                    "id": "input-postcode",
                    "placeholder": "کد پستی را وارد نمایید",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "input-phone",
                    "placeholder": " شماره موبایل را وارد نمایید",
                }
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
            "email": forms.TextInput(
                attrs={
                    "input_type": "email",
                    "class": "form-control",
                    "id": "input-email",
                    "placeholder": "ایمیل را وارد نمایید",
                }
            ),
            "address": forms.TextInput(
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
                    "placeholder": "استان را وارد نمایید",
                }
            ),
        }


class CheckoutForm(forms.Form):
    @staticmethod
    def choices():
        s = States.objects.all()
        lst = []
        for i in s:
            lst.append((i.id, i.name))
        return tuple(lst)
    
    company = forms.CharField(
        required=False,
        max_length=200,
        label="شرکت",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "input-payment-company",
                "placeholder": "شرکت",
                "name": "company",
            }
        ),
    )
    address = forms.CharField(
        max_length=500,
        label="آدرس",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "input-address",
                "placeholder": "آدرس",
                "name": "address",
            }
        ),
    )
    postcode = forms.CharField(
        max_length=10,
        label="کد پستی",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "input-post-code",
                "placeholder": "کد پستی",
                "name": "postcode",
            }
        ),
    )
    city = forms.CharField(
        max_length=50,
        label="شهر",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "input-city",
                "placeholder": "شهر",
                "name": "city",
            }
        ),
    )
    state = forms.ChoiceField(
        label="استان",
        choices=choices,
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "input-state",
                "placeholder": "استان",
                "name": "state",
            }
        ),
    )
    desc = forms.CharField(
        required=False,
        label="توضیحات",
        widget=forms.Textarea(
            attrs={
                "rows": "4",
                "class": "form-control",
                "id": "confirm_comment",
                "name": "desc",
            }
        ),
    )

    def clean_postcode(self):
        data = self.cleaned_data["postcode"]
        if not data.isdigit():
            raise ValidationError(_("کد پستی فقط شامل اعداد است."))
        elif len(data) != 10:
            raise ValidationError(_("کد پستی باید 10 رقم باشد."))
        return data


class PriceFilter(forms.Form):
    minPrice = forms.IntegerField(
        required=False,
        label="از",
        widget=forms.TextInput(attrs={"type": "number", "value": "0"}),
    )
    maxPrice = forms.IntegerField(
        required=False,
        label="تا",
        widget=forms.TextInput(attrs={"type": "number", "value": "0"}),
    )

    def clean_min_price(self):
        data = self.cleaned_data["minPrice"]
        data_max = self.cleaned_data["maxPrice"]
        if data > data_max:
            raise ValidationError(_("مقدار نادرست است لطفا چک کنید!"))
        return data

    def clean_max_Price(self):
        data_min = self.cleaned_data["minPrice"]
        data = self.cleaned_data["maxPrice"]
        if data < data_min:
            raise ValidationError(_("مقدار نادرست است لطفا چک کنید!"))
        return data


# ist not complete and usable price filter

class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, required=True)
