from django import forms

class AddForm(forms.Form):
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea)

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)