import os
import streamlit as st

# https://platform.openai.com/docs/guides/images/introduction?context=node
# https://stackoverflow.com/questions/76747912/error-in-displaying-image-using-streamlit-st-image

from openai import APIConnectionError


def make_api_call(prompt):
    return client.images.generate(
            # model="dall-e-2",
            model="dall-e-3",
            n=1,
            # response_format="url",
            response_format="b64_json",
            prompt=prompt,
            size="1024x1024",
            # style=st.session_state["style"],
            quality="standard",
        )

# STYLE = [NOT_GIVEN, 'vivid', 'natural']



if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()


    st.write("# Dalle 3 🎨")
    st.header("", divider="rainbow")


    API_KEY = os.getenv("OPENAI_API_KEY", None)


    from openai import OpenAI
    client = OpenAI(api_key=API_KEY)

    with st.container(border=True):
        st.write("## settings")
        st.caption("non yet")
        # st.radio("Style", STYLE, index=0, key="style")

    prompt = None
    if prompt := st.chat_input("Ask a question."):
        st.write(prompt)

        with st.spinner("🧠 Thinking..."):
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    responce = make_api_call(prompt) # TODO - https://platform.openai.com/docs/guides/error-codes/python-library-error-types
                    break  # Exit the loop if the API call is successful
                except APIConnectionError as e:
                    retry_count += 1
                    st.write(f"API connection error. Retrying... {retry_count}/{max_retries}")
                    st.error(e)
                    st.exception(e)
                    if retry_count == max_retries:
                        st.stop()  # Stop execution if maximum retries reached
                except Exception as e:
                    st.error(e)
                    st.exception(e)
                    st.stop()

        # st.image(responce.data[0].url)
        # st.image(responce.data[0].b64_json)
        # with open("foo.png","wb") as f:
        #     f.write(decodestring(responce.data[0].b64_json))
                    
        import base64
        with open("foo.png", "wb") as fh:
            fh.write(base64.b64decode(responce.data[0].b64_json))

        st.image('./foo.png', caption=responce.data[0].revised_prompt)
        st.write(responce.data[0].revised_prompt)
        # st.write(responce)
        # print(responce)
