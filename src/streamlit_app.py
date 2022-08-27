"""
Run code:
streamlit run video.py
"""

import os
import random
import streamlit as st
from qd import QuickDraw
from canvas import Canvas
from PIL import Image
from ke_v2 import keyword_extraction
from googletrans import Translator

# Example video code
# https://github.com/streamlit/streamlit/blob/develop/examples/video.py

st.set_page_config(
    page_title="Demo",
    page_icon="🎈",
)

st.write("""
## 🎬 演示
### 📌 請輸入任意短句
""")


with st.form(key="form1"):

    pad1, col, pad2 = st.columns([1, 100, 2])

    with col:
        doc = st.text_area(
            "",
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


def addBorder(old_im):
    w, h = old_im.size
    new_size = (w+4, h+4)
    new_im = Image.new("RGB", new_size)
    box = tuple((n - o) // 2 for n, o in zip(new_size, (w, h)))
    new_im.paste(old_im, box)
    return new_im

# press the bottom
if not submit_button:
    st.stop()
else:
    # Translation
    translator = Translator()
    translation = translator.translate(doc, src='zh-tw', dest='en') #a set that includes src, dest, text, pronouciation, extra_data
    st.subheader('翻譯:')
    st.write(translation.text)
    # get the keywords
    clauses = keyword_extraction(doc)
    print(f'clauses: {clauses}')
    st.subheader('關鍵字和介詞:')
    st.write(clauses)

    objs = []
    for clause in clauses:
        for obj in clause['sobj']:
            objs.append(obj)
        for obj in clause['pobj']:
            objs.append(obj)
    
    st.subheader('物件:')
    st.write(objs)

    canvas = Canvas()
    canvas.init(rate=0.15)

    for obj in objs:
        canvas.addObj(obj, random.randint(0, 99))

    canvas.addEdge(clauses)

    # canvas.config()
    im = canvas.draw()
    
    with st.container():
        st.subheader('輸出:')
        st.image(addBorder(im).resize((1920, 1080)))



 
