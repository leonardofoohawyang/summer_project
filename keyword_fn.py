import nltk
import jieba
import jieba.analyse
import jieba.posseg
import base64
import json
import numpy as np

fd = open("/content/Chinese_Classes.txt", "r")
data = fd.read()
chinese_class = data.split("\n")
fd.close()

fd = open("/content/English_Classes.txt", "r")
data = fd.read()
english_class = data.split("\n")
fd.close()

chi_eng = dict(zip(chinese_class, english_class))

posseg = jieba.posseg.POSTokenizer(tokenizer=None)
def ProperNounExtractor(text):
    sentences = jieba.posseg.POSTokenizer(tokenizer=None)
    words = posseg.cut(text)
    for word, tag in words:
        #print(word, tag)
        if tag == 'n':
            #return word
            index = "full_simplified_" + chi_eng.get(nouns) + ".ndjson"
            return index

text_1 = "右邊看到一輛車."
text_2 = "我走進屋."
text_3 = "我愛吃蘋果."
text_4 = "我有一隻貓"
nouns = ProperNounExtractor(text_2)
