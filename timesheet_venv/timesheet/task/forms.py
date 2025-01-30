# forms.py
from django import forms
from .models import ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = ticket
        fields = [
            
            "ticket_name",
            "customer",
            # "ticket_type",
            "date_opened",
            "priority",
            "assigned_to",
            "last_updated",
            # "state",
            "short_description",
            "comments",
            # "user_comments"
        ]
        widgets = {
            'date_opened': forms.DateInput(attrs={'type': 'date'}),
            'last_updated': forms.DateInput(attrs={'type': 'date'}),

        }