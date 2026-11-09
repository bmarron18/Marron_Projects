#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 06 2025
Modified: 25 Jan 2025
@author: bmarron

source: translate_v3beta1_translate_document.py
        https://codelabs.developers.google.com/codelabs/cloud-translation-python3#0
"""


# %%
# [BEGIN Workflow_gCloudShell_StandardNMT_GeneralTranslation_excerpts]

'''
Doing simple excerpt translations in GoogleCloudShell with the Standard NMT model
  Login to Google (marron,bruce,mx@gmail,com)
  Login to Google Cloud Console
  Activate Google Cloud Shell

  https://docs.cloud.google.com/shell/docs/using-cloud-shell
  Click Activate Cloud Shell at the top of the Google Cloud console.

Cloud Shell access
  https://console.cloud.google.com/welcome?project=my-project-uteca1
'''


Project name
    My Project-UTECA1
Project number
    735387290281
Project ID
    my-project-uteca1


'''
 Go to Cloud Hub for better visibility
This dashboard is no longer updated and will shut down in 2027. 
Cloud Hub offers a more comprehensive view across health, security, 
cost, optimization, and other data about your projects and applications. 

marron_bruce_mx@cloudshell:~ (my-project-uteca1)$ 
'''


# %%
'''
Doing simple excerpt translations in GoogleCloudShell with the Standard NMT model
  Authentication
  Account and Project Configuration
  Get the PROJECT_ID environment variable
  Call Google Cloud Translation API
'''

  # Follow prompts to obtain new authentication credentials (needed every time)
  # these are temporary ADC credentials ONLY if working in Cloud Shell!!
  # Credentials saved to file: [/tmp/tmp.mIXxB4oSdC/application_default_credentials.json]

#credentials check
$ gcloud auth list

   #check
$ gcloud config list project


 # Integrates text translation into your website or application
$ gcloud services enable translate.googleapis.com



$ export PROJECT_ID=$(gcloud config get-value core/project) &&
echo "PROJECT_ID: $PROJECT_ID"

 

 

# %%
'''
Doing simple excerpt translations in GoogleCloudShell with the Standard NMT model
  Python interpreter already installed
  google-cloud-translate SDK already installed
  Call ipython 
  Import Python modules and objects
  Define variables
'''

#$ pip install ipython google-cloud-translate

  #Call IPython into GoogleCloud Shell
$ ipython

  #  in Google Cloud Console (w/ IPython)
  
In [1]: 
import os
from os import environ
from google.cloud import translate

n [2]: 
PROJECT_ID = environ.get("PROJECT_ID", "")
assert PROJECT_ID
PARENT = f"projects/{PROJECT_ID}"

# %%

'''
Doing simple excerpt translations in GoogleCloudShell with the Standard NMT model
  Define "print_supported_languages Fxn" 
  [Uses the method, 'translate.TranslationServiceClient()']

'''

In [3]: 

def print_supported_languages(display_language_code: str):
    client = translate.TranslationServiceClient()

    response = client.get_supported_languages(
        parent=PARENT,
        display_language_code=display_language_code,
    )

    languages = response.languages
    print(f" Languages: {len(languages)} ".center(60, "-"))
    for language in languages:
        language_code = language.language_code
        display_name = language.display_name
        print(f"{language_code:10}{display_name}")


print_supported_languages("en")

# %%

'''
Doing simple excerpt translations in GoogleCloudShell with the Standard NMT model
  Define "translate_text Fxn" 
  [Uses the method, 'translate.TranslationServiceClient()']

'''

In [4]:

def translate_text(text: str, target_language_code: str) -> translate.Translation:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        target_language_code=target_language_code,
    )

    return response.translations[0]
    
# %%

  # Select language codes
tr        Turkish
de        German
es        Spanish
it        Italian
el        Greek
zh        Chinese (Simplified)
ja        Japanese
ko        Korean


In [5]:
  
text = "Hello World!"
target_languages = ["tr", "de", "es", "it", "el", "zh", "ja", "ko"]

print(f" {text} ".center(50, "-"))
for target_language in target_languages:
    translation = translate_text(text, target_language)
    source_language = translation.detected_language_code
    translated_text = translation.translated_text
    print(f"{source_language} → {target_language} : {translated_text}")


  # Output
------------------ Hello World! ------------------
en → tr : Selam Dünya!
en → de : Hallo Welt!
en → es : ¡Hola Mundo!
en → it : Ciao mondo!
en → el : Γεια σου Κόσμο!
en → zh : 你好世界！
en → ja : 「こんにちは世界」
en → ko : 안녕하세요!




# %%

  # Select language codes
es        Spanish
zh        Chinese (Simplified)
zh-TW     Chinese (Traditional)
yua       Yucatec Maya


In [6]:
  
text = "We explore the risk that self-reinforcing feedbacks could push the Earth System toward a planetary threshold that, if crossed, could prevent stabilization of the climate at intermediate temperature rises and cause continued warming on a Hothouse Earth pathway even as human emissions are reduced. Crossing the threshold would lead to a much higher global average temperature than any interglacial in the past 1.2 million years and to sea levels significantly higher than at any time in the Holocene. We examine the evidence that such a threshold might exist and where it might be. If the threshold is crossed, the resulting trajectory would likely cause serious disruptions to ecosystems, society, and economies. Collective human action is required to steer the Earth System away from a potential threshold and stabilize it in a habitable interglacial-like state. Such action entails stewardship of the entire Earth System—biosphere, climate, and societies—and could include decarbonization of the global economy, enhancement of biosphere carbon sinks, behavioral changes, technological innovations, new governance arrangements, and transformed social values."
target_languages = ["es", "zh", "zh-TW", "yua"]

print(f" {text} ")
for target_language in target_languages:
    translation = translate_text(text, target_language)
    source_language = translation.detected_language_code
    translated_text = translation.translated_text
    print(f"{source_language} → {target_language} : {translated_text}")
  
    

    # Output
We explore the risk that self-reinforcing feedbacks could push the Earth System toward a planetary threshold that, if crossed, could prevent stabilization of the climate at intermediate temperature rises and cause continued warming on a Hothouse Earth pathway even as human emissions are reduced. Crossing the threshold would lead to a much higher global average temperature than any interglacial in the past 1.2 million years and to sea levels significantly higher than at any time in the Holocene. We examine the evidence that such a threshold might exist and where it might be. If the threshold is crossed, the resulting trajectory would likely cause serious disruptions to ecosystems, society, and economies. Collective human action is required to steer the Earth System away from a potential threshold and stabilize it in a habitable interglacial-like state. Such action entails stewardship of the entire Earth System—biosphere, climate, and societies—and could include decarbonization of the global economy, enhancement of biosphere carbon sinks, behavioral changes, technological innovations, new governance arrangements, and transformed social values. 
en → es : Exploramos el riesgo de que las retroalimentaciones autorreforzadas puedan empujar al Sistema Tierra hacia un umbral planetario que, si se cruza, podría impedir la estabilización del clima en aumentos intermedios de temperatura y causar un calentamiento continuo en una trayectoria de Tierra de Invernadero incluso cuando se reduzcan las emisiones humanas. Cruzar el umbral conduciría a una temperatura media global mucho más alta que cualquier interglaciar en los últimos 1,2 millones de años y a niveles del mar significativamente más altos que en cualquier momento del Holoceno. Examinamos la evidencia de que tal umbral podría existir y dónde podría estar. Si se cruza el umbral, la trayectoria resultante probablemente causaría graves perturbaciones a los ecosistemas, la sociedad y las economías. Se requiere la acción humana colectiva para alejar al Sistema Tierra de un umbral potencial y estabilizarlo en un estado habitable similar al interglaciar. Tal acción implica la administración de todo el Sistema Tierra (biosfera, clima y sociedades) y podría incluir la descarbonización de la economía global, la mejora de los sumideros de carbono de la biosfera, cambios de comportamiento, innovaciones tecnológicas, nuevos acuerdos de gobernanza y valores sociales transformados.
en → zh : 我们探讨了这种风险，即自我强化反馈可能会将地球系统推向行星阈值，如果越过这个阈值，可能会阻止气候在中等温度上升时保持稳定，并导致即 使人类排放量减少，地球仍会继续变暖。越过这个阈值将导致全球平均气温比过去 120 万年中的任何一个间冰期都要高得多，海平面也将比全新世的任何时候都要高得多。我们研究了这种阈值可能存在的证据以及它可能在哪里。如果越过这个阈值，由此产生的轨迹可能会对生态系统、社会和经济造成严重破坏。需要人 类采取集体行动，使地球系统远离潜在的阈值，并将其稳定在类似间冰期的宜居状态。这种行动需要对整个地球系统（生物圈、气候和社会）进行管理，可能包 括全球经济脱碳、生物圈碳汇增强、行为变化、技术创新、新的治理安排和转变的社会价值观。
en → zh-TW : 我們探討了自我強化回饋可能將地球系統推向行星閾值的風險，一旦超過該閾值，可能會阻止中等溫度上升時氣候的穩定，並導致溫室地球路徑持續變暖，即使人類排放減少。跨越此閾值將導致全球平均氣溫比過去 120 萬年中的任何間冰期都要高得多，海平面也將比全新世任何時期都要高得多。我們檢查了這種閾值可能存在的證據以及它可能位於何處。一旦超越這個門檻，由此產生的軌跡可能會對生態系統、社會和經濟造成嚴重破壞。需要人類的集體行動來引 導地球系統遠離潛在的閾值並將其穩定在類似間冰期的宜居狀態。這種行動需要對整個地球系統（生物圈、氣候和社會）進行管理，並可能包括全球經濟脫碳、 生物圈碳匯增強、行為改變、技術創新、新的治理安排和社會價值觀轉變。
en → yua : K xak&#39;altik le riesgo u le retroalimentación autorefuerzo je&#39;el u páajtal u empujar le yaan lu&#39;um ti&#39; jump&#39;éel umbral planetario u, wa cruzado, je&#39;el Jech u estabilización le clima ti&#39; le aumentos temperatura intermedios yéetel causar calentamiento continuo ti&#39; jump&#39;éel beejil Hothouse Earth páajtal bey le emisiones humanas ku reducen. U k&#39;áatmáan le umbral je&#39;el u bisik jump&#39;éel temperatura promedio global jach asab ka&#39;anal u je&#39;el ba&#39;ax interglacial ti&#39; le ts&#39;ook 1.2 millones ja&#39;abo&#39;ob yéetel u niveles le k&#39;áak&#39;náabo&#39; significativamente asab ka&#39;anal u ti&#39; je&#39;el súutuko&#39; ti&#39; le Holoceno. K xak&#39;altik le ba&#39;ax ku ye&#39;esik je&#39;el u páajtal u yantal jump&#39;éel umbral beya&#39; yéetel tu&#39;ux je&#39;el u páajtal u yantal. Wa ku máan le umbralo&#39;, le trayectoria resultante je&#39;el u páajtal u causar graves interrupciones ti&#39; le ecosistemas, le kaaj yéetel le economías. K&#39;a&#39;abéet u múuch&#39; meyajo&#39;ob wíinik uti&#39;al u náachtal le lu&#39;uma&#39; ti&#39; jump&#39;éel umbral potencial yéetel u estabilizar ti&#39; jump&#39;éel noj habitable bey interglacial. Le meyajo&#39;oba&#39; ku taasik u kanáanta&#39;al tuláakal le lu&#39;uma&#39;—biosfera, clima yéetel kaajo&#39;ob—ka je&#39;el u páajtal u táakbesik u descarbonización le economía mundial, mejora ti&#39; le fregaderos carbono ti&#39; le biosfera, cambios comportamentales, innovaciones tecnológicas, túumben arreglos gobernabilidad, yéetel valores sociales transformados.



# %%

'''
Doing simple excerpt translations in GoogleCloudShell with the Standard NMT model
  Define "detect_language Fxn" 
  [Uses the method, 'translate.TranslationServiceClient()']

'''

def detect_language(text: str) -> translate.DetectedLanguage:
    client = translate.TranslationServiceClient()
    response = client.detect_language(parent=PARENT, content=text)

    return response.languages[0]
    


# %%

sentences = [
    "Selam Dünya!",
    "Hallo Welt!",
    "¡Hola Mundo!",
    "Ciao mondo!",
    "Γεια σου Κόσμο!",
    "你好世界！",
    "「こんにちは世界」",
    "안녕하세요!",
]
for sentence in sentences:
    language = detect_language(sentence)
    confidence = language.confidence
    language_code = language.language_code
    print(
        f"Confidence: {confidence:4.0%}",
        f"Language: {language_code:5}",
        sentence,
        sep=" | ",
    )
    



# %%

'''
Doing simple excerpt translations in GoogleCloudShell with the Standard NMT model
  Exit IPython
  Return to Google Cloud Shell
 '''


In [7]: 
  exit


