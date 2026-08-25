from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("phone_number", "delivery_method")
        widgets = {
            "phone_number": forms.TelInput(attrs={"placeholder": "050 000 00 00", "autocomplete": "tel"}),
            "delivery_method": forms.RadioSelect,
        }
