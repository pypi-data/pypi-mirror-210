"""Python package developed to simplify and facilitate the setup and processing of TESEO simulations (https://ihcantabria.com/en/specialized-software/teseo/)
"""
from pathlib import Path
from dotenv import load_dotenv

__version__ = "0.0.6"


if Path(".env").exists():
    load_dotenv(Path(".env"))
else:
    print("\nWARNING - .env file has not been loaded!")
