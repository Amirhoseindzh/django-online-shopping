from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .models import States

User = get_user_model


class CheckoutForm(forms.Form):
    postal_address = forms.CharField(
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
    postal_code = forms.CharField(
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
        address = kwargs.pop("address", None)
        super().__init__(*args, **kwargs)
        # Pre-fill fields with data from the profile if provided
        
        if address:
            for data in address:
                self.fields["postal_address"].initial = data.postal_address
                self.fields["postal_code"].initial = data.postal_code
                self.fields["city"].initial = data.city

        # Dynamically set state choices from the database
        self.fields["state"].choices = [
            (state.id, state.name) for state in States.objects.all()
        ]

    def clean_postal_code(self):
        data = self.cleaned_data["postal_code"]
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

    def clean_minPrice(self):
        min_price = self.cleaned_data.get("minPrice")
        max_price = self.cleaned_data.get("maxPrice")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationError(_("مقدار نادرست است لطفا چک کنید!"))
        return min_price

    def clean_maxPrice(self):
        min_price = self.cleaned_data.get("minPrice")
        max_price = self.cleaned_data.get("maxPrice")
        if min_price is not None and max_price is not None and max_price < min_price:
            raise ValidationError(_("مقدار نادرست است لطفا چک کنید!"))
        return max_price


# ist not complete and usable price filter
class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, required=True)
