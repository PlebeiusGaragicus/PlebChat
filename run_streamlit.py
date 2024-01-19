if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    from src.login import login_router_page

    from src import logger
    logger.setup_logging()
    # import logging
    # logging.getLogger("fsevents").setLevel(logging.WARNING)
    # logging.getLogger("matplotlib").setLevel(logging.WARNING)

    # import pdb; pdb.set_trace()
    login_router_page()
