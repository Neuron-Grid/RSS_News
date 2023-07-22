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
    interval = forms.IntegerField(
        label='更新間隔',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=1,
        max_value=10080,
        initial=300
    )