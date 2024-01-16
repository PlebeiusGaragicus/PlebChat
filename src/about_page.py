import os

import streamlit as st

from src.common import (
    center_text
)

ASSET_FOLDER = os.path.join(os.path.dirname(__file__), "assets")

PAGE_TEXT_1 = """# About

See the [GitHub repo](https://github.com/PlebeiusGaragicus/PlebChat) for more information...
"""

def about_page():
    col = st.columns((1, 1))
    with col[0]:
        st.markdown()

        st.write(PAGE_TEXT_1)

    with col[1]:
        st.image(
            image=os.path.join(ASSET_FOLDER, "assistant2sm.png"),
            caption="your own friendly assistant!",
        )

    st.write("---")

# st.image("https://picsum.photos/200")
# st.image("https://picsum.photos/200/300")