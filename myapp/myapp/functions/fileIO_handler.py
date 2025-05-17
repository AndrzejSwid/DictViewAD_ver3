import csv
import zipfile
import os

import pandas as pd

from django.http import HttpResponse

from myapp.models import *
from io import StringIO, BytesIO
from django.http import HttpResponse

from django.db import models, transaction
from django.apps import apps

exceptions = [
    "meaning",
    "sentence",
    "category",
]


def db_to_excel(write_rows=False):
    # Create a BytesIO object to hold the zip file in memory
    zip_buffer = BytesIO()

    # Create a ZipFile object to write to the zip_buffer
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        models = [
            Language,
            Dialect,
            Word,
            SpeechCategory,
            Meaning,
            GrammarNote,
            Category,
            Tag,
            Sentence,
            Text,
            Synonym,
            Meaning_Translation,
            Sentence_Translation,
        ]

        for model in models:
            # Create a StringIO object to hold the CSV data in memory
            csv_buffer = StringIO()

            # Get the model's fields
            field_names = [field.name for field in model._meta.fields]

            # Check for ManyToMany fields and add them to field names
            m2m_field_names = [field.name for field in model._meta.many_to_many]
            all_field_names = field_names + m2m_field_names

            # Create a CSV writer object
            writer = csv.DictWriter(
                csv_buffer, fieldnames=all_field_names, delimiter="$"
            )
            writer.writeheader()

            if write_rows:
                # Write data rows
                for obj in model.objects.all():
                    row = {}
                    for field in field_names:
                        row[field] = getattr(obj, field)

                    # Handle ManyToMany fields
                    for m2m_field in m2m_field_names:
                        m2m_values = getattr(obj, m2m_field).all()
                        row[m2m_field] = ";".join(
                            [str(m2m_value) for m2m_value in m2m_values]
                        )

                    writer.writerow(row)

            # Get the name of the CSV file
            if model._meta.model_name in exceptions:
                # Handle special cases
                csv_file_name = f"{model._meta.model_name}s.csv"
            else:
                # Default CSV file name
                csv_file_name = f"{model._meta.model_name}.csv"

            # Write the CSV buffer to the zip file
            zip_file.writestr(csv_file_name, csv_buffer.getvalue())

    # Reset the buffer position to the start
    zip_buffer.seek(0)

    # Create the HttpResponse to send the zip file
    response = HttpResponse(zip_buffer, content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="database_export.zip"'

    return response


def get_or_create_related(related_model, value):
    # Field names to search for before creating new object
    field_names = ["name", "content", "title", "translation_content", "note"]

    for field_name in field_names:
        # If object has specified field
        if hasattr(related_model, field_name):
            # Get the related object or create it if it doesn't exist
            related_obj = related_model.objects.filter(**{field_name: value}).first()
            if related_obj is None:
                related_obj = related_model.objects.create(**{field_name: value})
            return related_obj

    # If the related model doesn't have specified field
    # Most likely an error
    # Raise exception returning the table name and its fields
    raise Exception(
        f"Related model {related_model._meta.model_name} Fields: {related_model._meta.get_fields()}"
    )


def excel_to_db(file, table_name):

    # If file is passed as string or file, open it
    if isinstance(file, str):
        if file.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            return False, "Invalid file format, only CSV and XLSX files are supported."
    else:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            return False, "Invalid file format, only CSV and XLSX files are supported."

    # Convert all strings to lowercase
    df = df.map(lambda x: x.lower() if isinstance(x, str) else x)

    # Get the model class for the specified table
    model = apps.get_model(app_label="myapp", model_name=table_name)

    # Get field information
    fields = model._meta.get_fields()
    field_dict = {f.name: f for f in fields if f.name != "id"}

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        with transaction.atomic():
            # See if the object is already in the database by their first column
            obj = get_or_create_related(model, row.iloc[0])
            if obj:
                # Set the instance to an existing object
                instance = obj
            else:
                # Create a new instance of the model
                instance = model()

            # Iterate over each field in the row
            for field_name, value in row.items():
                # Check if value is nan
                if pd.isna(value):
                    continue
                # Check if the field is a normal field
                if field_name in field_dict and not field_dict[field_name].is_relation:
                    # Set the value of the field
                    setattr(instance, field_name, value)
                    # Save the instance
                    instance.save()

                # Check if the field is a ManyToMany field
                elif field_name in field_dict and field_dict[field_name].many_to_many:
                    # Split value by "," and strip them
                    values = [x.strip() for x in value.split(",")]
                    # Add each related object to the ManyToMany field
                    for value in values:
                        # Get the related object
                        related_obj = get_or_create_related(
                            field_dict[field_name].related_model, value
                        )

                        # Add the related object to the ManyToMany field
                        getattr(instance, field_name).add(related_obj)

                # Check if the field is a ForeignKey field
                elif field_name in field_dict and field_dict[field_name].related_model:
                    # Get the related object
                    related_obj = get_or_create_related(
                        field_dict[field_name].related_model, value
                    )

                    # Set the value of the field
                    setattr(instance, field_name, related_obj)
                    # Save the instance
                    instance.save()

            # Save the instance
            instance.save()

    return True, f"Successfully uploaded data to {table_name}"


def load_all_files():
    # Get all files from documents directory
    files = os.listdir("documents")

    # List of table names
    table_names = [
        "category",
        "language",
        "dialect",
        "speechcategory",
        "tag",
        "grammarnote",
        "word",
        "meaning",
        "synonym",
        "sentence",
        "text",
        "meaning_translation",
        "sentence_translation",
    ]

    # For name in table names, search for files containing that name, ignoring case, if not found, insert None
    file_dict = {}
    for name in table_names:
        if name in exceptions:
            # Handle exceptional files
            file_dict[name] = next(
                (f for f in files if (name.lower() + "s") in f.lower()), None
            )
        else:
            # Handle standard files
            file_dict[name] = next(
                (f for f in files if name.lower() in f.lower()), None
            )

    if any(file is None for file in file_dict.values()):
        # Raise an exception or handle it as needed
        missing_files = [name for name, file in file_dict.items() if file is None]
        return False, f"No files found for {missing_files} tables"

    # Load data from all files to db
    responses = []
    for i, name in enumerate(table_names):
        file = file_dict.get(name)
        if file is not None:
            file_path = os.path.join("documents", file)
            response = excel_to_db(file_path, name)
            responses.append((response, name))
        else:
            # Handle the case when the file is not found
            print(f"No file found for {name} table")

    # Check if everything alright
    if all(response[0] for response in responses):
        return True, "All data loaded successfully"
    else:
        # Get table names which failed to load
        failed_tables = [response[1] for response in responses if not response[0]]
        # Return False and error message
        return False, f"Error loading data for tables: {', '.join(failed_tables)}"
