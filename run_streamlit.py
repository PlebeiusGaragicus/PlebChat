if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    import os
    # print(f"{os.environ['TAVILY_API_KEY']=}")

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    # print(f"{os.environ['LANGCHAIN_API_KEY']=}")


    from src.interface.login import login_router_page

    from src import logger
    logger.setup_logging()
    import logging
    logging.getLogger("fsevents").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("langsmith.client").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)


    # import pdb; pdb.set_trace()
    # import asyncio
    # asyncio.run(login_router_page())
    login_router_page()
