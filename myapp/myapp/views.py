import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from myapp.forms import *

from .functions.fileIO_handler import db_to_excel, excel_to_db, load_all_files
from .functions.search_handler import filter_meanings, filter_texts
from .models import *


@login_required
def upload_view(request):
    messages = []

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "single_upload":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                table = form.cleaned_data["table"]
                file = request.FILES["file"]

                # Call the separate processing function
                success, message = excel_to_db(file, table)
                messages.append(message)
            else:
                messages.append("Form is not valid")

        elif form_type == "all_upload":
            success, message = load_all_files()
            messages.append(message)
            form = UploadForm()

    else:
        form = UploadForm()

    context = {"form": form, "messages": messages}

    return render(request, "myapp/upload.html", context)


@login_required
def download_view(request):
    response = db_to_excel()
    return response


@login_required
def excel_view(request):
    return render(request, "myapp/excel.html")


@login_required
def main_view(request):
    return render(request, "myapp/main.html")


# TODO optimize db usage
@login_required
def database_view(request):
    # Get all categories, languages (dialects) from the database
    categories = Category.objects.all()
    dialects = Dialect.objects.all()
    languages = Language.objects.all()
    tags = Tag.objects.all()
    speech_categories = SpeechCategory.objects.all()
    grammar_notes = GrammarNote.objects.all()
    meanings = None
    texts = None
    selected_search_type = None

    selected_category_id = request.POST.get("category", "")
    selected_language_id = request.POST.get("language", "")
    selected_dialect_id = request.POST.get("dialect", "")
    selected_tag_id = request.POST.get("tag", "")
    selected_speech_category_id = request.POST.get("speech_category", "")
    selected_grammar_note_id = request.POST.get("grammar_note", "")
    selected_level = request.POST.get("level", "")
    selected_score = request.POST.get("score", "")

    if request.method == "POST":
        selected_search_type = request.POST.get("search_type")

        if selected_search_type == "meaning_search":
            meanings = (
                filter_meanings(request)
                .prefetch_related("meaning_translation_set")
                .prefetch_related("sentence_set")
                .prefetch_related("sentence_set__sentence_translation_set")
            )

            # filter sentence_set and check if selected category is in categories
            if selected_category_id:
                for meaning in meanings:
                    meaning.sentence_set.set(
                        meaning.sentence_set.filter(categories=selected_category_id)
                    )

            # prefetch related sentence_translation from meanings.sentence
            for meaning in meanings:

                for sentence in meaning.sentence_set.all():
                    sentence.sentence_translation_set.set(
                        sentence.sentence_translation_set.all()
                    )

            # filter sentence
            request.session["search_results"] = [result.id for result in meanings]
            request.session["mode"] = "Meaning"

        elif selected_search_type == "text_search":
            texts = filter_texts(request).prefetch_related("meanings")

            # Fetch translations for texts where 'translationFor' points to this text
            for text in texts:
                text.translations = Text.objects.filter(translationFor=text)

            request.session["search_results"] = [result.id for result in texts]
            request.session["mode"] = "Text"

    # Pass the context to the template
    context = {
        "categories": categories,
        "languages": languages,
        "dialects": dialects,
        "tags": tags,
        "speech_categories": speech_categories,
        "grammar_notes": grammar_notes,
        "meanings": meanings,
        "texts": texts,
        "selected_search_type": selected_search_type,
        "selected_category_id": selected_category_id,
        "selected_language_id": selected_language_id,
        "selected_dialect_id": selected_dialect_id,
        "selected_tag_id": selected_tag_id,
        "selected_speech_category_id": selected_speech_category_id,
        "selected_grammar_note_id": selected_grammar_note_id,
        "selected_level": selected_level,
        "selected_score": selected_score,
    }
    return render(request, "myapp/view_database.html", context)


# TODO apply strategy(?)
@login_required
def play_view(request):

    if request.method == "POST":
        result_ids = request.session.get("search_results", [])
        # Check if should look for meanings or texts
        mode = request.session.get("mode", "")
        if mode == "Meaning":
            meanings = Meaning.objects.filter(id__in=result_ids)
            names = list(meanings.values_list("name", flat=True))
            translations = {}

            for meaning in meanings:
                translation = Meaning_Translation.objects.filter(
                    meaning=meaning
                ).first()
                if translation:
                    translations[meaning.name] = translation.translation_content

        elif mode == "Text":
            texts = Text.objects.filter(id__in=result_ids)
            names = list(texts.values_list("title", flat=True))
            translations = {}

            for text in texts:
                translation = Text.objects.filter(translationFor=text).first()
                if translation:
                    translations[text.id] = translation.title

        return render(
            request,
            "myapp/play.html",
            {
                "names": names,
                "translations": translations,
            },
        )

    return render(request, "myapp/play.html")


# TODO apply strategy(?)
@login_required
def test_view(request):
    if request.method == "POST":
        result_ids = request.session.get("search_results", [])
        # Check if should look for meanings or texts
        mode = request.session.get("mode", "")
        if mode == "Meaning":
            meanings = Meaning.objects.filter(id__in=result_ids)
            names = list(meanings.values_list("name", flat=True))
            translations = {}

            for meaning in meanings:
                translation = Meaning_Translation.objects.filter(
                    meaning=meaning
                ).first()
                if translation:
                    translations[meaning.name] = translation.translation_content
        elif mode == "Text":
            texts = Text.objects.filter(id__in=result_ids)
            names = list(texts.values_list("title", flat=True))
            translations = {}

            for text in texts:
                try:
                    translation = Text.objects.filter(translationFor=text).first()
                except:
                    translation = None
                if translation:
                    translations[text.id] = translation.title

        return render(
            request,
            "myapp/test.html",
            {
                "names": names,
                "translations": translations,
            },
        )


@login_required
def text_details_view(request, text_id):
    text = get_object_or_404(Text, id=text_id)
    meanings = text.meanings.all()  # Get all meanings associated with the text
    context = {"text": text, "meanings": meanings}
    return render(request, "myapp/text_details.html", context)


@login_required
def meaning_details_view(request, meaning_id):
    meaning = get_object_or_404(Meaning, id=meaning_id)

    # Split comma-separated fields
    pictures = meaning.pictures.split(",") if meaning.pictures else []
    mp3_files = meaning.mp3.split(",") if meaning.mp3 else []
    youtube_links = meaning.youtube.split(",") if meaning.youtube else []
    sources = meaning.source.split(",") if meaning.source else []

    texts = Text.objects.filter(meanings=meaning)

    context = {
        "meaning": meaning,
        "pictures": pictures,
        "mp3_files": mp3_files,
        "youtube_links": youtube_links,
        "sources": sources,
        "texts": texts,
    }
    return render(request, "myapp/meaning_details.html", context)


# TODO texts but idk how?
@csrf_exempt
@login_required
def save_scores(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            response = {}
            oneSuccess = False

            user = request.user  # Assuming user is authenticated

            for meaning_name, score_change in data.items():
                try:
                    # Retrieve or create the Score entry for the user and meaning
                    meaning = Meaning.objects.get(name=meaning_name)
                    score_obj, created = Scores.objects.get_or_create(
                        user=user, meaning=meaning
                    )

                    # Update the score and save
                    score_obj.score += score_change
                    score_obj.save()
                    oneSuccess = True

                except Meaning.DoesNotExist:
                    # If meaning is not found, add an error to the response
                    response[f"error-{meaning_name}"] = (
                        f"Meaning with name '{meaning_name}' not found."
                    )

            if oneSuccess:
                response["message"] = "Scores saved successfully."

            return JsonResponse(response)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)
