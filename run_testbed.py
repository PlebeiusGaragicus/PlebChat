if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    import streamlit as st


    # TODO - move this into settings
    import os
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "PlebChat testbed"
    # os.environ["LANGCHAIN_API_KEY"] = os.get

    if not os.getenv("LANGCHAIN_API_KEY", False):
        st.error("LANGCHAIN_API_KEY NOT SET")
    else:
        st.success("LANGCHAIN_API_KEY set ;)")

    import logging
    logging.getLogger("fsevents").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("langsmith.client").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)

    st.markdown("# Testbed")
    from testbed.test import main
    main()
