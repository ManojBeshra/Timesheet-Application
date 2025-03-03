from django import forms
from worklog . models import worklog

class WorklogForm(forms.ModelForm):
    class Meta: 
        model = worklog
        fields = [
            "user",
            "date",
            "workdone",
            "project_support",
            "ticket",
            "hours",
            "billable",
            "note",
            "priority",
            "category",
            "week",
            ]