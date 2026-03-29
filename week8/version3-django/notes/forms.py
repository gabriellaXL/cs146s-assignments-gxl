from django import forms

from .models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["title", "content", "status"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Release plan", "maxlength": 120}
            ),
            "content": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Capture the note details."}
            ),
            "status": forms.Select(),
        }

    def clean_title(self) -> str:
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        return title

    def clean_content(self) -> str:
        content = self.cleaned_data["content"].strip()
        if len(content) < 10:
            raise forms.ValidationError("Content must be at least 10 characters long.")
        return content
