from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField()
    target_language = forms.ChoiceField(
        choices=[("es", "Spanish"), ("fr", "French"), ("de", "German")],
        label="Target Language",
    )
