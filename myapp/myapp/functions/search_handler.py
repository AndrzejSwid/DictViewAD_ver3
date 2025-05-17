from django.shortcuts import render
from myapp.models import Category, Dialect, Language, Meaning, Text
from django.db.models import Q, F, Value
from django.db.models.functions import Coalesce


# tag, speech_category, grammar_notes, level
def filter_meanings(request):
    meanings = Meaning.objects.all()

    # List of queries
    queries = [
        "category",
        "language",
        "dialect",
        "tag",
        "speech_category",
        "grammar_note",
        "level",
        "score",
    ]

    # Obtain queries from request
    results = {}
    for query in queries:
        results[query] = request.POST.get(query, "")

    # Filter
    if results["category"]:  # If a category is selected
        meanings = meanings.filter(categories=results["category"])

    if results["language"]:  # If a language (dialect) is selected
        filtered_dialects = Dialect.objects.filter(language=results["language"])
        meanings = meanings.filter(dialect__in=filtered_dialects)
    else:
        if results["dialect"]:  # If a dialect is selected
            meanings = meanings.filter(dialect=results["dialect"])

    if results["tag"]:  # If a tag is selected
        meanings = meanings.filter(tags__id=results["tag"])

    if results["speech_category"]:  # If a speech category is selected
        meanings = meanings.filter(speech_category=results["speech_category"])

    if results["grammar_note"]:  # If a grammar note is selected
        meanings = meanings.filter(grammar_notes__id=results["grammar_note"])

    if results["level"]:  # If a level is selected
        meanings = meanings.filter(level=results["level"])

    # if score is selected, filter by score below selected score
    if results["score"]:
        meanings = meanings.annotate(
            user_score=Coalesce(
                F("scores__score"),
                Value(0),  # Default to 0 if no score exists for this user
            )
        ).filter(
            Q(
                scores__user=request.user, user_score__lt=results["score"]
            )  # Include meanings with scores below selected_score
            | Q(
                scores__user__isnull=True, user_score__lt=results["score"]
            )  # Include meanings with no scores (treated as 0)
        )

    return meanings


def filter_texts(request):
    texts = Text.objects.all()

    # List of queries
    queries = ["category", "language", "dialect", "score"]

    # Obtain queries from request
    results = {}
    for query in queries:
        results[query] = request.POST.get(query, "")

    # Filter
    if results["category"]:  # If a category is selected
        texts = texts.filter(category=results["category"])

    if results["language"]:  # If a language (dialect) is selected
        filtered_dialects = Dialect.objects.filter(language=results["language"])
        texts = texts.filter(dialect__in=filtered_dialects)
    else:
        if results["dialect"]:  # If a dialect is selected
            texts = texts.filter(dialect=results["dialect"])

    # if score is selected, filter by score below selected score
    if results["score"]:
        texts = texts.filter(score__lt=results["score"])

    return texts
