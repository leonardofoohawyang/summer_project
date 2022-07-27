"""
Run code:
streamlit run video.py
"""

import os
import random
import streamlit as st
from qd import QuickDraw
import time

# Example video code
# https://github.com/streamlit/streamlit/blob/develop/examples/video.py

def main():

    st.write("""
    # Demo
    """)

    st.write('## What is this?')
    qd = QuickDraw('video.mp4')

    files = os.listdir('../simplified')
    random.shuffle(files)

    idx = random.randint(0, 2)

    obj = files[idx].split(".ndjson")[0]

    print(f"Now draw {obj}!!")

    qd.create_spec_animation(obj)

    video_file = open('video.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)

    option = st.selectbox(
        'What would you like to be selected for?',
        (files[0].split(".ndjson")[0], files[1].split(".ndjson")[0], files[2].split(".ndjson")[0]))
    
    if option == obj:
        st.write('You selected:', option)
        st.write('Correct')
    else:
        st.write('You selected:', option)
        st.write('Wrong')

    time.sleep(3)

    return None

if __name__ == "__main__":
    main()