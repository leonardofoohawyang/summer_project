from googletrans import Translator
import os
from google.cloud import language_v1

import nltk
#nltk.download('popular') #Uncomment if you have never downloaded
from nltk.corpus import wordnet as wn

#Credentials for google Cloud NLP
api_key_path = r"C:\Users\siaje\OneDrive\Desktop\iAgent\summer-factor-355116-e0708ce86ad5.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = api_key_path

#Making Dictionary
fd = open(r"C:\Users\siaje\OneDrive\Desktop\iAgent\English_Classes.txt", "r")
data = fd.read()
english_class = data.split("\n")
fd.close()

class Clause:
    def __init__(self):
        self.sobj = []
        self.pobj = [] 
        self.adp = -1  #1: up, 2: down, 3: left, 4: right]

    def insert_sobj(self, sobj):
        self.sobj.append(sobj)

    def insert_pobj(self, pobj):
        self.pobj.append(pobj)

    def insert_adp(self, adp):
        if adp == "on" or adp == "above":
          self.adp = 1
        elif adp == "under" or adp == "below":
          self.adp = 2
        elif adp == "left":
          self.adp = 3
        elif adp == "right":
          self.adp = 4
        else:
          self.adp = adp

    def printing(self):
        print(u"sobj: {}".format(self.sobj))
        print(u"pobj: {}".format(self.pobj))
        print(u"adp: {}".format(self.adp))

def in_checklist(noun):
    if noun in english_class:
        return noun;
    else:
        for syn in wn.synsets(noun, pos=wn.NOUN):
            for l in syn.lemmas():
                if str(l) in english_class:
                    return l;
    return -1;

def keyword_extraction(content_text):
    ret = []

    #Translation
    translator = Translator()
    translation = translator.translate(content_text, src='zh-tw', dest='en') #a set that includes src, dest, text, pronouciation, extra_data
    print(translation.text)
    
    #Part of Speech Segmentation
    #Documentation Link: https://googleapis.dev/python/language/latest/index.html
    client = language_v1.LanguageServiceClient()
    language = "en"
    type_ = language_v1.Document.Type.PLAIN_TEXT

    tokenized_sentences=nltk.sent_tokenize(translation.text)
    for i in range(len(tokenized_sentences)):
      ret.append(Clause())
      document = {"content": tokenized_sentences[i], "type_": type_, "language": language}
      #encoding_type = enums.EncodingType.UTF8
      response = client.analyze_syntax(document=document, encoding_type='UTF8')

      nsubj = -1
      pobj = -1
      word_location = -1

      for token in response.tokens:
        #print(token)
        word_location = word_location + 1
        part_of_speech = token.part_of_speech #includes Tag, Voice, Tense
        tag = language_v1.PartOfSpeech.Tag(part_of_speech.tag).name
        dependency_edge = token.dependency_edge
        label = language_v1.DependencyEdge.Label(dependency_edge.label).name
        if tag == "NOUN":
          root = token.lemma
          exist = in_checklist(root)
          if exist != -1:
            if label == "POBJ":
              ret[i].insert_pobj(exist)
              pobj = word_location
            elif label == "NSUBJ":
              ret[i].insert_sobj(exist)
              nsubj = word_location
            elif label == "DOBJ":
              if not ret[i].sobj:
                ret[i].insert_sobj(exist)
                nsubj = word_location
              else:
                ret[i].insert_pobj(exist)
                pobj = word_location
            elif label == "CONJ" and dependency_edge.head_token_index == nsubj:
              ret[i].insert_sobj(exist)
            elif label == "CONJ" and dependency_edge.head_token_index == pobj:
              ret[i].insert_pobj(exist)
        elif tag == "ADP" and ret[i].adp == -1:
          ret[i].insert_adp(token.lemma)
        elif token.lemma == "right" or token.lemma == "left":
          if label == "AMOD":
            ret[i].insert_adp(token.lemma)    

    return ret

text = "我看到桌子右邊有蘋果, 花, 狗, 和貓咪。"
ff = keyword_extraction(text)
for i in ff:
  i.printing()
  print()
