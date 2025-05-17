from django import forms


class UploadForm(forms.Form):
    TABLE_CHOICES = [
        ("Language", "Language"),
        ("Dialect", "Dialect"),
        ("Word", "Word"),
        ("SpeechCategory", "SpeechCategory"),
        ("Meaning", "Meaning"),
        ("GrammarNote", "GrammarNote"),
        ("Category", "Category"),
        ("Tag", "Tag"),
        ("Sentence", "Sentence"),
        ("Text", "Text"),
        ("Synonym", "Synonym"),
        ("Meaning_Translation", "Meaning_Translation"),
        ("Sentence_Translation", "Sentence_Translation"),
    ]

    table = forms.ChoiceField(choices=TABLE_CHOICES, label="Choose Table")
    file = forms.FileField(label="Upload File")
