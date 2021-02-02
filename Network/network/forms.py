from django import forms

class AddForm(forms.Form):
    new_post = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Add new post...'}))