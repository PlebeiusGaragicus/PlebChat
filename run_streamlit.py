if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    from src.main import home_page

    from src import logger
    logger.setup_logging()
    # import logging
    # logging.getLogger("fsevents").setLevel(logging.WARNING)
    # logging.getLogger("matplotlib").setLevel(logging.WARNING)

    # import pdb; pdb.set_trace()
    home_page()
