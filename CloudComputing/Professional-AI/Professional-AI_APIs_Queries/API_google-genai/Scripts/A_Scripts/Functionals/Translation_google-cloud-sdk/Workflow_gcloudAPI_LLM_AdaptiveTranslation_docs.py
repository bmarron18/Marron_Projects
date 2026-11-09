#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 06 2025
@author: bmarron

source: https://cloud.google.com/translate/docs/advanced/adaptive-translation
"""

# %%

# NEEDS WORK!!

# %%

def adaptive_mt_translate():
  # Create a client
  client = translate.TranslationServiceClient()
  # Initialize the request
  request = translate.AdaptiveMtTranslateRequest(
    parent="projects/PROJECT_ID/locations/LOCATION",
    reference_sentence_config=[
      "reference_sentence_pair_lists": [
        "reference_sentence_pairs": {
          "source_sentence": 'REFERENCE_SOURCE_1_1'
          "target_sentence": 'REFERENCE_TARGET_1_1'
        },
        "reference_sentence_pairs": {
          "source_sentence": 'REFERENCE_SOURCE_1_2'
          "target_sentence": 'REFERENCE_TARGET_1_2'
        }
      ],
      "source_language_code": 'SOURCE_LANGUAGE'
      "target_language_code": 'TARGET_LANGUAGE'
    ],
    content=["SOURCE_TEXT"]
  )
  # Make the request
  response = client.adaptive_mt_translate(request)
  # Handle the response
  print(response)


# %%


from google.cloud import translate


def translate_text_with_model(
    text: str = "YOUR_TEXT_TO_TRANSLATE",
    project_id: str = "YOUR_PROJECT_ID",
    model_id: str = "YOUR_MODEL_ID",
) -> translate.TranslationServiceClient:
    """Translates a given text using Translation custom model."""

    client = translate.TranslationServiceClient()

    location = "us-central1"
    parent = f"projects/{project_id}/locations/{location}"
    model_path = f"{parent}/models/{model_id}"

    # Supported language codes: https://cloud.google.com/translate/docs/languages
    response = client.translate_text(
        request={
            "contents": [text],
            "target_language_code": "ja",
            "model": model_path,
            "source_language_code": "en",
            "parent": parent,
            "mime_type": "text/plain",  # mime types: text/plain, text/html
        }
    )
    # Display the translation for each input text provided
    for translation in response.translations:
        print(f"Translated text: {translation.translated_text}")

    return response



