# forms.py
from django import forms
from .models import ticket

from django.contrib.auth.models import User  # Import User model

class TicketForm(forms.ModelForm):
    
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
            "priority",
            "assigned_to",
            "state",
            "short_description",
        ]
        widgets = {
            'date_opened': forms.DateInput(attrs={'type': 'date'}),
            'last_updated': forms.DateInput(attrs={'type': 'date'}),

        }


class SolutionForm(forms.ModelForm):

    class Meta:
        model = ticket
        fields = [

            "solution",
        ]

