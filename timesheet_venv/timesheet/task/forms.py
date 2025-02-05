# forms.py
from django import forms
from .models import ticket

from django.contrib.auth.models import User  # Import User model

class TicketForm(forms.ModelForm):
    # class Meta:
    #     model = ticket
    #     fields = [
            
    #         "ticket_title",
    #         "customer",
    #         "ticket_type",
    #         "date_opened",
    #         "priority",
    #         "assigned_to",
    #         "last_updated",
    #         "state",
    #         "short_description",
    #         "solution",
    #     ]
    #     widgets = {
    #         'date_opened': forms.DateInput(attrs={'type': 'date'}),
    #         'last_updated': forms.DateInput(attrs={'type': 'date'}),

    #     }
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = ticket
        fields = [
            
            "ticket_title",
            "customer",
            "ticket_type",
            "date_opened",
            "priority",
            "assigned_to",
            "last_updated",
            "state",
            "short_description",
            "solution",
        ]
        widgets = {
            'date_opened': forms.DateInput(attrs={'type': 'date'}),
            'last_updated': forms.DateInput(attrs={'type': 'date'}),

        }