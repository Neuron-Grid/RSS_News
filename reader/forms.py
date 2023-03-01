from django import forms

class AddFeedForm(forms.Form):
    feed_name = forms.CharField(
        label='フィード名',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    url = forms.URLField(
        label='URL',
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

