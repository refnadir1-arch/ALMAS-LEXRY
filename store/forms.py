from django import forms

class StoreFilterForm(forms.Form):
    q = forms.CharField(required=False)
    category = forms.CharField(required=False)
    size = forms.CharField(required=False)
    color = forms.CharField(required=False)
    available = forms.CharField(required=False)
    sort = forms.CharField(required=False)