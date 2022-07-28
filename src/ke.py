from sklearn.feature_extraction.text import CountVectorizer
from keybert import KeyBERT
import jieba

import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, sent_tokenize

import jieba.analyse
import jieba.posseg

def keybert_sample():
    def tokenize_zh(text):
        words = jieba.lcut(text)
        return words

    vectorizer = CountVectorizer(tokenizer=tokenize_zh)

    doc = "我想吃蘋果"

    kw_model = KeyBERT()

    keywords = kw_model.extract_keywords(doc, vectorizer=vectorizer)

    print(keywords)

    """
    keywords = [('我', 0.7183), ('蘋果', 0.5982), ('想', 0.5003), ('吃', 0.5003)]
    """

    return None

def nltk_sample():
    nltk.download('all', download_dir='./nltk_data')
    def ProperNounExtractor(text):
        print('PROPER NOUNS EXTRACTED :')
        
        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            words = nltk.word_tokenize(sentence)
            words = [word for word in words if word not in set(stopwords.words('english'))]
            tagged = nltk.pos_tag(words)
            for (word, tag) in tagged:
                print(word, tag)
                #if tag == 'NN': # If the word is a proper noun
                    #print(word)

    text =  "Rohan is a wonderful player. He was born in India. He is a fan of the movie Wolverine. He has a dog named Bruno."

    keywords = ProperNounExtractor(text)

    """
    PROPER NOUNS EXTRACTED :
    Rohan NNP
    wonderful JJ
    player NN
    . .
    He PRP
    born VBZ
    India NNP
    . .
    He PRP
    fan VBZ
    movie NN
    Wolverine NNP
    . .
    He PRP
    dog VBZ
    named VBN
    Bruno NNP
    . .
    """

    print(keywords)

    return None

def nltk_jieba_sample():
    nltk.download('popular', download_dir='./nltk_data')
    text = "我前面有一棵樹. 樹周圍有很多花. 天上有星星. 右邊看到一輛車子."
    posseg = jieba.posseg.POSTokenizer(tokenizer=None)
    words = posseg.cut(text)
    for word, flag in words:
        print('%s %s' % (word, flag))

    """
    我 r
    前面 f
    有 v
    一棵 m
    樹 n
    . m
    x
    樹周圍 n
    有 v
    很多 m
    花 n
    . m
    x
    天上 s
    有 v
    星星 nz
    . x
    x
    右邊 f
    看到 v
    一輛 m
    車子 n
    . m
    """
    return None

if __name__ == "__main__":
    keybert_sample()
    # nltk_sample()
    # nltk_jieba_sample()