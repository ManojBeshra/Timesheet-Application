from django import forms
from worklog . models import worklog, requestreview
from django.contrib.auth.models import User


class WorklogForm(forms.ModelForm):
    class Meta: 
        model = worklog
        fields = [
            # "user",
            # "date",
            "workdone",
            "ticket",
            "hours",
            "billable",
            "note",
            "category",
            ]
        
class RequestreviewForm(forms.ModelForm):
    send_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )
    requested_note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        required=False
    )

    class Meta:
        model = requestreview
        fields = [
            "send_to", 
            "requested_note"]