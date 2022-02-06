from django import forms

class CreateGameForm(forms.Form):
    title = forms.CharField(label="Title", max_length="100", error_messages={
        "required": "This field cannot be empty",
        "max_length": "Too long name",
    })
    picture = forms.ImageField()
    description = forms.CharField(label="Description", widget=forms.Textarea, max_length="300")

class GameInformationForm(forms.Form):
    picture = forms.ImageField()
    clue = forms.CharField(label="Clue", widget=forms.Textarea, max_length="300")
    coordinates = forms.CharField(
        label="Location", widget=forms.Textarea, max_length="50")


class MapForm(forms.Form):
    map_name = forms.CharField(label='map name', max_length=100)