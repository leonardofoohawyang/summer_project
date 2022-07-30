"""
Run code:
streamlit run video.py
"""

import os
import random
import streamlit as st
from qd import QuickDraw

import jieba
import jieba.analyse
import jieba.posseg
import json

# Example video code
# https://github.com/streamlit/streamlit/blob/develop/examples/video.py

st.set_page_config(
    page_title="Demo",
    page_icon="🎈",
)

st.write("""
# 🎬 Demo
## 📌 Paste document
""")


with st.form(key="form1"):

    pad1, col, pad2 = st.columns([1, 100, 2])

    with col:
        doc = st.text_area(
            "請輸入中文句子",
            height=300,
        )

        MAX_WORDS = 500
        import re
        res = len(re.findall(r"\w+", doc))
        if res > MAX_WORDS:
            st.warning(
                "⚠️ Your text contains "
                + str(res)
                + " words."
                + " Only the first 500 words will be reviewed. Stay tuned as increased allowance is coming! 😊"
            )

            doc = doc[:MAX_WORDS]

        submit_button = st.form_submit_button(label="✨ 提取關鍵字 ✨")

def nltk_sample(text: str):
    print(nltk_sample)
    chinese_class = open("../content/Chinese_Classes.txt", "r").read().split("\n")
    english_class = open("../content/English_Classes.txt", "r").read().split("\n")
    chi_eng = dict(zip(chinese_class, english_class))

    posseg = jieba.posseg.POSTokenizer(tokenizer=None)
    sentences = jieba.posseg.POSTokenizer(tokenizer=None)
    words = posseg.cut(text)

    for word, tag in words:
        print(word, tag)
        if tag == 'n':
            return chi_eng.get(word)

    return None

if not submit_button:
    st.stop()
else:
    # get the keywords
    keyword = nltk_sample(doc)

    if keyword == None:
        st.subheader("No keywords found!")
    else:
        st.subheader(f"Extracted keyword: {keyword}")
        st.header(f"Generate {keyword} animation")
        qd = QuickDraw('video.mp4')
        qd.create_spec_animation(keyword)
        video_file = open('video.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes)


 
