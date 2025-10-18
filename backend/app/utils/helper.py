import os
import pandas as pd

FILENAME = "online_retail_II.csv"

def get_dataset_path() -> str:
    """
    Get the absolute path to the dataset file.
    :return:
    str: The absolute path to the dataset file.
    """

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_dir, "dataset", FILENAME)


def load_dataset() -> pd.DataFrame:
    """
    Load the dataset from the CSV file.
    :return:
    pd.DataFrame: The loaded dataset.
    """

    dataset_path = get_dataset_path()
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at {dataset_path}")

    df = pd.read_csv(dataset_path, encoding="unicode_escape")
    return df
