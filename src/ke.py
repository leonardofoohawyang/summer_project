import os
import random
import nltk
from nltk.corpus import wordnet as wn
from googletrans import Translator
from google.cloud import language_v1


class Clause:
    def __init__(self):
        self.sobj = []
        self.pobj = [] 
        self.adp = 'None'  

    def insert_sobj(self, sobj):
        self.sobj.append(sobj)

    def insert_pobj(self, pobj):
        self.pobj.append(pobj)

    def insert_adp(self, adp):
      if adp in ['on', 'above']:
        self.adp = 'up'
      elif adp in ['under', 'below']:
        self.adp = 'down'
      elif adp in ['left']:
        self.adp = 'left'
      elif adp in ['right']:
        self.adp = 'right'
      elif adp in ['beside', 'by', 'to', 'with']:
        self.adp = random.choice(['left', 'right'])
      else:
        self.adp = adp

    def getRelation(self):
      return {'sobj': self.sobj, 'pobj': self.pobj, 'adp': self.adp}

def in_checklist(noun, english_class):
    if noun in english_class:
        return noun;
    else:
        for syn in wn.synsets(noun, pos=wn.NOUN):
            for l in syn.lemmas():
                if str(l) in english_class:
                    return l;
    return None;

def keyword_extraction(content_text):
  #Credentials for google Cloud NLP
  api_key_path = '../content/summer-factor-355116-e0708ce86ad5.json'
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = api_key_path

  #Making Dictionary
  fd = open('../content/English_Classes.txt', "r")
  data = fd.read()
  english_class = data.split("\n")
  fd.close()

  #Translation
  translator = Translator()
  translation = translator.translate(content_text, src='zh-tw', dest='en') #a set that includes src, dest, text, pronouciation, extra_data
  
  #Part of Speech Segmentation
  #Documentation Link: https://googleapis.dev/python/language/latest/index.html
  client = language_v1.LanguageServiceClient()
  language = "en"
  type_ = language_v1.Document.Type.PLAIN_TEXT

  tokenized_sentences=nltk.sent_tokenize(translation.text)
  
  ret = []
  clauses = []
  for i in range(len(tokenized_sentences)):
    clauses.append(Clause())

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
        exist = in_checklist(root, english_class)
        if exist != None:
          if label == "POBJ":
            clauses[i].insert_pobj(exist)
            pobj = word_location
          elif label == "NSUBJ":
            clauses[i].insert_sobj(exist)
            nsubj = word_location
          elif label == "DOBJ":
            if not clauses[i].sobj:
              clauses[i].insert_sobj(exist)
              nsubj = word_location
            else:
              clauses[i].insert_pobj(exist)
              pobj = word_location
          elif label == "CONJ" and dependency_edge.head_token_index == nsubj:
            clauses[i].insert_sobj(exist)
          elif label == "CONJ" and dependency_edge.head_token_index == pobj:
            clauses[i].insert_pobj(exist)
      elif tag == "ADP" and clauses[i].adp == 'None':
        clauses[i].insert_adp(token.lemma)
      elif token.lemma == "right" or token.lemma == "left":
        if label == "AMOD":
          clauses[i].insert_adp(token.lemma)
    
    ret.append(clauses[i].getRelation())

  return ret

# text = "桌子旁邊有隻貓。樹上有隻鳥。"
# ff = keyword_extraction(text)
# print(ff) 
