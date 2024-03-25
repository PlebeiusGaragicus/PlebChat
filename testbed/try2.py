# import datetime

# import streamlit as st
# import extra_streamlit_components as stx

# st.write("# Cookie Manager")

# # @st.cache_resource
# @st.cache_resource(experimental_allow_widgets=True)
# def get_manager():
#     return stx.CookieManager()

# cookie_manager = get_manager()

# st.subheader("All Cookies:")
# cookies = cookie_manager.get_all()
# st.write(cookies)

# c1, c2, c3 = st.columns(3)

# with c1:
#     st.subheader("Get Cookie:")
#     cookie = st.text_input("Cookie", key="0")
#     clicked = st.button("Get")
#     if clicked:
#         value = cookie_manager.get(cookie=cookie)
#         st.write(value)
# with c2:
#     st.subheader("Set Cookie:")
#     cookie = st.text_input("Cookie", key="1")
#     val = st.text_input("Value")
#     if st.button("Add"):
#         cookie_manager.set(cookie, val) # Expires in a day by default
# with c3:
#     st.subheader("Delete Cookie:")
#     cookie = st.text_input("Cookie", key="2")
#     if st.button("Delete"):
#         cookie_manager.delete(cookie)


import streamlit as st
import extra_streamlit_components as stx
import uuid

st.write("# Cookie Manager")

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

st.subheader("All Cookies:")
cookies = cookie_manager.get_all()
st.write(cookies)

# Check if user_uuid is present
user_uuid_cookie = cookie_manager.get("user_uuid")
if user_uuid_cookie is None:
    # If not present, generate a new UUID and store it as a cookie
    new_uuid = uuid.uuid4()
    cookie_manager.set("user_uuid", str(new_uuid))

st.subheader("Your UUID:")
st.write(cookie_manager.get("user_uuid"))

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("Get Cookie:")
    cookie = st.text_input("Cookie", key="0")
    clicked = st.button("Get")
    if clicked:
        value = cookie_manager.get(cookie=cookie)
        st.write(value)

with c2:
    st.subheader("Set Cookie:")
    cookie = st.text_input("Cookie", key="1")
    val = st.text_input("Value")
    if st.button("Add"):
        cookie_manager.set(cookie, val) # Expires in a day by default

with c3:
    st.subheader("Delete Cookie:")
    cookie = st.text_input("Cookie", key="2")
    if st.button("Delete"):
        cookie_manager.delete(cookie)

increment = st.button("Increment")
if increment:
    count = cookie_manager.get("count")
    if count is None:
        count = 0
    else:
        count = int(count)
    count += 1
    cookie_manager.set("count", count)
    st.write(f"Count: {count}")


get_all = st.button("Get All")
if get_all:
    # cookies = cookie_manager.get_all()
    # st.write(cookies)
    cookies = cookie_manager.cookies
    st.write(cookies)


delete_all = st.button("Delete All")
if delete_all:
    # for c in cookie_manager.cookies:
    # st.write(cookie_manager.cookies.keys())
    while len(cookie_manager.cookies) > 0:
        c = list(cookie_manager.cookies.keys())[0]
        cookie_manager.delete(c, key=str(uuid.uuid4()))
        st.write("deleted: ", c)

    st.write("All cookies deleted")
