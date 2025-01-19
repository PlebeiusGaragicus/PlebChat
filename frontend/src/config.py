import pathlib

########################################################################
STATIC_PATH = pathlib.Path(__file__).parent.parent / "static"

# This is shown in the UI to the user
APP_NAME = "PlebChat"

# This is used to identify the approprate graph in the Langserver
GRAPH_NAME = "plebchat"

# Settings for this pipeline
HARD_DISABLE_TITLE_GENERATION = True

# Langserver endpoint
LANGSERVE_ENDPOINT = "http://backend"
PORT = 8000
# PIPELINE_ENDPOINT = "/chat"
# PIPELINE_ENDPOINT = "phi"
########################################################################
