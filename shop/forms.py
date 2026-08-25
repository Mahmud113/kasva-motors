from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("delivery_method",)
        widgets = {
            "delivery_method": forms.RadioSelect,
        }
