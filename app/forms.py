from django import forms
from django.forms import widgets
import datetime

class DateForm(forms.Form):
    date_selected = forms.DateField(initial=datetime.date.today, widget=widgets.DateInput(attrs={'type': 'date'}))
    csv_download = forms.BooleanField(required=False)