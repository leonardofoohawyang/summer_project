import os
from google.cloud import language_v1
from google.cloud.language_v1 import enums
from google.cloud import language
from google.cloud.language import types
from googletrans import Translator
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figureimport
import nltk
#nltk.download('popular') #Uncomment if you have never downloaded
from nltk.corpus import wordnet as wn

#Credentials for Google Cloud
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/content/summer-factor-355486-e0708lo86ad5.json"

fd = open("/content/English_Classes.txt", "r")
data = fd.read()
english_class = data.split("\n")
fd.close()

def keyword_extraction(content_text):
    nouns = []
    adp = []

    #Translation
    translator = Translator()
    translation = translator.translate(content_text, src='zh-tw', dest='en') #a set that includes src, dest, text, pronouciation, extra_data
    
    #Part of Speech Segmentation
    #Documentation Link: https://googleapis.dev/python/language/latest/index.html
    client = language_v1.LanguageServiceClient()
    language = "en"
    type_ = enums.Document.Type.PLAIN_TEXT
    document = {"content": translation.text, "type": type_, "language": language}
    encoding_type = enums.EncodingType.UTF8
    response = client.analyze_syntax(document=document, encoding_type='UTF8')

    for token in response.tokens:
      part_of_speech = token.part_of_speech #includes Tag, Voice, Tense
      tag = enums.PartOfSpeech.Tag(part_of_speech.tag).name
      if tag == "NOUN":
        root = token.lemma
        if root in english_class:
          nouns.append(root)
        else: #synonyms
          for syn in wn.synsets(root, pos=wn.NOUN):
            for l in syn.lemmas():
                if l in english_class:
                  nouns.append(l)
      elif tag == "ADP":
        adp.append(token.lemma)
    return nouns, adp
    

text = "桌子上有一隻貓."
n, pp = keyword_extraction(text)
print(n)
print(pp)