from django import forms

class CreateGameForm(forms.Form):
    title = forms.CharField(label="Title", max_length="100", error_messages={
        "required": "This field cannot be empty",
        "max_length": "Too long name",
    })
    description = forms.CharField(label="Description", widget=forms.Textarea, max_length="300")