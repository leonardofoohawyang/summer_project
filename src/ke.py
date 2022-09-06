import os
import random
from xmlrpc.client import MAXINT
from word2number import w2n
import nltk
from nltk.corpus import wordnet as wn
from googletrans import Translator
from google.cloud import language_v1

class Noun:
    def __init__(self, lemma, number):
        #print(lemma, number)    
        self.name = None
        self.lemma = lemma
        if number == -2:
          self.number = "plural"
        elif number == -1:
          self.number = 1
        else:
          self.number = w2n.word_to_num(number)

    def give_name(self, name):
      self.name = name

    def printing(self):
      print(self.name, self.lemma, self.number)    

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

    def printing(self):
      print("sobj:")    
      if(len(self.sobj) > 0):    
        for i in self.sobj:
          i.printing()
      print("pobj:")
      if(len(self.pobj) > 0):
        for i in self.pobj:
          i.printing()
      print("adp:")
      print(self.adp)   

def in_checklist(noun):
    fd = open('../content/English_Classes.txt', "r")
    data = fd.read()
    english_class = data.split("\n")
    fd.close()   

    if noun in english_class:
        return noun;
    else:
        for syn in wn.synsets(noun, pos=wn.NOUN):
            for l in syn.lemmas():
                if str(l) in english_class:
                    return l;
    return None;

def positional_relation(response):
  ret = Clause()    

  nsubj = -1
  pobj = -1
  word_location = -1
  num = MAXINT

  for token in response.tokens:
    word_location = word_location + 1
    part_of_speech = token.part_of_speech #includes Tag, Voice, Tense
    tag = language_v1.PartOfSpeech.Tag(part_of_speech.tag).name
    dependency_edge = token.dependency_edge
    label = language_v1.DependencyEdge.Label(dependency_edge.label).name
    if tag == "NOUN":
      exist = in_checklist(token.lemma)
      if num == MAXINT:
        num = language_v1.PartOfSpeech.Number(part_of_speech.number) * (-1)
      if exist != None:
        if label == "POBJ":
          ret.insert_pobj(Noun(exist, num))
          pobj = word_location
        elif label == "NSUBJ":
          ret.insert_sobj(Noun(exist, num))
          nsubj = word_location
        elif label == "DOBJ":
          if not ret.sobj:
            ret.insert_sobj(Noun(exist, num))
            nsubj = word_location
          else:
            ret.insert_pobj(exist)
            pobj = word_location
        elif label == "CONJ" and dependency_edge.head_token_index == nsubj:
          ret.insert_sobj(Noun(exist, num))
        elif label == "CONJ" and dependency_edge.head_token_index == pobj:
          ret.insert_pobj(Noun(exist, num)) 
      num = MAXINT  
    elif tag == "ADP" and ret.adp == 'None':
      ret.insert_adp(token.lemma)
    elif token.lemma == "right" or token.lemma == "left":
      if label == "AMOD":
        ret.insert_adp(token.lemma)
    elif tag == "NUM":
      num = token.lemma
  return ret

def check_name(response):
  noun = None
  name = None
  cnt = 0
  for token in response.tokens:
    part_of_speech = token.part_of_speech
    tag = language_v1.PartOfSpeech.Tag(part_of_speech.tag).name
    if tag == "NOUN":
      exist = in_checklist(token.lemma)
      if exist != None:
        noun = exist
      else:
        name = token.lemma
      cnt = cnt + 1
  if noun != None and name != None and cnt == 2:
    sobj = Noun(noun, -1)
    sobj.give_name(name)
    ret = Clause()
    ret.insert_sobj(sobj)
    return ret
  else:
    return None    

def keyword_extraction(content_text):
  #Credentials for google Cloud NLP
  api_key_path = '../content/summer-factor-355116-e0708ce86ad5.json'
  os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = api_key_path

  #Translation: a set that includes src, dest, text, pronouciation, extra_data
  translation = (Translator().translate(content_text, src='zh-tw', dest='en')).text
  #print(translation)
  
  #Part of Speech Segmentation
  #Documentation Link: https://googleapis.dev/python/language/latest/index.html
  client = language_v1.LanguageServiceClient()
  language = "en"
  type_ = language_v1.Document.Type.PLAIN_TEXT

  tokenized_sentences=nltk.sent_tokenize(translation)
  
  clauses = []
  for i in range(len(tokenized_sentences)):
    document = {"content": tokenized_sentences[i], "type_": type_, "language": language}
    response = client.analyze_syntax(document=document, encoding_type='UTF8')
    reference = check_name(response)
    if reference != None: 
      clauses.append(reference)
    else:  
      clauses.append(positional_relation(response))
  return clauses

#text = "我的貓咪叫Tom."
#ff = keyword_extraction(text)
#for i in ff:
#  i.printing()
