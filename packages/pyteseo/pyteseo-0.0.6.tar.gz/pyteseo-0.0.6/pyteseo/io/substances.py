""" Manage offline substance data stored in xlsx-files @ pyteseo/data/substances
"""
import pandas as pd
import pyteseo
from pathlib import Path


SUBSTANCES_OFFLINE_PATH = Path(Path(pyteseo.__file__).parent, "data/substances")


def get_offline_substance(substance_type: str, substance_name: str) -> pd.DataFrame:
    """retrieve a substance in a pandas Dataframe

    Args:
        substance_type (str): ["oil", "hns"]
        substance_name (str): name of the substance required

    Raises:
        FileNotFoundError: if database (oil.xlsx and hns.xlsx) are not located at SUBSTANCES_OFFLINE_PATH env variable
        ValueError: if substance name is not in the database

    Returns:
        pd.DataFrame: _description_
    """
    substance_type = substance_type.lower()
    substance_name = substance_name.lower()

    xlsx_path = Path(SUBSTANCES_OFFLINE_PATH, substance_type + ".xlsx")
    if not xlsx_path.exists():
        raise FileNotFoundError(f"{substance_type} not in path ({xlsx_path})")

    df = pd.read_excel(xlsx_path)
    if substance_name in df.name.to_list():
        return df.loc[df.name == substance_name]
    else:
        raise ValueError(
            f"Susbtance name required ({substance_name}) not in xlsx ({str(xlsx_path)})"
        )


def get_offline_substance_names(substance_type: str) -> list:
    """get all substance names availables for a specific substance type

    Args:
        substance_type (str): ["oil", "hns"]

    Raises:
        FileNotFoundError: if database (oil.xlsx or hns.xlsx) are not located at SUBSTANCES_OFFLINE_PATH env variable

    Returns:
        list: names of the susbstances
    """
    substance_type = substance_type.lower()
    xlsx_path = Path(SUBSTANCES_OFFLINE_PATH, substance_type + ".xlsx")
    if not xlsx_path.exists():
        raise FileNotFoundError(f"{substance_type} not in path ({xlsx_path})")

    df = pd.read_excel(xlsx_path)
    return df.name.to_list()
