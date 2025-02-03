# forms.py
from django import forms
from .models import ticket

class TicketForm(forms.ModelForm):
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