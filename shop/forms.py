from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("first_name", "last_name", "phone_number")
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Adınız", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Soyadınız", "autocomplete": "family-name"}),
            "phone_number": forms.TelInput(attrs={"placeholder": "050 000 00 00", "autocomplete": "tel"}),
        }
