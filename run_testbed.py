if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    import os
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "PlebChat testbed"
    if not os.getenv("LANGCHAIN_API_KEY", False):
        st.error("LANGCHAIN_API_KEY NOT SET")
        st.stop()

    from testing.test_bed import main_page
    main_page()
