from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import States

User = get_user_model


class CheckoutForm(forms.Form):
    company = forms.CharField(
        required=False,
        max_length=200,
        label="شرکت",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "input-payment-company",
                "placeholder": "شرکت",
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
            }
        ),
    )
    state = forms.ChoiceField(
        label="استان",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "input-state",
                "placeholder": "استان",
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
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        # Accept a 'profile' parameter to pre-fill fields from the user's profile
        profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)
        # Pre-fill fields with data from the profile if provided
        if profile:
            self.fields["address"].initial = profile.address
            self.fields["postcode"].initial = profile.postcode
            self.fields["city"].initial = profile.city

        # Dynamically set state choices from the database
        self.fields["state"].choices = [
            (state.id, state.name) for state in States.objects.all()
        ]

    def clean_postcode(self):
        data = self.cleaned_data["postcode"]
        if not data.isdigit():
            raise ValidationError(_("کد پستی فقط شامل اعداد است."))
        if len(data) != 10:
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
