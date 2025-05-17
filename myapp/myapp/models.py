from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()


class Language(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Dialect(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    language = models.ForeignKey(
        "Language", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        if self.language:
            return self.language.name + " - " + self.name
        else:
            return self.name


class Word(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    dialect = models.ForeignKey(
        Dialect, on_delete=models.CASCADE, null=True, blank=True
    )
    reading = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SpeechCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    similars = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.name


class Meaning(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    reading = models.CharField(max_length=255, blank=True)
    kana = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    dialect = models.ForeignKey(
        Dialect, on_delete=models.CASCADE, null=True, blank=True
    )
    speech_category = models.ForeignKey(
        SpeechCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    grammar_notes = models.ManyToManyField("GrammarNote", blank=True)
    comment = models.TextField(blank=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, null=True, blank=True)
    pictures = models.TextField(blank=True)  # Comma-separated links
    mp3 = models.TextField(blank=True)  # Comma-separated links
    youtube = models.TextField(blank=True)  # Comma-separated links
    source = models.TextField(blank=True)  # Comma-separated links
    categories = models.ManyToManyField("Category", blank=True)
    tags = models.ManyToManyField("Tag", blank=True)
    level = models.IntegerField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GrammarNote(models.Model):
    id = models.AutoField(primary_key=True)
    note = models.TextField()
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.note[:50]


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    similars = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Sentence(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    collocation = models.BooleanField(default=False)
    idiom = models.BooleanField(default=False)
    construction = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    dialect = models.ForeignKey(
        Dialect, on_delete=models.CASCADE, null=True, blank=True
    )
    source = models.TextField(blank=True)
    meaning = models.ManyToManyField(Meaning, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]


class Text(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    link = models.TextField(blank=True)
    fileName = models.CharField(max_length=255, blank=True)
    dialect = models.ForeignKey(
        Dialect, on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.TextField(blank=True)
    category = models.ManyToManyField(Category, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    translationFor = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    meanings = models.ManyToManyField(Meaning, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Synonym(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    meaning = models.ForeignKey(
        Meaning, on_delete=models.CASCADE, null=True, blank=True
    )
    dialect = models.ForeignKey(
        Dialect, on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.TextField(blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Meaning_Translation(models.Model):
    id = models.AutoField(primary_key=True)
    meaning = models.ForeignKey(
        Meaning, on_delete=models.CASCADE, null=True, blank=True
    )
    translation_content = models.TextField(blank=True)
    translation_dialect = models.ForeignKey(
        Dialect, on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.TextField(blank=True)
    reading = models.CharField(max_length=255, blank=True)
    kana = models.CharField(max_length=255, blank=True)
    mp3 = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    native_check_OK = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.translation_content[:50]


class Sentence_Translation(models.Model):
    id = models.AutoField(primary_key=True)
    sentence = models.ForeignKey(
        Sentence, on_delete=models.CASCADE, null=True, blank=True
    )
    translation_content = models.TextField(blank=True)
    translation_dialect = models.ForeignKey(
        Dialect, on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.TextField(blank=True)
    reading = models.CharField(max_length=255, blank=True)
    kana = models.CharField(max_length=255, blank=True)
    mp3 = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    native_check_OK = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.translation_content[:50]


class Scores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "meaning")

    def __str__(self):
        return self.user.username + " - " + self.meaning.name


class ADFile(models.Model):
    file = models.FileField(upload_to="excel")
