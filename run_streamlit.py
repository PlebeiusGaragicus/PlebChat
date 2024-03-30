if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    

    # TODO - move this into settings
    # import os
    # os.environ["LANGCHAIN_TRACING_V2"] = "true"
    # os.environ["LANGCHAIN_PROJECT"] = "PlebChat"

    # import logging
    # logging.getLogger("fsevents").setLevel(logging.WARNING)
    # logging.getLogger("PIL").setLevel(logging.WARNING)
    # logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    # logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    # logging.getLogger("httpx").setLevel(logging.WARNING)
    # logging.getLogger("langsmith.client").setLevel(logging.WARNING)
    # logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    # logging.getLogger("httpcore.connection").setLevel(logging.WARNING)


    from src.main import init_if_needed, main_page

    init_if_needed()
    main_page()
