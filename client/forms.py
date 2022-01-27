from django import forms
import folium

class CreateGameForm(forms.Form):
    title = forms.CharField(label="Title", max_length="100", error_messages={
        "required": "This field cannot be empty",
        "max_length": "Too long name",
    })
    user_image = forms.ImageField()
    description = forms.CharField(label="Description", widget=forms.Textarea, max_length="300")


class GameInformationForm(forms.Form):
    description_information = forms.CharField(label="Description", widget=forms.Textarea, max_length="300")
    user_image_2 = forms.ImageField()


